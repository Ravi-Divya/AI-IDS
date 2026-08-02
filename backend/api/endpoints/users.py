from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ...database.session import get_session
from ...schemas.user import UserResponse, UserListResponse, UserUpdate, RoleCreate, RoleResponse, UserRoleAssignment
from ...repositories.user_repository import UserRepository, RoleRepository
from ...middleware.auth_middleware import get_current_user

router = APIRouter()


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = UserRepository(session)
    items, total = await repo.get_all(skip=(page - 1) * page_size, limit=page_size)
    return {
        "items": [UserResponse.model_validate(u) for u in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = UserRepository(session)
    user = await repo.get(user_id)
    if not user:
        from ...middleware.error_handler import NotFoundException
        raise NotFoundException("User", user_id)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = UserRepository(session)
    user = await repo.update(user_id, **update_data.model_dump(exclude_unset=True))
    if not user:
        from ...middleware.error_handler import NotFoundException
        raise NotFoundException("User", user_id)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = UserRepository(session)
    deleted = await repo.soft_delete(user_id)
    if not deleted:
        from ...middleware.error_handler import NotFoundException
        raise NotFoundException("User", user_id)
    return {"message": "User deleted"}


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = RoleRepository(session)
    role = await repo.create(name=role_data.name, description=role_data.description)
    return RoleResponse.model_validate(role)


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = RoleRepository(session)
    roles, _ = await repo.get_all(limit=100)
    return [RoleResponse.model_validate(r) for r in roles]


@router.post("/assign-role")
async def assign_role(
    assignment: UserRoleAssignment,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = UserRepository(session)
    success = await repo.assign_role(assignment.user_id, assignment.role_id)
    if not success:
        from ...middleware.error_handler import NotFoundException
        raise NotFoundException("User or Role")
    return {"message": "Role assigned"}
