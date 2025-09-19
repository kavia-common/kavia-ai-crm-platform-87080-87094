from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.database import get_db
from src.models.crm_models import Account
from src.schemas.crm import Account as AccountSchema, AccountCreate, AccountUpdate

router = APIRouter(prefix="/accounts", tags=["accounts"])


def _get_account_or_404(db: Session, account_id: int) -> Account:
    inst = db.get(Account, account_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return inst


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[AccountSchema],
    summary="List accounts",
    description="Retrieve a paginated list of accounts filtered by optional query parameters.",
)
def list_accounts(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(default=None, description="Search by name, domain, or industry"),
    owner_user_id: Optional[str] = Query(default=None, description="Filter by owner user id"),
    limit: int = Query(default=50, ge=1, le=200, description="Max number of records"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
):
    stmt = select(Account)
    if q:
        like = f"%{q}%"
        stmt = stmt.filter((Account.name.ilike(like)) | (Account.domain.ilike(like)) | (Account.industry.ilike(like)))
    if owner_user_id:
        stmt = stmt.filter(Account.owner_user_id == owner_user_id)
    stmt = stmt.order_by(Account.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=AccountSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create account",
    description="Create a new account using the provided fields.",
)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    inst = Account(**payload.model_dump(exclude_unset=True))
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# PUBLIC_INTERFACE
@router.get(
    "/{account_id}",
    response_model=AccountSchema,
    summary="Get account",
    description="Retrieve account by id.",
)
def get_account(account_id: int, db: Session = Depends(get_db)):
    return _get_account_or_404(db, account_id)


# PUBLIC_INTERFACE
@router.put(
    "/{account_id}",
    response_model=AccountSchema,
    summary="Update account",
    description="Replace all updatable fields of an account.",
)
def update_account(account_id: int, payload: AccountCreate, db: Session = Depends(get_db)):
    inst = _get_account_or_404(db, account_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(inst, k, v)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# PUBLIC_INTERFACE
@router.patch(
    "/{account_id}",
    response_model=AccountSchema,
    summary="Patch account",
    description="Partially update fields of an account.",
)
def patch_account(account_id: int, payload: AccountUpdate, db: Session = Depends(get_db)):
    inst = _get_account_or_404(db, account_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(inst, k, v)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# PUBLIC_INTERFACE
@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete account",
    description="Delete an account by id.",
)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    inst = _get_account_or_404(db, account_id)
    db.delete(inst)
    db.commit()
    return None
