from datetime import UTC, datetime

from app.database import Base, engine  # noqa: F401
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    rut = Column(String, unique=True, nullable=True)
    hash_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    ingresos = relationship("Ingreso", back_populates="usuario", cascade="all, delete-orphan")


class Ingreso(Base):
    __tablename__ = "ingresos"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    monto_bruto = Column(Float, nullable=False)
    fecha_emision = Column(DateTime, nullable=False)
    descripcion = Column(String, nullable=True)
    cliente = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    usuario = relationship("Usuario", back_populates="ingresos")



