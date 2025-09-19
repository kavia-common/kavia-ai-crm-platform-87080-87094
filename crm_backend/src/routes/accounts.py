from typing import List
from fastapi import APIRouter, HTTPException, Query
from src.db.session import get_session
from src.schemas.accounts import AccountCreate, AccountOut, AccountUpdate
from src.services.accounts import account_service

router = APIRouter()


@router.get("/", response_model=List[AccountOut], summary="List accounts")
# PUBLIC_INTERFACE
def list_accounts(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    """
    List accounts with pagination.
    """
    db = get_session()
    skip = (page - 1) * size
    return account_service.list(db, skip=skip, limit=size)


@router.post("/", response_model=AccountOut, status_code=201, summary="Create account")
# PUBLIC_INTERFACE
def create_account(payload: AccountCreate):
    """
    Create a new account.
    """
    db = get_session()
    return account_service.create(db, payload)


@router.get("/{account_id}", response_model=AccountOut, summary="Get account")
# PUBLIC_INTERFACE
def get_account(account_id: int):
    """
    Get account by ID.
    """
    db = get_session()
    obj = account_service.get(db, account_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Account not found")
    return obj


@router.put("/{account_id}", response_model=AccountOut, summary="Update account")
# PUBLIC_INTERFACE
def update_account(account_id: int, payload: AccountUpdate):
    """
    Update account fields.
    """
    db = get_session()
    obj = account_service.get(db, account_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Account not found")
    return account_service.update(db, obj, payload)


@router.delete("/{account_id}", status_code=204, summary="Delete account")
# PUBLIC_INTERFACE
def delete_account(account_id: int):
    """
    Delete account by ID.
    """
    db = get_session()
    obj = account_service.get(db, account_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Account not found")
    account_service.delete(db, obj)
    return None
