import traceback

from fastapi import HTTPException, Request
from firebase_admin import auth

from firebase_auth import verify_user_token, verify_admin_token, app_user, app_admin


def get_current_user(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth_header.split(" ")[1]
    try:
        user = verify_user_token(token)
        get_user = auth.get_user(user['uid'], app=app_user)

        return get_user
    except Exception as _:
        error_msg = traceback.format_exc()
        print(error_msg)
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_admin(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth_header.split(" ")[1]
    try:
        user = verify_admin_token(token)
        get_user = auth.get_user(user['uid'], app=app_admin)
        return get_user
    except Exception as _:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_or_admin(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth_header.split(" ")[1]

    try:
        user = verify_user_token(token)
        get_user = auth.get_user(user["uid"], app=app_user)

        return get_user

    except HTTPException:
        try:
            admin = verify_admin_token(token)
            get_admin = auth.get_user(admin["uid"], app=app_admin)
            return get_admin

        except HTTPException:
            raise HTTPException(status_code=401, detail="invalid token")

