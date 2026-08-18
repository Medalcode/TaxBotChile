import os
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from app.database import get_db
from app.models import Usuario
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

SECRET_KEY = os.getenv("SECRET_KEY", "taxbot-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer()


def hash_password(password: str) -> str:
    hashed: bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    is_valid: bool = bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    return is_valid


def create_access_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(UTC) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)})
    token: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def get_usuario_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Usuario:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
        usuario_id = int(sub)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        ) from None

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    return usuario
