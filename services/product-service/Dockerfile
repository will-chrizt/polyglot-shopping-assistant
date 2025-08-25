FROM node:20-alpine
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm ci --omit=dev
COPY src ./src
ENV PORT=8001
EXPOSE 8001
CMD ["npm", "start"]
