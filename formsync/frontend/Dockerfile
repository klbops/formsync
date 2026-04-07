# Usamos a imagem oficial do Node (versão LTS - estável)
FROM node:20-slim

# Definimos a pasta de trabalho
WORKDIR /app

# Copiamos os arquivos de dependências
COPY package*.json ./

# Instalamos as dependências do Vue
RUN npm install

# Copiamos o resto dos arquivos do frontend
COPY . .

# Expomos a porta que o Vite (Vue) usa por padrão
EXPOSE 5173

# Comando para rodar o servidor de desenvolvimento com acesso externo
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]