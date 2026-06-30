FROM node:20-alpine

WORKDIR /app

COPY webapp/package.json webapp/package-lock.json* ./
RUN npm install

COPY webapp/ .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
