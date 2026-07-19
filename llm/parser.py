import json

def parse_json_content(content: str) -> dict:
    return json.loads(content)
