custom_stuff_template = """
Please provide a JSON response in the following format to the question provided, mark the json as ```json:
{format_instructions}

Given the provided conversation between an AI and a human looking for a suitable vehicle, 
as well as a list vehicle descriptions. Filter the list and return up to 3 matching vehicle descriptions
return a summary of each listing, always include the source of each listing
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