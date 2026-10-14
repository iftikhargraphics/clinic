from datetime import date, time
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
class DoctorOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; name:str; specialty:str; bio:str; initials:str
class ServiceOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; name:str; description:str; duration_minutes:int; fee_minor:int|None
class AppointmentCreate(BaseModel):
    patient_name:str=Field(min_length=2,max_length=120)
    phone:str=Field(min_length=5,max_length=40)
    email:EmailStr|None=None
    service_id:int
    doctor_id:int|None=None
    appointment_date:date
    appointment_time:time
    consent:bool
    @field_validator("patient_name","phone")
    @classmethod
    def strip_fields(cls,v):
        v=v.strip()
        if not v: raise ValueError("This field is required")
        return v
class AppointmentOut(BaseModel):
    id:int; status:str
class LoginIn(BaseModel):
    email:EmailStr
    password:str=Field(min_length=1,max_length=200)
class TokenOut(BaseModel): access_token:str; token_type:str="bearer"
class StatusUpdate(BaseModel): status:str
