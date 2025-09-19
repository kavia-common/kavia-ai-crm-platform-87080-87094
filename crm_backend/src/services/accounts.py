from src.db.models import Account
from src.schemas.accounts import AccountCreate, AccountUpdate
from src.services.common import CRUDService


class AccountService(CRUDService[Account, AccountCreate, AccountUpdate]):
    pass


account_service = AccountService(Account)
