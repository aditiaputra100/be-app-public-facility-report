from firebase_admin import auth, credentials, initialize_app

cred_user = credentials.Certificate("path/to/serviceAccountKeyUser.json")
app_user = initialize_app(cred_user, name="user_app")

cred_admin = credentials.Certificate("path/to/serviceAccountKeyAdmin.json")
app_admin = initialize_app(cred_admin, name="admin_app")

def verify_user_token(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token, app=app_user)
        return decoded_token
    except Exception as _:
        raise Exception("Invalid Firebase token")

def verify_admin_token(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token, app=app_admin)
        return decoded_token
    except Exception as _:
        raise Exception("Invalid Firebase token")