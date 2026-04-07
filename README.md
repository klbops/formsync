# 📝 FormSync

O **FormSync** é uma aplicação web completa projetada para automatizar e escalar a geração de documentos. Ele sincroniza dados de uma planilha Excel (`.xlsx`, `.xls`) com um modelo do Microsoft Word (`.docx`), gerando automaticamente dezenas ou centenas de documentos personalizados em poucos segundos, empacotados em um arquivo `.zip`.

## 🎯 Utilidade do Projeto

Criar documentos repetitivos (como contratos, certificados, notificações ou recibos) copiando e colando dados de uma planilha para o Word é um processo lento e sujeito a erros humanos. 

O FormSync resolve este problema permitindo que o usuário:
1. Faça o upload de um **Template Word** (usando tags como `{{ Nome }}`, `{{ CPF }}`, etc.).
2. Faça o upload de uma **Planilha Excel** contendo os dados.
3. Pré-visualize e **selecione exatamente quais linhas** deseja processar.
4. Escolha o formato de saída: **Word (.docx)** ou **PDF (.pdf)**.
5. Baixe um único arquivo `.zip` contendo todos os documentos gerados e nomeados com base nos dados.

## 🛠️ Tecnologias Utilizadas

O projeto foi dividido em duas camadas principais (Front-end e Back-end), conteinerizadas para rodar em qualquer ambiente.

### Front-end (Interface do Usuário)
* **[Vue.js 3](https://vuejs.org/):** Framework reativo utilizado para criar a interface de usuário (SPA).
* **[Tailwind CSS](https://tailwindcss.com/):** Framework de CSS utilitário para a estilização ágil e responsiva da página (cores, alinhamentos, barra de progresso).
* **[Axios](https://axios-http.com/):** Cliente HTTP para comunicação com a API e manipulação do download em formato `Blob`.

### Back-end (Motor de Processamento)
* **[Python 3.10+](https://www.python.org/):** Linguagem principal do servidor.
* **[FastAPI](https://fastapi.tiangolo.com/):** Framework web assíncrono e de alta performance para a criação dos endpoints da API (`/api/preview` e `/api/generate`).
* **[Pandas](https://pandas.pydata.org/):** Biblioteca para leitura rápida e manipulação dos dados da planilha Excel na memória.
* **[docxtpl (DocxTemplate)](https://docxtpl.readthedocs.io/):** Motor de renderização que substitui as variáveis do template Word pelos dados do Pandas.
* **[LibreOffice (Headless) + Subprocess](https://www.libreoffice.org/):** Instalado no servidor Linux para converter nativamente os arquivos `.docx` gerados para `.pdf` sem perder a formatação original.

### Infraestrutura
* **[Docker & Docker Compose](https://www.docker.com/):** Para criar ambientes isolados, garantindo que o front-end, o back-end (e o motor do LibreOffice) funcionem da mesma forma na máquina de desenvolvimento e em produção.

---

## ⚙️ Como foi montado (Arquitetura)

O FormSync opera focado em performance, processando a maior parte dos dados diretamente na memória RAM (evitando lentidão com disco rígido):

1. **Pré-visualização (Preview):** Ao inserir a planilha, o Front-end envia o arquivo para a rota `/api/preview`. O Pandas lê o arquivo, extrai apenas os nomes e devolve um JSON. O Front-end monta uma lista interativa onde o usuário pode marcar/desmarcar quem vai ser processado.
2. **Geração em DOCX (Memória RAM):** Ao clicar em "Gerar", os arquivos e a lista de selecionados vão para `/api/generate`. O Python cruza o Template com o Excel. Se a saída for DOCX, o arquivo é gerado em memória (`io.BytesIO`) e inserido diretamente em um buffer ZIP.
3. **Conversão para PDF (Arquivos Temporários):** Se a saída for PDF, o Python cria uma pasta temporária usando `tempfile`. Ele salva o `.docx` provisório, dispara um comando de terminal para o LibreOffice oculto (`libreoffice --headless --convert-to pdf`) e lê o PDF gerado de volta para inserir no ZIP, apagando a pasta em seguida.
4. **Entrega Otimizada:** O Back-end retorna o ZIP final como resposta da requisição. O Front-end, configurado com `responseType: 'blob'`, interpreta os pacotes, exibe uma barra de progresso em tempo real e inicia o download do arquivo `FormSync_Documentos_Gerados.zip` no navegador do usuário.

---

## 🚀 Como rodar o projeto localmente

Como o projeto utiliza Docker, a execução é extremamente simples. Certifique-se de ter o Docker e o Docker Compose instalados na sua máquina.

1. Clone este repositório.
2. Abra o terminal na pasta raiz do projeto.
3. Execute o comando:
   ```bash
   docker compose up --build
