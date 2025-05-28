
# Foodgram

## Описание проекта

**Foodgram** — это веб-приложение для публикации, просмотра и добавления кулинарных рецептов. Пользователи могут создавать собственные рецепты, добавлять ингредиенты, подписываться на авторов и формировать список покупок.

---

## Сайт проекта

**URL проекта:** [Foodgram](http://51.250.99.160:8001)

## Инструкция по запуску

### 1. Клонируйте репозиторий

```bash
git clone git@github.com:Guram-Gurych/foodgram.git
cd foodgram
````

### 2. Подготовьте `.env` файл

Создайте `.env` в корне проекта и укажите:

```env
POSTGRES_USER=foodgram_admin
POSTGRES_PASSWORD=mysecretpasswordadmin
POSTGRES_DB=foodgram

DB_HOST=db
DB_PORT=5432

SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS="localhost,127.0.0.1,your_domain"
```

### 3. Подготовьте сервер

```bash
mkdir -p ~/foodgram
```

### 4. Укажите переменные окружения в GitHub Actions

**Settings → Secrets and variables → Actions:**

```
HOST — IP-адрес сервера
USER — имя пользователя
SSH_KEY — приватный SSH-ключ
SSH_PASSPHRASE — пароль к ключу
DOCKER_USERNAME — логин DockerHub
DOCKER_PASSWORD — пароль DockerHub
TELEGRAM_TO — ID чата
TELEGRAM_TOKEN — токен бота Telegram
```

### 5. Запушьте проект в GitHub

CI/CD GitHub Actions автоматически развернёт проект на сервере.

---

## Примеры API-запросов

### Список рецептов

```http
GET /api/recipes/
```

### Создание рецепта

```http
POST /api/recipes/
```

**Request:**

```json
{
  "name": "Паста с соусом",
  "text": "Пошаговое описание рецепта...",
  "cooking_time": 25,
  "ingredients": [
    { "id": 1, "amount": 200 },
    { "id": 2, "amount": 3 }
  ],
  "tags": [1, 2],
  "image": "base64..."
}
```

---

### Получить список ингредиентов

```http
GET /api/ingredients/
```

---

### Подписаться на пользователя

```http
POST /api/users/{id}/subscribe/
```

---

### Создать токен

```http
POST /api/token/login/
```

**Request:**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**

```json
{
  "auth_token": "your_token_here"
}
```

---

## Используемые технологии

![Python](https://img.shields.io/badge/Python-3.9-blue)
![Django](https://img.shields.io/badge/Django-3.2.3-green)
![Django REST Framework](https://img.shields.io/badge/DRF-3.12.4-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13.3-purple)
![Gunicorn](https://img.shields.io/badge/Gunicorn-20.1.0-lightgreen)
![Nginx](https://img.shields.io/badge/Nginx-1.21-red)
![Docker](https://img.shields.io/badge/Docker-20.10-blueviolet)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2.0-yellowgreen)

---

## Автор

Проект разработал: [Бледных Кирилл](https://github.com/Guram-Gurych)
