FROM node:22

# Рабочая директория внутри контейнера

WORKDIR /app

# Копируем package.json и package-lock.json чтобы npm install не делал лишнюю работу каждый раз

COPY my-frontend/package*.json ./

# Устанавливаем все зависимости

RUN npm install

# Копируем весь проект

COPY my-frontend/ .

# Собираем проект (можно dev для разработки)

CMD ["npm", "run", "dev"]
