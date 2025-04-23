def escape_f_string(text):
    return text.replace('{', '{{').replace('}', '}}')


def escape_examples(examples):
    return [{k: escape_f_string(v) for k, v in example.items()} for example in examples]
