"""
Pydantic v2 schemas for the Company resource.
Separates API contract from ORM model.
"""

from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str
    industry: str | None = None
    description: str | None = None


class CompanyCreate(CompanyBase):
    """Payload for creating a new company."""
    pass


class CompanyUpdate(BaseModel):
    """Payload for partial updates — all fields optional."""
    name: str | None = None
    industry: str | None = None
    description: str | None = None


class CompanyRead(CompanyBase):
    """Response schema — includes server-generated id."""
    id: int

    model_config = {"from_attributes": True}
