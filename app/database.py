# app/database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("❌ DATABASE_URL environment variable is not set!")
    # For local development only
    DATABASE_URL = "sqlite:///./app.db"
    logger.warning(f"Using SQLite fallback: {DATABASE_URL}")

logger.info(f"Connecting to database...")

# Handle different database types
connect_args = {}
if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # For PostgreSQL, ensure SSL is used
    if DATABASE_URL and "sslmode" not in DATABASE_URL:
        separator = "?" if "?" not in DATABASE_URL else "&"
        DATABASE_URL += f"{separator}sslmode=require"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# Test connection
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful!")
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    total_sessions = Column(Integer, default=0)

# Activity Model
class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    activity_type = Column(String)
    activity_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

# Reflection Model
class Reflection(Base):
    __tablename__ = "reflections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    question = Column(String)
    answer = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Goal Model
class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    text = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

# Create tables
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")

# Initialize on import
init_db()