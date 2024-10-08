from datetime import datetime
from typing import TypedDict, Annotated, Sequence

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition
from langgraph.graph import StateGraph, add_messages
import logging
import sqlite3

from model.user_profile import UserProfile
from tools.fetch_user_information import fetch_user_information_tool
from langchain_aws import ChatBedrock
from tools.turners_geography import turners_geography_tool
from tools.vehicle_comparison import vehicle_comparison_tool
from tools.vehicle_search import vehicle_search_tool
from tools.watch_list import add_to_watch_list_tool, get_watch_list_tool
from utils import create_tool_node_with_fallback, has_results_to_show

log = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_info: UserProfile


class VirtualTina:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: AgentState, config: RunnableConfig):
        while True:
            user = state.get("user_info", None)
            state = {**state, "user_info": user}
            result = self.runnable.invoke(state)

            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get('text')
            ):
                messages = state['messages'] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


# Define the config
class GraphConfig(TypedDict):
    model_name: str
    user_id: str


llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)


assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful but sassy assistant working for Turners Automotive, a used vehicle marketplace for cars, trucks and machinery in New Zealand."
            "Respond to user queries in a concise manner to reduce the amount they have to read"
            "Use the provided tools to assist the user's job to be done, only if necessary."
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            " If a search comes up empty, expand your search before giving up."
            "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

tools = [
    fetch_user_information_tool,
    turners_geography_tool,
    vehicle_search_tool,
    vehicle_comparison_tool,
    add_to_watch_list_tool,
    get_watch_list_tool,
]


def user_info(state: AgentState):
    return {"user_info": fetch_user_information_tool.invoke({})}


# Define a new graph
workflow = StateGraph(AgentState, config_schema=GraphConfig)
assistant_runnable = assistant_prompt | llm.bind_tools(tools)
workflow.set_entry_point("fetch_user_info")
workflow.add_node("fetch_user_info", user_info)
workflow.add_node("assistant", VirtualTina(assistant_runnable))
workflow.add_node("tools", create_tool_node_with_fallback(tools))

workflow.add_edge("fetch_user_info", "assistant")
workflow.add_conditional_edges(
    "assistant",
    tools_condition,
)
workflow.add_edge("tools","assistant")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
conn = sqlite3.connect(":memory:")
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
