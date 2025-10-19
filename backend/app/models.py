from datetime import datetime
import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'taxbot.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    rut = Column(String, unique=True, nullable=True)
    hash_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    ingresos = relationship("Ingreso", back_populates="usuario", cascade="all, delete-orphan")


class Ingreso(Base):
    __tablename__ = "ingresos"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    monto_bruto = Column(Float, nullable=False)
    fecha_emision = Column(DateTime, nullable=False)
    descripcion = Column(String, nullable=True)
    cliente = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    usuario = relationship("Usuario", back_populates="ingresos")


Base.metadata.create_all(bind=engine)
