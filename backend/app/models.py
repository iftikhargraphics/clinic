from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, Date, Time, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def utcnow(): return datetime.now(timezone.utc)
class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True)
    email: Mapped[str]=mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    role: Mapped[str]=mapped_column(String(30), default="receptionist")
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utcnow)
class Doctor(Base):
    __tablename__="doctors"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(120))
    specialty: Mapped[str]=mapped_column(String(120))
    bio: Mapped[str]=mapped_column(String(500), default="")
    initials: Mapped[str]=mapped_column(String(4), default="DR")
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)
class Service(Base):
    __tablename__="services"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(120), unique=True)
    description: Mapped[str]=mapped_column(String(500), default="")
    duration_minutes: Mapped[int]=mapped_column(Integer, default=30)
    fee_minor: Mapped[int|None]=mapped_column(Integer, nullable=True)
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)
class Appointment(Base):
    __tablename__="appointments"
    id: Mapped[int]=mapped_column(primary_key=True)
    patient_name: Mapped[str]=mapped_column(String(120))
    phone: Mapped[str]=mapped_column(String(40))
    email: Mapped[str|None]=mapped_column(String(254), nullable=True)
    service_id: Mapped[int]=mapped_column(ForeignKey("services.id"), index=True)
    doctor_id: Mapped[int|None]=mapped_column(ForeignKey("doctors.id"), nullable=True, index=True)
    appointment_date: Mapped[object]=mapped_column(Date, index=True)
    appointment_time: Mapped[object]=mapped_column(Time)
    duration_minutes: Mapped[int]=mapped_column(Integer, default=30)
    status: Mapped[str]=mapped_column(String(20), default="pending", index=True)
    consent: Mapped[bool]=mapped_column(Boolean, default=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utcnow)
    service: Mapped[Service]=relationship()
    doctor: Mapped[Doctor|None]=relationship()
    __table_args__=(Index("ix_appointment_slot", "doctor_id", "appointment_date", "appointment_time"),)
class ContactEnquiry(Base):
    __tablename__="contact_enquiries"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(120))
    email: Mapped[str]=mapped_column(String(254))
    message: Mapped[str]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utcnow)
class AuditEvent(Base):
    __tablename__="audit_events"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int|None]=mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str]=mapped_column(String(100))
    entity_type: Mapped[str]=mapped_column(String(60))
    entity_id: Mapped[str]=mapped_column(String(60))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utcnow)
