from datetime import datetime
from typing import TypedDict, Annotated, Sequence, Literal

from langchain_core.messages import BaseMessage, ToolMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, END, add_messages
import logging

from model.user_profile import UserProfile
from tools.fetch_user_information import fetch_user_information_tool
from tools.turners_geography import turners_geography_tool
from tools.vehicle_search import vehicle_search_tool
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
            user_id = config.get("user_id", None)
            state = {**state, "user_info": user_id}
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


def display_results(state: AgentState):
    if messages := state.get("messages", []):
        ai_message = messages[-1]
        if isinstance(ai_message, ToolMessage) and ai_message.name == "vehicle_search":
            return {"messages": [ai_message.content]}


def route_tool_results(state: AgentState) -> Literal["assistant", "display_results"]:
    if messages := state.get("messages", []):
        ai_message = messages[-1]
        if isinstance(ai_message, ToolMessage) and ai_message.name == "vehicle_search":
            if has_results_to_show(ai_message.content):
                return "display_results"

    return "assistant"


# Define the config
class GraphConfig(TypedDict):
    model_name: str
    user_id: str


# Define the two nodes we will cycle between
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)

assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful but sassy assistant working for Car Place, a used vehicle marketplace for cars, trucks and machinery in New Zealand."
            "Respond to user queries in a concise manner to reduce the amount they have to read"
            "Use the provided tools to search for vehicles and other information to assist the user's queries, only if necessary."
            "Only use the `turners_geography_tool` if a specific location is mentioned in the conversation."
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
    TavilySearchResults(max_results=1)
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
workflow.add_node("display_results", display_results)

workflow.add_edge("fetch_user_info", "assistant")
workflow.add_conditional_edges(
    "assistant",
    tools_condition,
)
workflow.add_conditional_edges(
    "tools",
    route_tool_results,
    {
        "assistant": "assistant",
        "display_results": "display_results"
    }
)
workflow.add_edge("display_results", "__end__")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
memory = SqliteSaver.from_conn_string(":memory:")
graph = workflow.compile(checkpointer=memory)
