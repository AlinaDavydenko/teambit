# Teambit

A real-time collaborative project management application built with FastAPI. Teams can create Kanban boards, manage tasks together in real time, communicate via built-in chat, and get AI assistance — all in one place.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Redis](https://img.shields.io/badge/Redis-latest-red)
![Docker](https://img.shields.io/badge/Docker-compose-blue)
![Tests](https://img.shields.io/badge/Tests-pytest-green)

---

## Features

- **Kanban boards** — create boards, columns, and cards; drag & drop cards between columns
- **Real-time sync** — all changes are instantly visible to every team member via WebSockets
- **Team collaboration** — invite members, assign roles (owner / member), transfer board ownership
- **Live chat** — built-in board chat with online presence indicators
- **AI assistant** — AI bot in chat powered by OpenAI API; answers questions, summarizes board activity, translates messages
- **Background tasks** — async task processing via Celery for email notifications and AI summarization
- **Email verification** — account activation via email code on registration
- **JWT authentication** — secure access/refresh token flow
- **REST API** — fully documented via Swagger UI at `/docs`

---
## Screenshots

![Dashboard](screenshots/dashboard.png)
![Board](screenshots/board.png)
![Chat](screenshots/chat.png)

---
## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.12 |
| Database | PostgreSQL 15, SQLAlchemy, Alembic |
| Cache & Pub/Sub | Redis |
| Real-time | WebSockets |
| Background tasks | Celery |
| AI | OpenAI API (GPT) |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Testing | pytest, pytest-cov, httpx |
| Containerization | Docker, docker-compose |
| CI/CD | GitHub Actions |

---

## Architecture Overview

```
Browser ──HTTP──► FastAPI ──► PostgreSQL
   │                │
   └──WebSocket──►  │ ──► Redis pub/sub ──► All workers
                    │
                    └──► Celery worker ──► OpenAI API
                                       └──► SMTP (email)
```

**Request flow:**
1. REST requests are handled by FastAPI and persisted to PostgreSQL
2. After each mutating action, an event is published to Redis
3. Redis pub/sub delivers the event to all FastAPI workers
4. Each worker broadcasts the event to its connected WebSocket clients
5. Heavy async tasks (AI calls, emails) are offloaded to Celery workers

---

## Project Structure

```
teambit/
├── app/
│   ├── api/
│   │   ├── auth.py          # Registration, login
│   │   ├── boards.py        # Board CRUD, members, messages
│   │   ├── cards.py         # Card CRUD, move
│   │   ├── columns.py       # Column CRUD
│   │   ├── users.py         # User search
│   │   └── websocket.py     # WebSocket endpoint
│   ├── core/
│   │   ├── config.py        # Environment variables
│   │   ├── redis_client.py  # Async Redis client
│   │   └── security.py      # JWT, password hashing
│   ├── db/
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── session.py       # DB session factory
│   ├── services/
│   │   ├── ai_service.py    # OpenAI integration
│   │   └── websocket_manager.py  # Connection manager + Redis pub/sub
│   ├── tasks/
│   │   └── celery_tasks.py  # Background tasks
│   └── main.py
├── tests/
│   ├── integration/
│   │   ├── test_auth.py
│   │   ├── test_boards.py
│   │   ├── test_columns.py
│   │   └── test_cards.py
│   └── conftest.py
├── static/
│   ├── index.html           # Login / Register
│   ├── dashboard.html       # Board list
│   └── board.html           # Kanban board + chat
├── alembic/                 # Database migrations
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Docker and docker-compose installed
- OpenAI API key (for AI features)

### Installation

```bash
git clone https://github.com/AlinaDavydenko/teambit
cd teambit
```

Create a `.env` file in the project root:

```env
# Database
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_NAME=teambit

# Redis
REDIS_PASSWORD=yourredispassword

# JWT
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (for AI features)
OPENAI_API_KEY=your_openai_api_key
```

Generate a secure secret key:

```bash
openssl rand -hex 32
```

### Run

```bash
docker-compose up --build
```

Apply database migrations:

```bash
docker-compose exec web alembic upgrade head
```

The application will be available at:

- **App:** `http://localhost:8000/static/index.html`
- **API docs:** `http://localhost:8000/docs`

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get JWT token |

### Boards
| Method | Endpoint | Description |
|---|---|---|
| GET | `/boards/` | Get all boards for current user |
| POST | `/boards/` | Create a board |
| GET | `/boards/{id}` | Get board by id |
| DELETE | `/boards/{id}` | Delete a board |
| POST | `/boards/{id}/members` | Add a member |
| DELETE | `/boards/{id}/member` | Remove a member |
| PATCH | `/boards/{id}/transfer` | Transfer ownership |
| PATCH | `/boards/{id}/color` | Update board color |
| GET | `/boards/{id}/members` | Get board members |
| GET | `/boards/{id}/messages` | Get chat history |

### Columns
| Method | Endpoint | Description |
|---|---|---|
| POST | `/boards/{id}/columns` | Create a column |
| GET | `/boards/{id}/columns` | Get all columns |
| PATCH | `/boards/{id}/columns/{col_id}` | Rename a column |
| DELETE | `/boards/{id}/columns/{col_id}` | Delete a column |

### Cards
| Method | Endpoint | Description |
|---|---|---|
| POST | `/cards/columns/{col_id}/card` | Create a card |
| GET | `/cards/columns/{col_id}/cards` | Get all cards in column |
| PATCH | `/cards/{id}` | Update a card |
| DELETE | `/cards/{id}` | Delete a card |
| PATCH | `/cards/{id}/move` | Move card to another column |

### WebSocket
| Endpoint | Description |
|---|---|
| `ws://host/ws/boards/{id}?token=...` | Real-time board connection |

**WebSocket events (server → client):**

```json
{ "action": "card_created",          "card": {...} }
{ "action": "card_update",           "card": {...} }
{ "action": "card_moved",            "card": {...} }
{ "action": "card_deleted",          "card_id": 1  }
{ "action": "column_created",        "column": {...} }
{ "action": "column_renamed",        "column": {...} }
{ "action": "column_deleted",        "column_id": 1 }
{ "action": "board_deleted",         "board_id": 1  }
{ "action": "message_added",         "message": {...} }
{ "action": "online_users_updated",  "user_ids": [1, 2] }
```

---

## Running Tests

```bash
docker-compose exec web pytest tests/ -v
```

With coverage report:

```bash
docker-compose exec web pytest tests/ --cov=app --cov-report=term-missing
```

---

## Database Schema

```
users ──────────────────────────────────────────────────┐
  │                                                      │
  ├──► boards (owner_id → users)                        │
  │       │                                              │
  │       ├──► board_members (board_id, user_id, role)  │
  │       ├──► columns (board_id)                       │
  │       │       └──► cards (column_id)                │
  │       │               └──► card_comments            │
  │       │               └──► card_members             │
  │       └──► messages (board_id, user_id, is_ai)      │
  └──────────────────────────────────────────────────────┘
```

---

## License

MIT