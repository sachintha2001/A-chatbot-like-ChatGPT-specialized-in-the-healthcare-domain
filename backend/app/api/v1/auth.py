from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db_session
from app.models.user import User, UserRole
from app.models.audit import AuditActionType, ComplianceStatus
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.auth.security import hash_password, verify_password, create_access_token, get_current_user
from app.compliance.audit_logger import audit_logger

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    stmt = select(User).where(User.email == payload.email)
    res = await session.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this clinical email address already exists"
        )

    # Clinicians must provide licensing credential identifier
    if payload.role == UserRole.CLINICIAN and not payload.license_credential_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Licensed healthcare providers must provide a valid NPI, GMC, or institutional medical license number"
        )

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        license_credential_id=payload.license_credential_id,
        is_active=True
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    await audit_logger.log_event(
        session=session,
        action_type=AuditActionType.AUTHENTICATION_EVENT,
        resource_accessed="/auth/register",
        user_id=user.id,
        compliance_status=ComplianceStatus.COMPLIANT,
        metadata={"role": user.role.value, "credential_id": user.license_credential_id}
    )

    return user


@router.post("/login", response_model=TokenResponse)
async def login_user(
    payload: UserLogin,
    session: AsyncSession = Depends(get_db_session)
):
    stmt = select(User).where(User.email == payload.email)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid clinical credentials provided"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been suspended or deactivated by clinical governance"
        )

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        credential_id=user.license_credential_id
    )

    await audit_logger.log_event(
        session=session,
        action_type=AuditActionType.AUTHENTICATION_EVENT,
        resource_accessed="/auth/login",
        user_id=user.id,
        compliance_status=ComplianceStatus.COMPLIANT,
        metadata={"role": user.role.value}
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
