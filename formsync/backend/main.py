from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import json
import pandas as pd
import traceback

from core.database import engine
from models import models
from services.generator import process_documents

# Inicializa as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FormSync API", description="Motor de geração de documentos")

# Configuração de CORS para o Vue.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "🚀 FormSync API online!"}

# --- ROTA DE PREVIEW ---
@app.post("/api/preview")
async def preview_spreadsheet(spreadsheet: UploadFile = File(...)):
    try:
        content = await spreadsheet.read()
        df = pd.read_excel(io.BytesIO(content))
        
        # Procura coluna NOME de forma insensível a maiúsculas
        nome_col = next((col for col in df.columns if str(col).strip().upper() == 'NOME'), None)
        
        preview_data = []
        for idx, row in df.iterrows():
            nome = row[nome_col] if nome_col and pd.notna(row[nome_col]) else f"Linha {idx + 1}"
            preview_data.append({"index": idx, "nome": str(nome)})
            
        return {"rows": preview_data}
    except Exception as e:
        print(f"❌ Erro no Preview: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro ao ler planilha: {str(e)}")

# --- ROTA DE PROGRESSO (Evita o 404 no Front-end) ---
@app.post("/api/generate-progress")
async def generate_progress():
    # Retorna status fixo enquanto o arquivo principal é processado
    return {"progress": 100, "status": "Processando arquivos..."}

# --- ROTA DE GERAÇÃO ---
@app.post("/api/generate")
async def generate_docs(
    template: UploadFile = File(...),
    spreadsheet: UploadFile = File(...),
    format_type: str = Form("docx"),
    selected_rows: str = Form(None)
):
    print(f"📦 Arquivo: {template.filename} | Formato: {format_type.upper()}")

    try:
        # Tratamento seguro para a lista de linhas selecionadas
        rows_to_process = None
        if selected_rows and selected_rows not in ["undefined", "null", "[]", ""]:
            try:
                rows_to_process = json.loads(selected_rows)
                print(f"🎯 Filtrando {len(rows_to_process)} linhas.")
            except Exception as e:
                print(f"⚠️ Erro ao converter JSON de linhas: {e}")

        # Lendo os arquivos em bytes
        template_bytes = await template.read()
        spreadsheet_bytes = await spreadsheet.read()

        # Chamada ao serviço de geração
        zip_bytes = process_documents(
            template_bytes, 
            spreadsheet_bytes, 
            format_type, 
            rows_to_process
        )

        # --- TRAVA DE SEGURANÇA E VERIFICAÇÃO DE TAMANHO ---
        tamanho_zip = len(zip_bytes)
        print(f"✅ Motor finalizou! Tamanho do ZIP gerado: {tamanho_zip} bytes")

        # Se o ZIP tiver menos de 100 bytes, ele está vazio/corrompido.
        if tamanho_zip < 100:
            print("❌ ERRO: O generator devolveu um ZIP vazio!")
            raise HTTPException(
                status_code=500, 
                detail="O motor falhou ao gerar os documentos. Verifique as tags do template e os dados da planilha."
            )

        # Criando o stream a partir dos bytes gerados
        stream_final = io.BytesIO(zip_bytes)
        
        # GARANTIA: Rebobinar o stream para o FastAPI ler desde o começo!
        stream_final.seek(0)

        return StreamingResponse(
            stream_final,
            media_type="application/x-zip-compressed", # Tipo MIME compatível
            headers={
                "Content-Disposition": f"attachment; filename=documentos_gerados.zip",
                "Access-Control-Expose-Headers": "Content-Disposition",
                "Content-Length": str(tamanho_zip) # <-- Diz ao navegador o tamanho exato!
            }
        )

    except HTTPException as http_exc:
        # Repassa o erro 500 proposital se o ZIP estiver vazio
        raise http_exc
    except Exception as e:
        # Log detalhado do erro crítico no terminal do Docker
        error_msg = traceback.format_exc()
        print(f"🔥 ERRO NA GERAÇÃO:\n{error_msg}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar documentos: {str(e)}")