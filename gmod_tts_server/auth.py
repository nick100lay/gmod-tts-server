

from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import SECRET_KEY


auth_scheme = HTTPBearer(auto_error=False)
async def authorization_dep(token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)]) -> str:
    if not SECRET_KEY:
        return ""
    ex = HTTPException(status_code=401, detail="Unauthorized")
    if token is None:
        raise ex
    secret_key = token.credentials
    secret_key = secret_key.strip()
    if secret_key != SECRET_KEY:
        raise ex
    return secret_key

AuthDep = Annotated[str, Depends(authorization_dep)]