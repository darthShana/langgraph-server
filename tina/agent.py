from datetime import datetime
from typing import TypedDict, Annotated, Sequence

from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph, add_messages
import logging
import sqlite3

from tina.model.user_profile import UserProfile
from tina.tools.ask_human import AskHuman
from tina.tools.book_a_test_drive import book_a_test_drive_tool
from tina.tools.clarifing_questions import clarifying_question_tool
from tina.tools.fetch_user_information import fetch_user_information_tool
from tina.tools.request_callback import request_callback_tool
from tina.tools.structured_search import structured_search_options_tool, structured_search_tool
from tina.tools.turners_geography import turners_geography_tool
from tina.tools.vehicle_comparison import vehicle_comparison_tool
from tina.tools.vehicle_search import vehicle_search_tool
from tina.tools.watch_list import add_to_watch_list_tool, get_watch_list_tool
from utils import create_tool_node_with_fallback, has_results_to_show

log = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    structured_search: dict


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


llm = init_chat_model("gpt-4o", model_provider="openai")


assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful but sassy assistant working for Turners Automotive, a used vehicle retailer for cars with branches throughout New Zealand. "
            "Always use the ClarifyingQuestion tool to initiate a conversation with a new visitor to tease out what kind of vehicle the user is looking for, once some criteria have been collected use the vehicle_search tool to find vehicles matching their criteria."
            "After using the vehicle_search tool summarise your response to ONLY include make, model year of the vehicles found. "
            "Guide them to book a test drive, or create search notification, add to watch list or request a callback"
            "Do not ask the user for their location, use the turners_geography tool which can work this out. "
            "Instead of saying no suitable cars found, use the request_callback tool to to get a human sales rep to call the user back"
            "Use the ask_human tool when a tool requires input or confirmation from the user do NOT guess, ask for all the required information at once. "
            "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# We define a fake node to ask the human
def ask_human(state: AgentState):
    pass

tools = [
    turners_geography_tool,
    clarifying_question_tool,
    vehicle_search_tool,
    vehicle_comparison_tool,
    add_to_watch_list_tool,
    get_watch_list_tool,
    book_a_test_drive_tool,
    request_callback_tool,
    structured_search_options_tool,
    structured_search_tool,
]

def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # If there is no function call, then we finish
    if not last_message.tool_calls:
        return "end"
    # If tool call is asking Human, we return that node
    # You could also add logic here to let some system know that there's something that requires Human input
    # For example, send a slack message, etc
    elif last_message.tool_calls[0]["name"] == "AskHuman":
        return "ask_human"
    # Otherwise if there is, we continue
    else:
        return "continue"


def user_info(state: AgentState):
    return {"user_info": fetch_user_information_tool.invoke({})}


# Define a new graph
workflow = StateGraph(AgentState, config_schema=GraphConfig)
assistant_runnable = assistant_prompt | llm.bind_tools(tools + [AskHuman])
workflow.set_entry_point("assistant")
workflow.add_node("assistant", VirtualTina(assistant_runnable))
workflow.add_node("tools", create_tool_node_with_fallback(tools))
workflow.add_node("ask_human", ask_human)

workflow.add_conditional_edges(
    "assistant",
    should_continue,
    {
        "continue": "tools",
        "ask_human": "ask_human",
        "end": END,
    },
)
workflow.add_edge("tools","assistant")
workflow.add_edge("ask_human", "assistant")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
conn = sqlite3.connect(":memory:")
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory, interrupt_before=["ask_human"])
