class TopicAssignmentTemplate():
    SYSTEM_PROMPT = """\
You are a precise classifier. Analyze the text and assign it to exactly one of these topics by ID:
{topic_list}

CRITICAL: Output ONLY the number ID (e.g. '0', '5', '12'). Do not write the name.
"""

    USER_PROMPT = """{text_to_evaluate}"""