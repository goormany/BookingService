import hashlib
import json

from fastapi import Request, Response

def request_key_builder(
    func,
    namespace: str = "",
    *args,
    request: Request = None,
    response: Response = None,
    **kwargs
) -> str:
    sorted_params = sorted(request.query_params.items())
    
    content = f"{namespace}:{request.method.lower()}:{request.url.path}:{json.dumps(sorted_params, sort_keys=True)}"
    
    hash_key = hashlib.md5(content.encode()).hexdigest()[:12]
    
    readable = f"{namespace}:{request.method.lower()}:{request.url.path}"
    
    return ":".join([readable, hash_key])