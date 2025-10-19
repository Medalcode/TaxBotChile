from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime
from app.models import engine, Usuario, Ingreso
from app.schemas import (
    IngresoCreate,
    IngresoResponse,
    BoletaResponse,
    ProyeccionResponse,
    GlobalComplementarioResponse,
    RecomendacionItem,
)
from app.services.auth import get_usuario_from_token
from app.services.tax_calculator import (
    calcular_retencion_boleta,
    calcular_proyeccion_anual,
    calcular_recomendaciones,
)

router = APIRouter(prefix="/api", tags=["ingresos"])

SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/ingresos", response_model=IngresoResponse)
def registrar_ingreso(
    payload: IngresoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_from_token),
):
    try:
        fecha = datetime.strptime(payload.fecha_emision, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    ingreso = Ingreso(
        usuario_id=usuario.id,
        monto_bruto=payload.monto_bruto,
        fecha_emision=fecha,
        descripcion=payload.descripcion,
        cliente=payload.cliente,
    )
    db.add(ingreso)
    db.commit()
    db.refresh(ingreso)
    return ingreso


@router.get("/ingresos", response_model=list[IngresoResponse])
def listar_ingresos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_from_token),
):
    return db.query(Ingreso).filter(Ingreso.usuario_id == usuario.id).order_by(Ingreso.fecha_emision.desc()).all()


@router.delete("/ingresos/{ingreso_id}")
def eliminar_ingreso(
    ingreso_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_from_token),
):
    ingreso = db.query(Ingreso).filter(Ingreso.id == ingreso_id, Ingreso.usuario_id == usuario.id).first()
    if not ingreso:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
    db.delete(ingreso)
    db.commit()
    return {"status": "ok"}


@router.post("/calcular/boleta", response_model=BoletaResponse)
def calcular_boleta(monto: float):
    return calcular_retencion_boleta(monto)


@router.get("/proyeccion", response_model=ProyeccionResponse)
def obtener_proyeccion(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_from_token),
):
    ingresos = db.query(Ingreso).filter(Ingreso.usuario_id == usuario.id).all()
    if not ingresos:
        raise HTTPException(status_code=404, detail="No hay ingresos registrados. Agrega al menos uno.")

    mensual: dict[str, list[float]] = {}
    for ing in ingresos:
        mes = ing.fecha_emision.strftime("%Y-%m")
        if mes not in mensual:
            mensual[mes] = []
        mensual[mes].append(ing.monto_bruto)

    meses_ordenados = sorted(mensual.keys())
    montos_mensuales = [sum(mensual[m]) for m in meses_ordenados]
    return calcular_proyeccion_anual(montos_mensuales)


@router.get("/recomendaciones", response_model=list[RecomendacionItem])
def obtener_recomendaciones(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_from_token),
):
    ingresos = db.query(Ingreso).filter(Ingreso.usuario_id == usuario.id).all()
    if not ingresos:
        raise HTTPException(status_code=404, detail="No hay ingresos registrados.")

    mensual: dict[str, list[float]] = {}
    for ing in ingresos:
        mes = ing.fecha_emision.strftime("%Y-%m")
        if mes not in mensual:
            mensual[mes] = []
        mensual[mes].append(ing.monto_bruto)

    meses_ordenados = sorted(mensual.keys())
    montos_mensuales = [sum(mensual[m]) for m in meses_ordenados]
    return calcular_recomendaciones(montos_mensuales)
