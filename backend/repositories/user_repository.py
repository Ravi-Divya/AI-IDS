from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import User, Role, RefreshToken
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User:
        query = select(User).where(
            User.email == email,
            User.is_deleted == False,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User:
        query = select(User).where(
            User.username == username,
            User.is_deleted == False,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_roles(self, user_id: str) -> User:
        query = select(User).where(
            User.id == user_id,
            User.is_deleted == False,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def assign_role(self, user_id: str, role_id: str) -> bool:
        user = await self.get(user_id)
        role_query = select(Role).where(Role.id == role_id)
        role_result = await self.session.execute(role_query)
        role = role_result.scalar_one_or_none()
        if not user or not role:
            return False
        if role not in user.roles:
            user.roles.append(role)
            await self.session.flush()
        return True

    async def revoke_role(self, user_id: str, role_id: str) -> bool:
        user = await self.get(user_id)
        if not user:
            return False
        user.roles = [r for r in user.roles if r.id != role_id]
        await self.session.flush()
        return True


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)

    async def get_by_name(self, name: str) -> Role:
        query = select(Role).where(Role.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken:
        query = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def revoke_all_for_user(self, user_id: str) -> None:
        query = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
        )
        result = await self.session.execute(query)
        tokens = result.scalars().all()
        for token in tokens:
            token.is_revoked = True
        await self.session.flush()
