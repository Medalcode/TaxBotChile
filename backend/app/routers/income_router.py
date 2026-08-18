from datetime import datetime
from typing import Any

from app.database import get_db
from app.models import Ingreso, Usuario
from app.schemas import (
    BoletaResponse,
    IngresoCreate,
    IngresoResponse,
    ProyeccionResponse,
    RecomendacionItem,
)
from app.services.auth import get_usuario_from_token
from app.services.tax_calculator import (
    calcular_proyeccion_anual,
    calcular_recomendaciones,
    calcular_retencion_boleta,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["ingresos"])


def _obtener_montos_mensuales(db: Session, usuario_id: int) -> list[float]:
    ingresos = db.query(Ingreso).filter(Ingreso.usuario_id == usuario_id).all()
    if not ingresos:
        return []

    mensual: dict[str, list[float]] = {}
    for ing in ingresos:
        mes = ing.fecha_emision.strftime("%Y-%m")
        if mes not in mensual:
            mensual[mes] = []
        mensual[mes].append(ing.monto_bruto)

    meses_ordenados = sorted(mensual.keys())
    return [sum(mensual[m]) for m in meses_ordenados]


@router.post("/ingresos", response_model=IngresoResponse)
def registrar_ingreso(
    payload: IngresoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_from_token),
) -> Ingreso:
    try:
        fecha = datetime.strptime(payload.fecha_emision, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Use YYYY-MM-DD",
        ) from None
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
) -> list[Ingreso]:
    ingresos = (
        db.query(Ingreso)
        .filter(Ingreso.usuario_id == usuario.id)
        .order_by(Ingreso.fecha_emision.desc())
        .all()
    )
    return list(ingresos)


@router.delete("/ingresos/{ingreso_id}")
def eliminar_ingreso(
    ingreso_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_from_token),
) -> dict[str, str]:
    ingreso = (
        db.query(Ingreso)
        .filter(Ingreso.id == ingreso_id, Ingreso.usuario_id == usuario.id)
        .first()
    )
    if not ingreso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingreso no encontrado",
        )
    db.delete(ingreso)
    db.commit()
    return {"status": "ok"}


@router.post("/calcular/boleta", response_model=BoletaResponse)
def calcular_boleta(monto: float) -> dict[str, Any]:
    res: dict[str, Any] = calcular_retencion_boleta(monto)
    return res


@router.get("/proyeccion", response_model=ProyeccionResponse)
def obtener_proyeccion(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_from_token),
) -> dict[str, Any]:
    montos_mensuales = _obtener_montos_mensuales(db, usuario.id)
    if not montos_mensuales:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay ingresos registrados. Agrega al menos uno.",
        )
    res: dict[str, Any] = calcular_proyeccion_anual(montos_mensuales)
    return res


@router.get("/recomendaciones", response_model=list[RecomendacionItem])
def obtener_recomendaciones(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_from_token),
) -> list[dict[str, str]]:
    montos_mensuales = _obtener_montos_mensuales(db, usuario.id)
    if not montos_mensuales:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay ingresos registrados.",
        )
    res: list[dict[str, str]] = calcular_recomendaciones(montos_mensuales)
    return res

