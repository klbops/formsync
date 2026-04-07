#!/bin/bash

echo "🚀 Iniciando a criação da estrutura do projeto FormSync..."

# Cria a pasta raiz e entra nela
mkdir -p formsync
cd formsync

# 1. Arquivos da raiz
echo "Criando arquivos de configuração root..."
touch .gitignore docker-compose.yml .env.example

# 2. Infraestrutura (Nginx)
echo "Criando diretórios do Nginx..."
mkdir -p nginx
touch nginx/nginx.conf

# 3. Frontend (React/Vue)
echo "Criando estrutura do Frontend..."
mkdir -p frontend/public
mkdir -p frontend/src/components frontend/src/pages frontend/src/services
touch frontend/Dockerfile frontend/package.json
touch frontend/public/index.html frontend/src/App.js

# 4. Backend (Python/FastAPI)
echo "Criando estrutura do Backend..."
mkdir -p backend/core backend/api backend/models backend/services backend/utils
touch backend/Dockerfile backend/requirements.txt backend/main.py

# Criando arquivos __init__.py para o Python reconhecer as pastas como módulos
touch backend/core/__init__.py backend/api/__init__.py backend/models/__init__.py backend/services/__init__.py backend/utils/__init__.py

# 5. Storage (Volumes do Docker)
echo "Criando diretórios de armazenamento..."
mkdir -p storage/templates storage/outputs

echo "✅ Estrutura criada com sucesso! O terreno do FormSync está pronto."
