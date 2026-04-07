# Usamos uma versão leve do Python
FROM python:3.11-slim

# Definimos a pasta de trabalho dentro do container
WORKDIR /app

# Atualiza o sistema e instala o LibreOffice (necessário para converter DOCX em PDF)
RUN apt-get update && apt-get install -y libreoffice --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copiamos as dependências e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos o restante do código
COPY . .

# Comando para rodar o servidor FastAPI com live-reload ativo
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]