import pandas as pd
from docxtpl import DocxTemplate
import io
import zipfile
import re
import os
import tempfile
import subprocess

def process_documents(template_bytes, spreadsheet_bytes, format_type="docx", selected_rows=None):
    try:
        print(f"\n--- 🚀 INICIANDO MOTOR DE GERAÇÃO (Formato: {format_type.upper()}) ---")
        
        # Lê a planilha
        df = pd.read_excel(io.BytesIO(spreadsheet_bytes))
        
        # Filtra as linhas
        if selected_rows is not None and len(selected_rows) > 0:
            indices = [int(i) for i in selected_rows]
            df = df.iloc[indices]

        if df.empty:
            raise ValueError("Nenhuma linha para processar após o filtro.")

        zip_buffer = io.BytesIO()
        arquivos_colocados_no_zip = 0
        
        # Criamos um diretório temporário no disco (necessário para o conversor de PDF)
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for idx, row in df.iterrows():
                    try:
                        # Renderiza o documento Word normalmente
                        doc = DocxTemplate(io.BytesIO(template_bytes))
                        context = {str(k): (str(v) if pd.notna(v) else "") for k, v in row.to_dict().items()}
                        doc.render(context)
                        
                        # Define o nome base limpo
                        nome_base = context.get("NOME") or context.get("Nome") or f"doc_{idx+1}"
                        nome_limpo = re.sub(r'[\\/*?:"<>|]', "", str(nome_base)).strip()
                        
                        # --- LÓGICA DE ESCOLHA: DOCX OU PDF ---
                        if format_type.lower() == "pdf":
                            # Caminhos dos arquivos na pasta temporária
                            docx_path = os.path.join(temp_dir, f"{nome_limpo}.docx")
                            pdf_path = os.path.join(temp_dir, f"{nome_limpo}.pdf")
                            
                            # 1. Salva o DOCX no disco
                            doc.save(docx_path)
                            
                            # 2. Executa o LibreOffice invisível (headless) para converter
                            subprocess.run([
                                "libreoffice", "--headless", "--convert-to", "pdf", 
                                "--outdir", temp_dir, docx_path
                            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
                            
                            # 3. Lê o PDF gerado
                            if os.path.exists(pdf_path):
                                with open(pdf_path, "rb") as f:
                                    bytes_finais = f.read()
                                nome_final = f"{nome_limpo}.pdf"
                            else:
                                raise FileNotFoundError("Falha na conversão para PDF.")
                                
                        else:
                            # Se for DOCX, fazemos tudo na memória RAM (mais rápido)
                            doc_io = io.BytesIO()
                            doc.save(doc_io)
                            bytes_finais = doc_io.getvalue()
                            nome_final = f"{nome_limpo}.docx"

                        # Adiciona o arquivo (PDF ou DOCX) ao ZIP
                        if len(bytes_finais) > 0:
                            zf.writestr(nome_final, bytes_finais)
                            arquivos_colocados_no_zip += 1
                            print(f"✅ Sucesso: {nome_final} adicionado ao ZIP.")
                        else:
                            print(f"❌ Erro: {nome_final} ficou vazio (0 bytes).")

                    except Exception as erro_da_linha:
                        print(f"❌ Erro na linha {idx}: {erro_da_linha}")

        print(f"📦 FINALIZADO! Total de {arquivos_colocados_no_zip} arquivos em {format_type.upper()} gerados.")
        return zip_buffer.getvalue()

    except Exception as e:
        print(f"🔥 ERRO NO GENERATOR: {str(e)}")
        raise e