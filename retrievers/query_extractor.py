from langchain_anthropic import ChatAnthropic
import logging

from langchain_core.prompts import PromptTemplate, FewShotPromptWithTemplates
from langchain_core.utils.json import parse_json_markdown

from retrievers.templates import query_extraction_example_template, query_extraction_prefix, query_extraction_examples

log = logging.getLogger(__name__)


class QueryExtractor:
    chat = ChatAnthropic(model="claude-3-5-sonnet-20240620")
    metadata_field_info = {
        "content": "Vehicle Listings",
        "attributes": [
            {
                "name": "make",
                "description": "the manufacture who made this item",
                "type": "string"
            },
            {
                "name": "model",
                "description": "the model name of this item",
                "type": "string"
            },
            {
                "name": "year",
                "description": "the year the item was made",
                "type": "integer"
            },
            {
                "name": "fuel",
                "description": "the fuel type this vehicle uses. One of ['Petrol', 'Diesel', 'Hybrid']",
                "type": "integer"
            },
            {
                "name": "seats",
                "description": "the number of seats to carray passengers in this vehicle",
                "type": "integer"
            },
            {
                "name": "odometer",
                "description": "the odometer reading showing the milage of this vehicle",
                "type": "integer"
            },
            {
                "name": "price",
                "description": "the price this vehicle is on sale for",
                "type": "number",
            },
            {
                "name": "location",
                "description": "the location this vehicle is at. One of ['Whangarei', 'Westgate', 'North Shore', 'Otahuhu', 'Penrose', 'Botany', 'Manukau', 'Hamilton', 'Tauranga', 'New Plymouth', 'Napier', 'Rotorua', 'Palmerston North', 'Wellington', 'Nelson', 'Christchurch', 'Timaru', 'Dunedin', 'Invercargill']",
                "type": "string"
            },
            {
                "name": "vehicle_type",
                "description": "the type of vehicle this is. One of  ['Wagon', 'Sedan' ,'Hatchback', 'SUV', 'Utility', 'Sports Car', 'Van', 'Tractor', 'Excavator', 'Generator', 'FEL', 'Roller']",
                "type": "string"
            },
            {
                "name": "colour",
                "description": "the color of the vehicle",
                "type": "string"
            },
            {
                "name": "drive",
                "description": "the drive wheels on this vehicle One of ['Two Wheel Drive', 'Four Wheel Drive']",
                "type": "string"
            }
        ]
    }

    def __init__(self):
        pass

    @staticmethod
    def escape_f_string(text):
        return text.replace('{', '{{').replace('}', '}}')

    @staticmethod
    def escape_examples(examples):
        return [{k: QueryExtractor.escape_f_string(v) for k, v in example.items()} for example in examples]

    EXAMPLE_PROMPT2 = PromptTemplate(
        input_variables=["conversation", "result"], template=query_extraction_example_template
    )

    def extract_query(self, conversation: list):
        prefix = PromptTemplate(
            input_variables=["field_metadata"], template=query_extraction_prefix
        )
        suffix = PromptTemplate(
            input_variables=["conversation"],
            template="""
                    So given 
                    conversation: 
                    {{conversation}}. 
                    Extract the result in json format marking the json as ```json:""",
        )

        prompt = FewShotPromptWithTemplates(
            suffix=suffix,
            prefix=prefix,
            input_variables=["field_metadata", "conversation"],
            examples=QueryExtractor.escape_examples(query_extraction_examples),
            example_prompt=self.EXAMPLE_PROMPT2,
            example_separator="\n",
        )

        chain = prompt | self.chat
        output = chain.invoke({"field_metadata": self.metadata_field_info, "conversation": conversation})
        return parse_json_markdown(output.content)
