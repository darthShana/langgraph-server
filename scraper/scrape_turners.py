from json import JSONDecodeError
from typing import Sequence

import requests
import re

from bs4 import BeautifulSoup
from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrock
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_core.documents import Document
from langchain_core.utils.json import parse_json_markdown
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import ValidationError
from tinydb import TinyDB, Query

from scraper.vector_db import VectorDB
from scraper.vehicle_listing import VehicleListing, VehicleListingMetadata

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class TurnersScraper:
    chat = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)

    parser = JsonOutputParser(pydantic_object=VehicleListing)
    vector_store = VectorDB()
    db = TinyDB('db/db.json')

    @staticmethod
    def filter_content(docs_transformed):
        for d in docs_transformed:
            if "Start: Main Content Area" in d.page_content:
                d.page_content = d.page_content.split('Start: Main Content Area')[1]
            if "End: Main Content Area" in d.page_content:
                d.page_content = d.page_content.split('End: Main Content Area')[0]

    def run_crawler(self):
        max_count = 40

        vgm_urls = [
            f'https://www.turners.co.nz/Cars/Used-Cars-for-Sale/?sortorder=7&pagesize={max_count}&pageno=1&issearchsimilar=true&types=convertible',
            f'https://www.turners.co.nz/Cars/Used-Cars-for-Sale/?sortorder=7&pagesize={max_count}&pageno=1&issearchsimilar=true&types=wagon',
            f'https://www.turners.co.nz/Cars/Used-Cars-for-Sale/?sortorder=7&pagesize={max_count}&pageno=1&issearchsimilar=true&types=utility',
            f'https://www.turners.co.nz/Cars/Used-Cars-for-Sale/?sortorder=7&pagesize={max_count}&pageno=1&issearchsimilar=true&types=hatchback',
            f'https://www.turners.co.nz/Cars/Used-Cars-for-Sale/?sortorder=7&pagesize={max_count}&pageno=1&issearchsimilar=true&types=van',
            f"https://www.turners.co.nz/Cars/Used-Cars-for-Sale/?sortorder=7&pagesize={max_count}&pageno=1&issearchsimilar=true&types=sedan",
            f"https://www.turners.co.nz/Cars/Used-Cars-for-Sale/?sortorder=7&pagesize={max_count}&pageno=1&issearchsimilar=true&types=suv",
            f"https://www.turners.co.nz/Cars/Used-Cars-for-Sale/?sortorder=7&pagesize={max_count}&pageno=1&issearchsimilar=true&types=coupe",
            # f'https://www.turners.co.nz/Trucks-Machinery/Used-Trucks-and-Machinery-for-Sale/?sortorder=0&pagesize={max_count}&pageno=1&industry=agriculture',
            # f'https://www.turners.co.nz/Trucks-Machinery/Used-Trucks-and-Machinery-for-Sale/?sortorder=0&pagesize={max_count}&pageno=1&industry=construction%2C%20forestry%20%26%20earthmoving',
            # f'https://www.turners.co.nz/Trucks-Machinery/Used-Trucks-and-Machinery-for-Sale/?sortorder=0&pagesize={max_count}&pageno=1&industry=industrial',
            # f'https://www.turners.co.nz/Trucks-Machinery/Used-Trucks-and-Machinery-for-Sale/?sortorder=0&pagesize={max_count}&pageno=1&industry=lifting%20%26%20material%20handling',
            # f"https://www.turners.co.nz/Trucks-Machinery/Used-Trucks-and-Machinery-for-Sale/?sortorder=0&pagesize={max_count}&pageno=1&industry=trailers",
            # f"https://www.turners.co.nz/Trucks-Machinery/Used-Trucks-and-Machinery-for-Sale/?sortorder=0&pagesize={max_count}&pageno=1&industry=trucks"
        ]

        urls = []

        for vgm_url in vgm_urls:
            html_text = requests.get(vgm_url).text
            soup = BeautifulSoup(html_text, 'html5lib')
            attrs = {
                'class': "green"
            }
            for listing in soup.find_all('a', attrs=attrs):
                urls.append("https://www.turners.co.nz/"+listing['href'])

        stale = [doc for doc in self.db.all() if doc['source'] not in urls]
        q = Query()
        for doc in stale:
            log.info(f"removing stale listing:{doc['source']}")
            self.db.remove(q.source == doc['source'])
            self.vector_store.delete(doc)

        urls = [url for url in urls if len(self.db.search(q.source == url)) == 0]

        docs_transformed = TurnersScraper.extract_data(urls)
        log.info(f"loaded {len(docs_transformed)} documents")

        for doc in docs_transformed:
            try:
                listing = self.append_data_from_images(doc)
                self.vector_store.save(listing, doc)
                self.db.insert({'source': doc.metadata['source'], 'image': doc.metadata['image'], 'content': doc.page_content})

            except (ValidationError, JSONDecodeError) as e:
                print(e)

    @staticmethod
    def extract_data(urls: list[str]) -> Sequence[Document]:
        loader = AsyncHtmlLoader(urls, default_parser="html5lib")
        data = loader.load()
        html2text = BeautifulSoupTransformer()
        docs_transformed = html2text.transform_documents(data)
        TurnersScraper.filter_content(docs_transformed)

        return docs_transformed

    def append_data_from_images(self, doc: Document) -> VehicleListing:
        log.info(doc.metadata)
        template = """Please provide a JSON response in the following format to the question provided, mark the json as ```json:
            {format_instructions}
            ---
            Question:
            Given the following text listing of a vehicle for sale, split all content into sections. ensure 
            all content is put into at least one section, do not leave anything out:
            ---
            Content to split:
            {page_content}
            """

        prompt = PromptTemplate(
            template=template,
            input_variables=["page_content"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        chain = prompt | self.chat
        output_from_claude = chain.invoke({"page_content": doc.page_content})
        markdown = parse_json_markdown(output_from_claude.content)
        listing = VehicleListing.parse_obj(markdown)

        template = """Please provide a JSON response in the following format to the question provided, mark the json as ```json:
            {format_instructions}
            ---
            Question:
            Given the following text listing of a vehicle for sale, What additional details can be found in
            the included images that may be of interest to buyers? Only include details NOT already in the text listing.
            Split the results into sections:
            ---
            Text Listing:
            {page_content}
            ---
            Images:
            {images}
            """
        prompt = PromptTemplate(
            template=template,
            input_variables=["page_content", "images"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        chain = prompt | self.chat

        html_text = requests.get(doc.metadata['source']).text
        soup = BeautifulSoup(html_text, 'html5lib')

        attrs = {
            'class': "lazyOwl"
        }

        image_urls = []
        for image in soup.find_all('img', attrs=attrs):
            pattern = r"Photo '[1,2,4,5]'"
            match = re.match(pattern, image['alt'])
            if match:
                log.info(image['data-src'])
                image_urls.append(image['data-src'])

        output_from_claude = chain.invoke({
            "page_content": listing.json(),
            "images": image_urls
        })
        parsed_json = parse_json_markdown(output_from_claude.content)

        log.info("image enrichment complete")
        log.info(parsed_json)

        if 'manufacturer_details' in parsed_json and isinstance(parsed_json['manufacturer_details'], str):
            listing.manufacturer_details += parsed_json['manufacturer_details']
        if 'feature_details' in parsed_json and isinstance(parsed_json['feature_details'], str):
            listing.feature_details += parsed_json['feature_details']
        if 'condition_details' in parsed_json and isinstance(parsed_json['condition_details'], str):
            listing.condition_details += parsed_json['condition_details']
        if 'possible_uses' in parsed_json and isinstance(parsed_json['possible_uses'], str):
            listing.possible_uses += parsed_json['possible_uses']
        if 'other' in parsed_json and isinstance(parsed_json['other'], str):
            listing.other += parsed_json['other']
        if len(image_urls) > 0:
            listing.metadata.image = image_urls[0]

        return listing


if __name__ == "__main__":
    print("hello turners langchain")
    crawler = TurnersScraper()
    crawler.run_crawler()
