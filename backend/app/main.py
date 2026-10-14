from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .config import settings
from .database import Base, engine, get_db, SessionLocal
from .models import User, Doctor, Service, Appointment, AuditEvent
from .schemas import DoctorOut, ServiceOut, AppointmentCreate, AppointmentOut, LoginIn, TokenOut, StatusUpdate
from .security import hash_password, verify_password, create_token, decode_token

@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.scalar(select(Service).limit(1)):
            db.add_all([Service(name="Primary care",description="General consultations and preventive care.",duration_minutes=30),Service(name="Specialist consultation",description="A focused appointment with a clinician.",duration_minutes=30),Service(name="Wellness follow-up",description="A follow-up visit to discuss next steps.",duration_minutes=20)])
        if not db.scalar(select(Doctor).limit(1)):
            db.add_all([Doctor(name="Dr. Alex Morgan",specialty="General Practice",bio="Fictional demo profile. Verify credentials before use.",initials="AM"),Doctor(name="Dr. Sam Lee",specialty="Family Medicine",bio="Fictional demo profile. Verify credentials before use.",initials="SL")])
        if settings.admin_password and not db.scalar(select(User).where(User.email==settings.admin_email.lower())):
            db.add(User(email=settings.admin_email.lower(),password_hash=hash_password(settings.admin_password),role="owner",is_active=True))
        db.commit()
    yield
app=FastAPI(title="Clinic Management API",version="0.1.0",description="Starter API for a configurable clinic website.",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=list(settings.allowed_origins),allow_credentials=False,allow_methods=["GET","POST","PATCH"],allow_headers=["Authorization","Content-Type"])
bearer=HTTPBearer(auto_error=False)
@app.middleware("http")
async def security_headers(request:Request,call_next):
    response=await call_next(request);response.headers["X-Content-Type-Options"]="nosniff";response.headers["Referrer-Policy"]="strict-origin-when-cross-origin";response.headers["X-Frame-Options"]="DENY";response.headers["Permissions-Policy"]="camera=(), microphone=(), geolocation=()"
    return response
@app.get("/health")
def health():return {"status":"ok"}
@app.get("/api/doctors",response_model=list[DoctorOut])
def doctors(db:Session=Depends(get_db)):return list(db.scalars(select(Doctor).where(Doctor.is_active.is_(True)).order_by(Doctor.name)))
@app.get("/api/services",response_model=list[ServiceOut])
def services(db:Session=Depends(get_db)):return list(db.scalars(select(Service).where(Service.is_active.is_(True)).order_by(Service.name)))
@app.post("/api/appointments",response_model=AppointmentOut,status_code=201)
def create_appointment(payload:AppointmentCreate,db:Session=Depends(get_db)):
    if not payload.consent:raise HTTPException(422,"Consent is required to contact you about this request")
    if payload.appointment_date < datetime.now().date():raise HTTPException(422,"Choose today or a future date")
    service=db.get(Service,payload.service_id)
    if not service or not service.is_active:raise HTTPException(422,"Please select a valid service")
    if payload.doctor_id is not None:
        doctor=db.get(Doctor,payload.doctor_id)
        if not doctor or not doctor.is_active:raise HTTPException(422,"Please select a valid doctor")
    else:
        doctor=db.scalar(select(Doctor).where(Doctor.is_active.is_(True)).order_by(Doctor.id).limit(1))
        if not doctor:raise HTTPException(409,"No doctors are currently available")
    start=datetime.combine(payload.appointment_date,payload.appointment_time);end=start+timedelta(minutes=service.duration_minutes)
    if start.hour<8 or start.hour>=18 or start.minute not in (0,30):raise HTTPException(422,"Choose a listed appointment time within clinic hours")
    existing=db.scalars(select(Appointment).where(Appointment.doctor_id==doctor.id,Appointment.appointment_date==payload.appointment_date,Appointment.status.notin_(["cancelled","no_show"]))).all()
    for item in existing:
        old_start=datetime.combine(item.appointment_date,item.appointment_time);old_end=old_start+timedelta(minutes=item.duration_minutes)
        if start<old_end and old_start<end:raise HTTPException(409,"That time was just booked. Please choose another time.")
    appointment=Appointment(patient_name=payload.patient_name,phone=payload.phone,email=str(payload.email) if payload.email else None,service_id=service.id,doctor_id=doctor.id,appointment_date=payload.appointment_date,appointment_time=payload.appointment_time,duration_minutes=service.duration_minutes,status="pending",consent=True)
    db.add(appointment)
    try:db.commit();db.refresh(appointment)
    except IntegrityError:db.rollback();raise HTTPException(409,"Could not reserve that slot; please choose another time")
    return AppointmentOut(id=appointment.id,status=appointment.status)
@app.post("/api/auth/login",response_model=TokenOut)
def login(payload:LoginIn,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==payload.email.lower()))
    # Generic response avoids disclosing whether an account exists.
    if not user or not user.is_active or not verify_password(payload.password,user.password_hash):raise HTTPException(401,"Invalid email or password")
    return TokenOut(access_token=create_token(user.id,user.role))
def current_user(credentials:HTTPAuthorizationCredentials|None=Depends(bearer),db:Session=Depends(get_db)):
    if not credentials:raise HTTPException(401,"Authentication required")
    claims=decode_token(credentials.credentials)
    if not claims or not claims.get("sub"):raise HTTPException(401,"Session expired or invalid")
    user=db.get(User,int(claims["sub"]))
    if not user or not user.is_active:raise HTTPException(401,"Session expired or invalid")
    return user
def require_staff(user:User=Depends(current_user)):
    if user.role not in {"owner","admin","receptionist"}:raise HTTPException(403,"Insufficient permissions")
    return user
@app.get("/api/admin/appointments")
def list_appointments(db:Session=Depends(get_db),user:User=Depends(require_staff)):
    rows=db.scalars(select(Appointment).order_by(Appointment.appointment_date.desc(),Appointment.appointment_time.desc()).limit(500)).all()
    return [{"id":a.id,"patient_name":a.patient_name,"phone":a.phone,"service_name":a.service.name,"doctor_name":a.doctor.name if a.doctor else "Unassigned","appointment_date":a.appointment_date.isoformat(),"appointment_time":a.appointment_time.strftime("%H:%M"),"status":a.status} for a in rows]
@app.patch("/api/admin/appointments/{appointment_id}")
def update_appointment(appointment_id:int,payload:StatusUpdate,db:Session=Depends(get_db),user:User=Depends(require_staff)):
    allowed={"pending","confirmed","completed","cancelled","no_show"}
    if payload.status not in allowed:raise HTTPException(422,"Invalid appointment status")
    item=db.get(Appointment,appointment_id)
    if not item:raise HTTPException(404,"Appointment not found")
    item.status=payload.status;db.add(AuditEvent(user_id=user.id,action="appointment.status_changed",entity_type="appointment",entity_id=str(item.id)));db.commit()
    return {"id":item.id,"status":item.status}
