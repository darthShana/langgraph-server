custom_stuff_template = """
Given the provided conversation between an AI and a human looking for a suitable vehicle, 
as well as a list vehicle descriptions. Filter the list and return matching vehicle descriptions
return a summary of each listing based on the criteria the human has mentioned, always include the source of each listing
Conversation:
{conversation}
Vehicle Descriptions:
{vehicle_descriptions} 
"""

returning_visitor_greeting_template = """
Given the provided conversation which was the previous conversation between an AI and a human looking for a vehicle.
Generate a greeting for the human who has now returned to our site. Summarize the previous conversation in the greeting
Include the last vehicle listings if present, always include the source of each listing.
Previous conversation:
{previous_conversation} 
"""

custom_comparison_template = """
Please provide a JSON response in the following format to the question provided, mark the json as ```json:
{format_instructions}

Given the provided list of vehicle details, compare them to highlight their differences
Vehicles:
{vehicles}
"""

clarifying_question_prefix = """
You are helpful but sassy car sales person
Given a chat history between an AI and a human looking for a vehicle (Which maybe empty).
Suggest a clarifying question the AI can ask the human to better understand the humans needs
The AI can find vehicles by filtering based on the following metadata:
metadata:
{{metadata}}
and from a encoded vector value of a query. So suggest a question that will help populate the filter or the query.
Limit multichoice questions to 4 choices, Use non-technical language in your response.
"""

clarifying_question_example_template = """
Here is an example:
<example>
chat_history:
{chat_history}
result:
{result}
"""

clarifying_question_examples = [
    {
        "chat_history": """[
            {"himan": "Hi, im a new visitor"}
        ]""",
        "result": """{
            "question": "Hi there!, So what kind of car are you looking for?",
            "question_type": "multi_choice",
            "options": [
                "I have a budget of 10-15k that I can work with",
                "Id like to look at specific makes or models",
                "there are some specific features the car needs to have",
                "I want a certain kind of vehicle like hatch, SUV, waggon"
            ]
        }"""

    },
    {
        "chat_history": """[
            {"human": "I have a budget of 10-15k that I can work with"}
        ]""",
        "result": """{
            "question": "Great, tell me more about this budget?",
            "question_type": "multi_choice",
            "options": [
                "10-15k",
                "15-20k",
                "20-25k",
                "25-30k",
            ]
        }"""
    },
    {
        "chat_history": """[
            {human: "Im expecting a baby, whats a good car for me?"}
        ]""",
        "result": """{
            "question": "Congratulations! let me suggest some features to look for. 5 seats or more, child seat anchor, room for a stroller. Shall i look for something like this?",
            "question_type": "true_false",
        }"""
    },
    {
        "chat_history": """[
            {"human": "im looking for something recent with good fuel economy"},
            {"ai": "Okey.. those are great things to have in a car lets try get a bit more specific, Would yo prefer a hybrid?"},
            {"ai:" "yes"}
        ]""",
        "result": """{
            "question": "Cool lets talk about your new ride being 'recent', it there a year you would like to stay above?",
            "question_type": "freeform",
        }"""
    }

]