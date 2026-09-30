"""
Authentication and user account service.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, Header
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.errors import AuthenticationException, AppException
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, UserOut, TokenResponse


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, data: UserRegister) -> TokenResponse:
        # Check if email exists
        res = await db.execute(select(User).filter(User.email == data.email))
        if res.scalars().first():
            raise AppException(code="EMAIL_ALREADY_EXISTS", message="User with this email already exists", status_code=409)

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            role="USER"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        token = create_access_token(subject=user.id, role=user.role)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserOut.model_validate(user)
        )

    @staticmethod
    async def login(db: AsyncSession, data: UserLogin) -> TokenResponse:
        res = await db.execute(select(User).filter(User.email == data.email))
        user = res.scalars().first()
        if not user or not verify_password(data.password, user.password_hash):
            raise AuthenticationException("Invalid email or password")

        token = create_access_token(subject=user.id, role=user.role)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserOut.model_validate(user)
        )

    @staticmethod
    async def get_current_user(
        authorization: Optional[str] = Header(None),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """Dependency for authenticating user via Bearer token."""
        if not authorization or not authorization.startswith("Bearer "):
            # Fallback for local demo/testing if not logged in: auto-provision demo user
            res = await db.execute(select(User).filter(User.email == "demo@antigravity.ai"))
            demo_user = res.scalars().first()
            if not demo_user:
                demo_user = User(
                    email="demo@antigravity.ai",
                    password_hash=hash_password("DemoPassword123!"),
                    role="USER"
                )
                db.add(demo_user)
                await db.commit()
                await db.refresh(demo_user)
            return demo_user

        token = authorization.replace("Bearer ", "").strip()
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload")

        res = await db.execute(select(User).filter(User.id == user_id))
        user = res.scalars().first()
        if not user:
            raise AuthenticationException("User not found")
        return user
