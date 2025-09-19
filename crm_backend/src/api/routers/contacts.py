from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.database import get_db
from src.models.crm_models import Contact
from src.schemas.crm import Contact as ContactSchema, ContactCreate, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])


def _get_or_404(db: Session, contact_id: int) -> Contact:
    inst = db.get(Contact, contact_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return inst


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[ContactSchema],
    summary="List contacts",
    description="Retrieve contacts with optional filters and pagination.",
)
def list_contacts(
    db: Session = Depends(get_db),
    account_id: Optional[int] = Query(default=None, description="Filter by account id"),
    q: Optional[str] = Query(default=None, description="Search by name, email, or phone"),
    owner_user_id: Optional[str] = Query(default=None, description="Filter by owner user id"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(Contact)
    if account_id is not None:
        stmt = stmt.filter(Contact.account_id == account_id)
    if is_active is not None:
        stmt = stmt.filter(Contact.is_active == is_active)
    if owner_user_id:
        stmt = stmt.filter(Contact.owner_user_id == owner_user_id)
    if q:
        like = f"%{q}%"
        stmt = stmt.filter(
            (Contact.first_name.ilike(like))
            | (Contact.last_name.ilike(like))
            | (Contact.email.ilike(like))
            | (Contact.phone.ilike(like))
        )
    stmt = stmt.order_by(Contact.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=ContactSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create contact",
    description="Create a new contact record.",
)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    inst = Contact(**payload.model_dump(exclude_unset=True))
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# PUBLIC_INTERFACE
@router.get(
    "/{contact_id}",
    response_model=ContactSchema,
    summary="Get contact",
    description="Retrieve a contact by id.",
)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, contact_id)


# PUBLIC_INTERFACE
@router.put(
    "/{contact_id}",
    response_model=ContactSchema,
    summary="Update contact",
    description="Replace all updatable fields of a contact.",
)
def update_contact(contact_id: int, payload: ContactCreate, db: Session = Depends(get_db)):
    inst = _get_or_404(db, contact_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(inst, k, v)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# PUBLIC_INTERFACE
@router.patch(
    "/{contact_id}",
    response_model=ContactSchema,
    summary="Patch contact",
    description="Partially update fields of a contact.",
)
def patch_contact(contact_id: int, payload: ContactUpdate, db: Session = Depends(get_db)):
    inst = _get_or_404(db, contact_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(inst, k, v)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# PUBLIC_INTERFACE
@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete contact",
    description="Delete a contact by id.",
)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    inst = _get_or_404(db, contact_id)
    db.delete(inst)
    db.commit()
    return None
