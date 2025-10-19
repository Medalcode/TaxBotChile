from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from app.models import engine, Usuario
from app.schemas import UsuarioCreate, UsuarioResponse, TokenResponse, LoginRequest
from app.services.auth import hash_password, verify_password, create_access_token

SessionLocal = sessionmaker(bind=engine)

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/registro", response_model=UsuarioResponse)
def registrar_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    existente = db.query(Usuario).filter(Usuario.email == payload.email).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado")
    usuario = Usuario(
        email=payload.email,
        nombre=payload.nombre,
        rut=payload.rut,
        hash_password=hash_password(payload.password),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == payload.email).first()
    if not usuario or not verify_password(payload.password, usuario.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token({"sub": str(usuario.id), "email": usuario.email})
    return {"access_token": token}
