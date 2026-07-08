import os
import random
import string
import smtplib
from typing import Optional
from datetime import datetime
from sqlalchemy import delete
from sqlalchemy.future import select
from email.mime.text import MIMEText
from app.core.config import settings
from app.core.security import hash_password as get_password_hash, verify_password
from app.models.user_token import UserToken
from app.models.user_master import UserMaster
from email.mime.multipart import MIMEMultipart
from sqlalchemy.ext.asyncio import AsyncSession
from jinja2 import Environment, FileSystemLoader
from fastapi import HTTPException, status
from app.db.database import get_db
from app.schemas.user_master import UserMasterAddEdit


# =========================
# Helpers
# =========================

def generate_random_password(length: int = 8) -> str:
    """Generates a random password containing letters, numbers, and symbols."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


def generate_otp(length: int = 6) -> str:
    """Generate a random numeric OTP of a given length."""
    return "".join(random.choice(string.digits) for _ in range(length))


# =========================
# User Queries
# =========================

async def get_user_by_email(session: AsyncSession, email: str, is_deleted: int = 0) -> Optional[UserMaster]:
    result = await session.execute(
        select(UserMaster).where(
            UserMaster.email_id == email,
            UserMaster.is_deleted == is_deleted
        )
    )
    return result.scalars().first()


async def get_user_by_id(session: AsyncSession, id: int, is_deleted: int = 0) -> Optional[UserMaster]:
    result = await session.execute(
        select(UserMaster).where(
            UserMaster.id == id,
            UserMaster.is_deleted == is_deleted
        )
    )
    return result.scalars().first()


async def get_all_active_users(session: AsyncSession) -> list[UserMaster]:
    """Get all active (not deleted) users."""
    result = await session.execute(
        select(UserMaster).where(UserMaster.is_deleted == 0)
    )
    return result.scalars().all()


# =========================
# Add / Edit User
# =========================

async def add_edit_user(db: AsyncSession, user_data: UserMasterAddEdit) -> UserMaster:
    """Add a new user or edit an existing user."""
    if user_data.id == 0:
        existing_active_user = await get_user_by_email(db, user_data.email_id, is_deleted=0)
        if existing_active_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists and is active"
            )

        generated_password = generate_random_password(8)

        new_user = UserMaster(
            email_id=user_data.email_id,
            full_name=user_data.full_name,
            username=user_data.username,
            mobile_number=user_data.mobile_number,
            password_hash=get_password_hash(generated_password),
            role_id=user_data.role_id,
        )
        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            await send_password_email(user_data.email_id, generated_password)
        except Exception as e:
            await db.rollback()
            raise e

        return new_user

    else:
        existing_user = await get_user_by_id(db, user_data.id, is_deleted=0)
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user_data.full_name is not None:
            existing_user.full_name = user_data.full_name
        if user_data.email_id is not None:
            existing_user.email_id = user_data.email_id
        if user_data.mobile_number is not None:
            existing_user.mobile_number = user_data.mobile_number
        if user_data.role_id is not None:
            existing_user.role_id = user_data.role_id
        if user_data.password:
            existing_user.password_hash = get_password_hash(user_data.password)

        existing_user.updated_by = 1
        existing_user.updated_on = datetime.now()
        await db.commit()
        await db.refresh(existing_user)
        return existing_user


# =========================
# Delete User
# =========================

async def delete_user_service(db: AsyncSession, user_id: int, deleted_by: int):
    """Soft delete a user by setting is_deleted flag."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_deleted = 1
    user.deleted_by = deleted_by
    user.deleted_on = datetime.utcnow()

    await db.commit()
    await db.refresh(user)
    return user


# =========================
# OTP
# =========================

async def add_otp_to_verification_table(session: AsyncSession, user_id: int, otp: str) -> UserToken:
    """Store an OTP in user_token for later verification."""
    new_otp_verification = UserToken(user_id=user_id, otp=otp)
    session.add(new_otp_verification)
    await session.commit()
    await session.refresh(new_otp_verification)
    return new_otp_verification


async def delete_expired_otps(db: AsyncSession):
    """Delete expired OTP rows from user_token."""
    await db.execute(
        delete(UserToken).where(UserToken.exp_date <= datetime.now())
    )
    await db.commit()


# =========================
# Email
# =========================

async def send_otp_email(email_id: str, otp: str):
    """Send OTP to user's email."""
    template_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'static', 'templates'
    )
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('otp_template.html')
    html_content = template.render(otp=otp)

    message = MIMEMultipart()
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = email_id
    message["Subject"] = "Your OTP for Verification"
    message.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, email_id, message.as_string())
    except Exception as e:
        print(f"Failed to send OTP email: {e}")


async def send_password_email(email_id: str, password: str):
    """Send auto-generated password to user's email."""
    template_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'static', 'templates'
    )
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('password_template.html')
    html_content = template.render(password=password)

    message = MIMEMultipart()
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = email_id
    message["Subject"] = "Your New Account Password"
    message.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, email_id, message.as_string())
    except Exception as e:
        print(f"Failed to send password email: {e}")