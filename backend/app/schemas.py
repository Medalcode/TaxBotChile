from datetime import datetime

from pydantic import BaseModel, Field


class UsuarioCreate(BaseModel):
    email: str
    nombre: str
    password: str = Field(min_length=6)
    rut: str | None = None


class UsuarioResponse(BaseModel):
    id: int
    email: str
    nombre: str
    rut: str | None = None

    model_config = {"from_attributes": True}


class IngresoCreate(BaseModel):
    monto_bruto: float = Field(gt=0)
    fecha_emision: str
    descripcion: str | None = None
    cliente: str | None = None


class IngresoResponse(BaseModel):
    id: int
    monto_bruto: float
    fecha_emision: datetime
    descripcion: str | None = None
    cliente: str | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str


class BoletaResponse(BaseModel):
    monto_bruto: float
    retencion: float
    liquido_a_recibir: int
    tasa_retencion: float


class GlobalComplementarioResponse(BaseModel):
    ingreso_bruto_anual: float
    utm_equivalentes: float
    tasa_efectiva: float
    impuesto_calculado: float
    total_retenido_anual: float
    saldo_a_pagar: float
    saldo_a_favor: float


class ProyeccionResponse(BaseModel):
    total_ingresado: float
    meses_activos: int
    promedio_mensual: float
    proyeccion_anual: float
    retencion_promedio_mensual: float
    ahorro_sugerido_mensual: float
    global_complementario: GlobalComplementarioResponse


class RecomendacionItem(BaseModel):
    tipo: str
    mensaje: str
