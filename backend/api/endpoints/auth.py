from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from ...database.session import get_session
from ...schemas.user import LoginRequest, LoginResponse, RefreshTokenRequest, TokenResponse, ChangePasswordRequest, UserCreate
from ...services.auth_service import AuthService
from ...middleware.auth_middleware import get_current_user


class SetupCompanyRequest(BaseModel):
    company_name: str

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, req: Request, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    result = await service.login(request.username, request.password, req.client.host)
    return result


@router.post("/register", response_model=LoginResponse)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    result = await service.register(user_data.email, user_data.username, user_data.password, user_data.full_name)
    return result


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    result = await service.refresh_token(request.refresh_token)
    return result


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    await service.logout(current_user["sub"])
    return {"message": "Logged out successfully"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = AuthService(session)
    await service.change_password(current_user["sub"], request.current_password, request.new_password)
    return {"message": "Password changed successfully"}


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    return await service.get_current_user(current_user["sub"])


@router.post("/setup-company")
async def setup_company(
    request: SetupCompanyRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = AuthService(session)
    return await service.setup_company(current_user["sub"], request.company_name)



