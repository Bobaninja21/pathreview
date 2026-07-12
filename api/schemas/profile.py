from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from uuid import UUID
from typing import Optional


class ProfileCreate(BaseModel):
    github_username: Optional[str] = Field(default=None, max_length=255)
    portfolio_url: Optional[str] = Field(default=None, max_length=500)


class ProfileUpdate(BaseModel):
    github_username: Optional[str] = Field(default=None, max_length=255)
    portfolio_url: Optional[str] = Field(default=None, max_length=500)


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    github_username: Optional[str]
    portfolio_url: Optional[str]
    created_at: datetime
    resume_filename: Optional[str]

    @computed_field
    @property
    def profile_id(self) -> UUID:
        return self.id

    model_config = {"from_attributes": True}
