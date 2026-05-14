# Habits Tracker Backend

API backend para una aplicación de seguimiento de hábitos con gamificación, recomendaciones por IA y notificaciones por email.

## Stack

- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **Auth:** JWT (python-jose) + bcrypt + Google OAuth
- **Cache:** Redis (opcional, fallback en memoria)
- **AI:** OpenRouter.ai + Pexels API
- **Migrations:** Alembic

## Requisitos

- Python 3.11+
- (Opcional) Docker + Docker Compose

## Inicio rápido

```bash
# Clonar e instalar
pip install -r requirements.txt

# Copiar y configurar variables de entorno
cp .env.template .env

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

## API Endpoints

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Registrar usuario |
| POST | `/auth/login` | No | Iniciar sesión |
| POST | `/auth/logout` | Sí | Cerrar sesión |
| GET | `/auth/google` | No | Login con Google |
| GET | `/auth/google/callback` | No | Callback Google OAuth |
| POST | `/habits/` | Sí | Crear hábito |
| GET | `/habits/` | Sí | Listar hábitos |
| GET | `/habits/{id}` | Sí | Obtener hábito |
| PUT | `/habits/{id}` | Sí | Actualizar hábito |
| DELETE | `/habits/{id}` | Sí | Eliminar hábito |
| POST | `/habits/{id}/logs` | Sí | Registrar progreso |
| GET | `/habits/{id}/logs/stats` | Sí | Estadísticas |
| GET | `/habits/{id}/logs/today` | Sí | Progreso hoy |
| GET | `/stats/weekly` | Sí | Resumen semanal |
| GET | `/stats/today-count` | Sí | Conteo hoy |
| GET | `/stats/profile` | Sí | Perfil y nivel |
| GET | `/stats/yearly` | Sí | Resumen anual |
| GET | `/stats/habit/{id}/period-progress` | Sí | Progreso por período |
| GET | `/badges/` | Sí | Insignias |
| GET | `/badges/progress` | Sí | Progreso insignias |
| GET | `/recommendation` | No | Recomendación IA |
| PUT | `/notifications/me/notifications` | Sí | Preferencias |
| GET | `/notifications/me/notifications` | Sí | Ver preferencias |
| PUT | `/users/me` | Sí | Actualizar perfil |
| POST | `/users/refresh` | Sí | Refrescar token |

## Variables de Entorno

Ver `.env.template` para la lista completa.

## Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest tests/ -v
```

## Migraciones

```bash
# Crear migración
alembic revision --autogenerate -m "descripción"

# Aplicar
alembic upgrade head

# Revertir
alembic downgrade -1
```
