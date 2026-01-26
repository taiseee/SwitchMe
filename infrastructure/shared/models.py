"""SQLAlchemy ORM models"""

from datetime import datetime, UTC
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Float,
    JSON,
    ForeignKey,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()


class UserModel(Base):
    """User ORM model"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    oauth_provider = Column(String, nullable=False)
    oauth_user_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    milestones = relationship(
        "MilestoneModel", back_populates="user", cascade="all, delete-orphan"
    )


class MilestoneModel(Base):
    """Milestone ORM model"""

    __tablename__ = "milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String, nullable=False)

    # Deadline information
    deadline_date = Column(String, nullable=False)  # ISO format date string
    deadline_time = Column(String, nullable=False)  # ISO format time string
    timezone = Column(String, nullable=False)

    # Verification criteria
    verification_type = Column(String, nullable=False)
    verification_conditions = Column(JSON, nullable=False)
    verification_threshold = Column(Float, nullable=False)

    # Penalty information
    penalty_amount = Column(Integer, nullable=False)
    penalty_currency = Column(String, nullable=False)
    penalty_description = Column(String, nullable=False, default="")

    # Status
    status = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    user = relationship("UserModel", back_populates="milestones")
    verifications = relationship(
        "VerificationModel", back_populates="milestone", cascade="all, delete-orphan"
    )


class VerificationModel(Base):
    """Verification ORM model"""

    __tablename__ = "verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    milestone_id = Column(
        UUID(as_uuid=True),
        ForeignKey("milestones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String, nullable=False)

    # Verification result (nullable until completed)
    result_success = Column(Boolean, nullable=True)
    result_score = Column(Float, nullable=True)
    result_confidence = Column(Float, nullable=True)
    result_evidence = Column(JSON, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    milestone = relationship("MilestoneModel", back_populates="verifications")
    user = relationship("UserModel")
    sensor_data = relationship(
        "SensorDataModel", back_populates="verification", cascade="all, delete-orphan"
    )


class SensorDataModel(Base):
    """Sensor Data ORM model"""

    __tablename__ = "sensor_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(
        UUID(as_uuid=True),
        ForeignKey("verifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    verification = relationship("VerificationModel", back_populates="sensor_data")
