query_extraction_prefix = """
Your goal is to structure the user's query to match the request schema provided below.

The query string should contain only text that is expected to match the contents of documents. Any conditions in the filter should not be mentioned in the query as well.

A logical condition statement is composed of one or more comparison and logical operation statements.

A comparison statement takes the form: `comp(attr, val)`:
- `comp` ($eq | $ne | $gt | $gte | $lt | $lte | $contain | $like | $in | $nin): comparator
- `attr` (string):  name of attribute to apply the comparison to
- `val` (string): is the comparison value

A logical operation statement takes the form `op(statement1, statement2, ...)`:
- `op` ($and | $or | $not): logical operator
- `statement1`, `statement2`, ... (comparison statements or logical operation statements): one or more statements to apply the operation to

Make sure that you only use the comparators and logical operators listed above and no others.
Make sure that filters only refer to attributes that exist in the data source.
Make sure that filters only use the attributed names with its function names if there are functions applied on them.
Make sure that filters only use format `YYYY-MM-DD` when handling date data typed values.
Make sure that filters take into account the descriptions of attributes and only make comparisons that are feasible given the type of data being stored.
Make sure that filters are only used as needed. If there are no filters that should be applied return "NO_FILTER" for the filter value.

Date source:
{{field_metadata}}
"""

query_extraction_example_template = """
Here is an example:
<example>
conversation:
{conversation}
result:
{result}
"""

query_extraction_examples = [
    {
        "conversation": """
        [
            "system: You are a helpful but sassy sales assistant, working for Turners Automotive Group,",
            "ai: Hi! im Tina, a virtual sales assistant. How can i help you today?",
            "human: im looking for a fun car",
            "ai: Awesome, you have come to the right place, could you tell me more about the kind od car your looking for?",
            "human: a toyota",
            "ai: Toyata is a very good brand, Could you tell me what your budget is? and where you are located?",
            "human: something under 15k"
        ]""",
        "result": """
        {
            "query": "fun car", 
            "filter": {
                "$and": [
                    {"make": {"$eq": "Toyota"}},
                    {"price": {"$lt": 15000}}
                ]
            }
        }"""
    },
    {
        "conversation": """
        [
            "system: You are a helpful but sassy sales assistant, working for Turners Automotive Group,",
            "ai: Hi! im Tina, a virtual sales assistant. How can i help you today?",
            "human: im i want a new car",
            "ai: Awesome, you have come to the right place, could you tell me more about the kind od car your looking for?",
            "human: somehting recent with good fuel economy",
            "ai: Recent and good fuel economy are great thing to have in a car, maybe you can tell me about your budget and location to help me narrow things down",
            "human: im in the bay of plenty. i'd like a hatchback or a sedan, with bluetooth and a reversing camera",
            "ai: hmm i cant seem to find anything that matched this criteria, how about increasing your budget?",
            "human: okey 20k",
            "ai: the relevant Turners locations to search are are Tauranga, Hamilton",
        ]""",
        "result": """
        {   
            "query": "good fuel economy, bluetooth and a reversing camera",
            "filter": {
                "$and": [
                    {"year": {"$gt": 2015}},
                    {"vehicle_type": {"$in": ["Hatchback", "Sedan"]}},
                    {"location": {"$in": ["Tauranga", "Hamilton"]}},
                    {"price": {"$lt": 20000}}
                ]
            }
        }"""
    }
]
