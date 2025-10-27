"""
Custom JSON encoder to handle datetime serialization
Workaround for Agno's session summary datetime serialization bug
"""
import json
from datetime import datetime, date
from uuid import UUID


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime, date, and UUID objects"""
    
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


def patch_json_encoder():
    """
    Monkey patch json module to use DateTimeEncoder by default
    Call this at the start of your application
    """
    original_dumps = json.dumps
    
    def patched_dumps(*args, **kwargs):
        if 'cls' not in kwargs:
            kwargs['cls'] = DateTimeEncoder
        return original_dumps(*args, **kwargs)
    
    json.dumps = patched_dumps

