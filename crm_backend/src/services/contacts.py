from sqlalchemy.orm import Session
from sqlalchemy import select
from src.db.models import Contact
from src.schemas.contacts import ContactCreate, ContactUpdate
from src.services.common import CRUDService


class ContactService(CRUDService[Contact, ContactCreate, ContactUpdate]):
    def by_email(self, db: Session, email: str):
        stmt = select(Contact).where(Contact.email == email)
        return db.execute(stmt).scalar_one_or_none()


contact_service = ContactService(Contact)
