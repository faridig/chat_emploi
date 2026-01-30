"""SQLAlchemy models for Chat Emploi database.

This module defines the database schema according to TECH_SPECS.md section 3.1.
"""

import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class User(Base):
    """User model representing a local session/user."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID v7
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_active: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, nullable=False, default=dict
    )

    # Relationships
    anonymized_profiles: Mapped[list["AnonymizedProfile"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    applications: Mapped[list["Application"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    conversation_history: Mapped[list["ConversationHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    feedback: Mapped[list["Feedback"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, created_at={self.created_at!r})"


class AnonymizedProfile(Base):
    """Anonymized CV profile with extracted data."""

    __tablename__ = "anonymized_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    original_hash: Mapped[str] = mapped_column(
        String, nullable=False
    )  # hash of original file
    anonymized_path: Mapped[str] = mapped_column(
        String, nullable=False
    )  # path to anonymized file
    analysis_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    extracted_data: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    embedding_vector: Mapped[bytes | None] = mapped_column(
        LargeBinary
    )  # serialized embedding
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="anonymized_profiles")
    applications: Mapped[list["Application"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"AnonymizedProfile(id={self.id!r}, user_id={self.user_id!r})"


class JobOffer(Base):
    """Job offer cached from France Travail and other sources."""

    __tablename__ = "job_offers"

    id: Mapped[str] = mapped_column(
        String, primary_key=True
    )  # France Travail ID + hash
    source: Mapped[str] = mapped_column(
        String, nullable=False
    )  # 'france_travail', 'web_scraped', 'manual'
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    title: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    contract_type: Mapped[str] = mapped_column(String, nullable=False)
    publication_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_vector: Mapped[bytes | None] = mapped_column(
        LargeBinary
    )  # serialized embedding
    fetched_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    applications: Mapped[list["Application"]] = relationship(
        back_populates="offer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"JobOffer(id={self.id!r}, title={self.title!r}, company={self.company!r})"
        )


class Application(Base):
    """Job application tracking."""

    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    profile_id: Mapped[str | None] = mapped_column(ForeignKey("anonymized_profiles.id"))
    offer_id: Mapped[str | None] = mapped_column(ForeignKey("job_offers.id"))
    status: Mapped[str] = mapped_column(
        String,
        CheckConstraint(
            "status IN ('draft', 'applied', 'interview', 'rejected', 'accepted')",
            name="valid_status",
        ),
        nullable=False,
        default="draft",
    )
    applied_date: Mapped[datetime.date | None] = mapped_column(Date)
    cover_letter_path: Mapped[str | None] = mapped_column(String)
    notes: Mapped[str | None] = mapped_column(Text)
    interview_date: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    reminders: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="applications")
    profile: Mapped[Optional["AnonymizedProfile"]] = relationship(
        back_populates="applications"
    )
    offer: Mapped[Optional["JobOffer"]] = relationship(back_populates="applications")

    def __repr__(self) -> str:
        return f"Application(id={self.id!r}, user_id={self.user_id!r}, status={self.status!r})"


class ConversationHistory(Base):
    """History of conversations with AI agents."""

    __tablename__ = "conversation_history"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    agent_type: Mapped[str] = mapped_column(
        String, nullable=False
    )  # 'coach', 'researcher', 'writer', 'interviewer'
    message_type: Mapped[str] = mapped_column(
        String,
        CheckConstraint("message_type IN ('user', 'agent')", name="valid_message_type"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, nullable=False, default=dict
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="conversation_history")

    def __repr__(self) -> str:
        return f"ConversationHistory(id={self.id!r}, agent_type={self.agent_type!r}, message_type={self.message_type!r})"


class Feedback(Base):
    """User feedback for continuous improvement."""

    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    item_type: Mapped[str] = mapped_column(
        String, nullable=False
    )  # 'offer', 'letter', 'interview', 'agent_response'
    item_id: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[int] = mapped_column(
        CheckConstraint("rating BETWEEN 1 AND 5", name="valid_rating"), nullable=False
    )
    comment: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, nullable=False, default=dict
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="feedback")

    def __repr__(self) -> str:
        return f"Feedback(id={self.id!r}, item_type={self.item_type!r}, rating={self.rating!r})"


class AuditLog(Base):
    """Audit trail for GDPR compliance and security."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    event_type: Mapped[str] = mapped_column(
        String, nullable=False
    )  # 'cv_upload', 'api_call', 'data_export', 'data_deletion'
    event_data: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    ip_address: Mapped[str | None] = mapped_column(String)
    user_agent: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"AuditLog(id={self.id!r}, event_type={self.event_type!r}, user_id={self.user_id!r})"


# Export all models
__all__ = [
    "Base",
    "User",
    "AnonymizedProfile",
    "JobOffer",
    "Application",
    "ConversationHistory",
    "Feedback",
    "AuditLog",
]
