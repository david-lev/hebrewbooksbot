import json


def js_to_py(data: str, to: str = 'list') -> dict | list:
    """Convert JavaScript to Python"""
    if to == 'list':
        return json.loads(data[data.index('['):data.index(']') + 1])
    elif to == 'dict':
        return json.loads(data[data.index('{'):data.rindex('}') + 1])
    else:
        raise ValueError('Invalid type')
