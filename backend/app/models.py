import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    role = Column(String(50), default="engineer")
    created_at = Column(DateTime(timezone=True), default=utc_now)

    workstations = relationship("Workstation", back_populates="user")
    jobs = relationship("Job", back_populates="user")

class Workstation(Base):
    __tablename__ = "workstations"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    ip_address = Column(String(50), unique=True, index=True, nullable=False)
    hostname = Column(String(100), nullable=True)
    os_name = Column(String(50), default="Windows")
    status = Column(String(50), default="OFFLINE") # READY, BUSY, OFFLINE
    user_id = Column(String(64), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="workstations")
    agents = relationship("AutodeskAgent", back_populates="workstation")

class AutodeskAgent(Base):
    __tablename__ = "autodesk_agents"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    workstation_ip = Column(String(50), index=True, nullable=False)
    workstation_id = Column(String(64), ForeignKey("workstations.id"), nullable=True)
    application_name = Column(String(50), default="Inventor") # Inventor, Fusion, AutoCAD
    application_version = Column(String(50), nullable=True)
    status = Column(String(50), default="CONNECTED") # CONNECTED, READY, BUSY, DISCONNECTED
    is_active = Column(Boolean, default=True)
    last_heartbeat = Column(DateTime(timezone=True), default=utc_now)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    workstation = relationship("Workstation", back_populates="agents")
    jobs = relationship("Job", back_populates="agent")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(64), primary_key=True, default=lambda: f"job-{uuid.uuid4().hex[:8]}")
    user_id = Column(String(64), ForeignKey("users.id"), nullable=True)
    workstation_ip = Column(String(50), index=True, nullable=False)
    agent_id = Column(String(64), ForeignKey("autodesk_agents.id"), nullable=True)
    prompt = Column(Text, nullable=False)
    tool_name = Column(String(100), nullable=False)
    parameters = Column(JSON, nullable=False)
    status = Column(String(50), default="PENDING") # PENDING, VALIDATED, QUEUED, DISPATCHED, EXECUTING, COMPLETED, FAILED
    result_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="jobs")
    agent = relationship("AutodeskAgent", back_populates="jobs")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(100), nullable=False)
    user_identifier = Column(String(100), nullable=True)
    workstation_ip = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now)
