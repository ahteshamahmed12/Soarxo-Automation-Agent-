"""Auth API router: signup requests, admin approval, login, user management.

Endpoints:
  POST   /api/auth/request-signup   — public: submit signup request
  GET    /api/auth/requests         — owner: list pending requests
  POST   /api/auth/approve/{id}     — owner: approve + create user
  POST   /api/auth/reject/{id}      — owner: reject a request
  POST   /api/auth/login            — public: login with email + password
  GET    /api/auth/me               — JWT: get current user
  GET    /api/auth/users            — owner: list all users
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session, select

from ..core.database import get_session
from ..models.auth import SignupRequest, User, UserRole, UserStatus
from ..services.auth import (
    authenticate_user,
    create_access_token,
    get_user_by_email,
    get_user_by_id,
    hash_password,
    require_role,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class RequestSignupRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = None
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    def model_post_init(self, __context) -> None:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str | None = None
    role: str
    status: str
    created_at: str | None = None
    approved_at: str | None = None


class SignupRequestResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str | None = None
    status: str
    created_at: str | None = None


class ApproveRequest(BaseModel):
    role: str = "user"  # "user" or "admin"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/request-signup", status_code=status.HTTP_201_CREATED)
def request_signup(
    payload: RequestSignupRequest,
    db: Session = Depends(get_session),
):
    """Submit a signup request. No immediate account creation — requires approval."""
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    existing_request = db.exec(
        select(SignupRequest).where(SignupRequest.email == payload.email)
    ).first()
    if existing_request and existing_request.status == "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A signup request with this email is already pending",
        )

    signup_req = SignupRequest(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        status="pending",
    )
    db.add(signup_req)
    db.commit()
    db.refresh(signup_req)

    return {"message": "Signup request submitted — pending admin approval", "request_id": signup_req.id}


@router.get("/requests", response_model=list[SignupRequestResponse])
def list_signup_requests(
    status_filter: str = "pending",
    db: Session = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.ADMIN)),
):
    """List signup requests. Owner/admin only."""
    stmt = select(SignupRequest).where(SignupRequest.status == status_filter)
    requests = db.exec(stmt).all()
    return [
        SignupRequestResponse(
            id=r.id,
            full_name=r.full_name,
            email=r.email,
            phone=r.phone,
            status=r.status or "pending",
            created_at=str(r.created_at) if r.created_at else None,
        )
        for r in requests
    ]


@router.post("/approve/{request_id}", status_code=status.HTTP_200_OK)
def approve_signup_request(
    request_id: int,
    payload: ApproveRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.ADMIN)),
):
    """Approve a signup request → creates an ACTIVE User account."""
    req = db.get(SignupRequest, request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signup request not found",
        )
    if req.status == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request already approved",
        )
    if req.status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot re-approve a rejected request",
        )

    role = UserRole(payload.role) if payload.role in UserRole.__members__ else UserRole.USER
    if role == UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot self-promote to owner via this endpoint",
        )

    user = User(
        email=req.email,
        full_name=req.full_name,
        phone=req.phone,
        password_hash=req.password_hash,
        role=role,
        status=UserStatus.ACTIVE,
        approved_at=req.created_at,
    )
    db.add(user)

    req.status = "approved"
    req.reviewed_by = current_user.id
    req.reviewed_at = req.created_at  # approximate; use utcnow in real impl

    db.commit()
    db.refresh(user)
    db.refresh(req)

    return {"message": "User approved", "user_id": user.id, "email": user.email}


@router.post("/reject/{request_id}", status_code=status.HTTP_200_OK)
def reject_signup_request(
    request_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.ADMIN)),
):
    """Reject a pending signup request."""
    req = db.get(SignupRequest, request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signup request not found",
        )
    if req.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject a request with status '{req.status}'",
        )

    req.status = "rejected"
    from ..core.utils import utcnow
    req.reviewed_by = current_user.id
    req.reviewed_at = utcnow()
    db.commit()

    return {"message": "Signup request rejected"}


@router.post("/login")
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_session),
):
    """Authenticate a user and return a JWT token.

    Token is returned in both the JSON body and an httponly cookie
    (so the frontend can use either approach for dynamic fetching).
    """
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=int(settings.JWT_EXPIRE_MINUTES * 60),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role.value,
            status=user.status.value,
            created_at=str(user.created_at) if user.created_at else None,
            approved_at=str(user.approved_at) if user.approved_at else None,
        ),
    }


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.ADMIN, UserRole.USER)),
):
    """Get the authenticated user's profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role=current_user.role.value,
        status=current_user.status.value,
        created_at=str(current_user.created_at) if current_user.created_at else None,
        approved_at=str(current_user.approved_at) if current_user.approved_at else None,
    )


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.OWNER)),
):
    """List all users. Owner only."""
    stmt = select(User)
    users = db.exec(stmt).all()
    return [
        UserResponse(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            phone=u.phone,
            role=u.role.value,
            status=u.status.value,
            created_at=str(u.created_at) if u.created_at else None,
            approved_at=str(u.approved_at) if u.approved_at else None,
        )
        for u in users
    ]
