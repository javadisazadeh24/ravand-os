"""
CRUD operations for the Company model.
Pure database logic — no HTTP concerns here.
"""

from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


def get_company(db: Session, company_id: int) -> Company | None:
    return db.get(Company, company_id)


def get_companies(db: Session, skip: int = 0, limit: int = 100) -> list[Company]:
    return db.query(Company).offset(skip).limit(limit).all()


def create_company(db: Session, payload: CompanyCreate) -> Company:
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def update_company(db: Session, company: Company, payload: CompanyUpdate) -> Company:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return company


def delete_company(db: Session, company: Company) -> None:
    db.delete(company)
    db.commit()
