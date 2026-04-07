from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

# Importações do seu projeto
from core.database import SessionLocal
from core.security import SECRET_KEY, ALGORITHM
from models.models import User

# Informa ao FastAPI qual é a rota que gera o token de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# Função para abrir e fechar a conexão com o banco de dados a cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# O nosso Porteiro Digital
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    # Mensagem padrão caso o token seja inválido ou o usuário não exista
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Tenta abrir o token digital
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Pega o email (que salvamos no campo 'sub' do token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Vai no banco de dados conferir se o usuário dono do token ainda existe
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
        
    # Se deu tudo certo, devolve os dados do usuário logado
    return user
