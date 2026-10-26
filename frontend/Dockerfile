FROM node:22.23.4-alpine

WORKDIR /app

# Copiar package files
COPY package.json package-lock.json* ./
RUN npm install

# Copiar código
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
