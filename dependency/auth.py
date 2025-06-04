from fastapi import HTTPException, Request
from firebase_auth import verify_token

def get_current_user(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth_header.split(" ")[1]
    try:
        user = verify_token(token)
        return user
    except Exception as _:
        raise HTTPException(status_code=401, detail="Invalid token")