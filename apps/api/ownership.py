"""Request and response schemas for FORTUNA ownership evidence."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


DocumentType = Literal[
    "grundbuchauszug",
    "handelsregister",
    "kaufvertrag",
    "fahrzeugbrief",
    "erc721",
    "kontoauszug",
    "sonstiger_nachweis",
]
ObservationKind = Literal["value", "signature", "seal"]
ExtractionMethod = Literal["manual", "ocr", "metadata"]


class OwnershipObservationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_kind: ObservationKind
    label: str = Field(min_length=1, max_length=200)
    observed_text: str = Field(min_length=1, max_length=4000)
    interpreted_meaning: str | None = Field(default=None, max_length=2000)
    normalized_value: str | None = Field(default=None, max_length=1000)
    page_number: int | None = Field(default=None, ge=1)
    extraction_method: ExtractionMethod = "manual"


class OwnershipObservationResponse(OwnershipObservationCreate):
    review_status: Literal["UNREVIEWED"] = "UNREVIEWED"


class OwnershipProofCreate(BaseModel):
    """A claimant-submitted record; fields do not assert legal verification."""

    model_config = ConfigDict(extra="forbid")

    asset_id: UUID
    claimed_owner: str = Field(min_length=1, max_length=300)
    ownership_claim: str = Field(min_length=1, max_length=100)
    document_type: DocumentType
    reference_number: str | None = Field(default=None, max_length=255)
    document_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    storage_key: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z0-9_-]{1,128}$",
        description="Opaque encrypted-storage object key; filesystem paths are not accepted.",
    )
    observations: list[OwnershipObservationCreate] = Field(default_factory=list, max_length=100)
    notes: str | None = Field(default=None, max_length=2000)


class OwnershipProofResponse(OwnershipProofCreate):
    id: UUID
    evidence_id: UUID
    claimant_id: str
    verification_status: Literal["SUBMITTED"] = "SUBMITTED"
    created_at: datetime
    observations: list[OwnershipObservationResponse] = Field(default_factory=list)
