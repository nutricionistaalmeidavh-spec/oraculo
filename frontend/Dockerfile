FROM node:20-alpine

WORKDIR /app

# Copiar package files
COPY package.json package-lock.json* ./
RUN npm install

# Copiar código
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
