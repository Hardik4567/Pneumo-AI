import os
from jose import JWTError, jwt
from fastapi import HTTPException
from app.core.logger import app_logger
from datetime import datetime, timedelta, timezone

def create_authToken(user, expires_delta=None):
    print("SECRET_KEY =", os.getenv("SECRET_KEY"))
    print("ALGORITHM =", os.getenv("ALGORITHM"))
    print("EXPIRE =", os.getenv("authToken_EXPIRE_MINUTES"))

    to_encode = {
        "id": user.id,
        "fullName": user.full_name,
        "emailId": user.email_id,
        "mobileNumber": user.mobile_number,
    }

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=int(os.getenv("authToken_EXPIRE_MINUTES")))
    )

    to_encode["exp"] = expire

    token = jwt.encode(
        to_encode,
        os.getenv("SECRET_KEY"),
        algorithm=os.getenv("ALGORITHM")
    )

    print("TOKEN =", token)

    return token


def decode_authToken(token: str):
    try:
        # Decode the token without verifying the signature to inspect the payload
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        if "user_id" in payload:
            payload["id"] = payload.pop("user_id")
        return payload
    except jwt.ExpiredSignatureError:
        app_logger.error("Token has expired.")
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as e:
        app_logger.error(f"JWTError decoding token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
