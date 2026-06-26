"""
Company endpoints for RAVAND OS.
Handles HTTP layer only — delegates logic to crud/company.py.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import company as crud
from app.database.session import get_db
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate

router = APIRouter(prefix="/company", tags=["Company"])


@router.get("/", response_model=list[CompanyRead], summary="List all companies")
def list_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_companies(db, skip=skip, limit=limit)


@router.post("/", response_model=CompanyRead, status_code=status.HTTP_201_CREATED, summary="Create a company")
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    return crud.create_company(db, payload)


@router.get("/{company_id}", response_model=CompanyRead, summary="Get a company by ID")
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.patch("/{company_id}", response_model=CompanyRead, summary="Partially update a company")
def update_company(company_id: int, payload: CompanyUpdate, db: Session = Depends(get_db)):
    company = crud.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return crud.update_company(db, company, payload)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a company")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    crud.delete_company(db, company)
