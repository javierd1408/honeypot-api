from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base

class IntrusionLog(Base):
    __tablename__ = "intrusion_logs"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    user_agent = Column(String)
    headers = Column(JSON)
    payload = Column(String, nullable=True) # Storing as string to handle arbitrary bad payloads
    endpoint = Column(String, index=True)
    method = Column(String)
    threat_type = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
