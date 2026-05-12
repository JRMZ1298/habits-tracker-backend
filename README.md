# Habit Tracker API

Backend de un rastreador de hábitos con sistema de gamificación (rachas, niveles, insignias), recomendaciones por IA, autenticación JWT y Google OAuth.

## Stack

- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Base de datos**: SQLite (configurable vía `DATABASE_URL`)
- **Migraciones**: Alembic
- **Autenticación**: JWT + bcrypt + Google OAuth
- **Tareas programadas**: APScheduler (recordatorios diarios y resúmenes semanales)
- **Rate limiting**: SlowAPI
- **APIs externas**: OpenRouter (recomendaciones IA), Pexels (imágenes)

## Requisitos

- Python 3.10+

## Instalación

```bash
git clone <repo>
cd 01-habits-tracker-backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración

Copia el archivo de plantilla y completa los valores:

```bash
cp .env.template .env
```

### Variables de entorno

| Variable | Por defecto | Descripción |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./habits.db` | URL de conexión SQLAlchemy |
| `SECRET_KEY` | `cambia_esto_en_produccion` | Clave secreta para firmar JWT |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Expiración del token (24 h) |
| `GOOGLE_CLIENT_ID` | — | ID de cliente de Google OAuth |
| `GOOGLE_CLIENT_SECRET` | — | Secreto de Google OAuth |
| `GOOGLE_REDIRECT_URI` | `http://localhost:8000/auth/google/callback` | URI de redirección OAuth |
| `FRONTEND_URL` | `http://localhost:5173` | URL del frontend (CORS) |
| `SMTP_HOST` | `smtp.gmail.com` | Servidor SMTP |
| `SMTP_PORT` | `587` | Puerto SMTP |
| `SMTP_USER` | — | Usuario SMTP |
| `SMTP_PASS` | — | Contraseña SMTP |
| `PEXELS_API_KEY` | — | API key de Pexels |
| `OPENROUTER_API_KEY` | — | API key de OpenRouter |

## Ejecución

```bash
uvicorn app.main:app --reload
```

La API se levanta en `http://localhost:8000`. La documentación interactiva está en `/docs` (Swagger) y `/redoc` (ReDoc).

En el arranque, la aplicación ejecuta automáticamente las migraciones pendientes de Alembic y siembra las insignias predefinidas.

## Estructura del proyecto

```
├── app/
│   ├── main.py                  # Punto de entrada FastAPI
│   ├── database.py              # Motor SQLAlchemy y sesión
│   ├── models.py                # Modelos ORM (User, Habit, HabitLog, Badge, UserBadge)
│   ├── seeds.py                 # Datos iniciales de insignias
│   ├── scheduler.py             # Tareas programadas (APScheduler)
│   ├── core/
│   │   ├── config.py            # Configuración con Pydantic Settings
│   │   └── limiter.py           # Rate limiter
│   ├── schemas/                 # Pydantic models (user, habit, badge, notification)
│   ├── routers/                 # Endpoints (auth, habits, logs, stats, badges, notifications, users, recomendations)
│   └── services/                # Lógica de negocio (auth, badges, email, streak)
├── alembic/                     # Migraciones de base de datos
├── .env.template                # Plantilla de variables de entorno
├── requirements.txt
└── alembic.ini
```

## Endpoints

### Auth (`/auth`)
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/auth/register` | Registrar usuario (`email`, `name`, `password`) |
| POST | `/auth/login` | Iniciar sesión (OAuth2 form) → JWT |
| GET | `/auth/google` | Redirige a Google OAuth |
| GET | `/auth/google/callback` | Callback de Google OAuth → JWT |

### Habits (`/habits`)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/habits/` | Listar hábitos del usuario (paginado) |
| POST | `/habits/` | Crear hábito |
| GET | `/habits/{id}` | Obtener hábito |
| PUT | `/habits/{id}` | Actualizar hábito |
| DELETE | `/habits/{id}` | Eliminar hábito |

### Logs (`/habits/{habit_id}/logs`)
| Método | Ruta | Descripción |
|---|---|---|
| POST | `.../logs/` | Registrar progreso del día |
| GET | `.../logs/stats` | Estadísticas del hábito (racha actual, mejor racha, total) |
| GET | `.../logs/today` | Verificar si ya se registró hoy/esta semana |

### Stats (`/stats`)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/stats/weekly` | Completados por día de la semana actual |
| GET | `/stats/today-count` | Total completados hoy |
| GET | `/stats/profile` | Nivel, progreso, rachas y completados totales |
| GET | `/stats/yearly` | Completados por mes del año actual |
| GET | `/stats/habit/{id}/period-progress` | Barras de progreso del período |

### Badges (`/badges`)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/badges/` | Listar insignias con estado del usuario |
| GET | `/badges/progress` | Racha máxima actual por categoría/icono |

### Recommendations (`/recommendation`)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/recommendation` | Recomendación IA de hábito con imagen (10 req/min) |

### Notifications (`/notifications`)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/notifications/me/notifications` | Preferencias de notificación |
| PUT | `/notifications/me/notifications` | Actualizar preferencias |

### Users (`/users`)
| Método | Ruta | Descripción |
|---|---|---|
| PUT | `/users/me` | Actualizar perfil |
| POST | `/users/refresh` | Refrescar JWT |

Todos los endpoints excepto `/auth/register`, `/auth/login`, `/auth/google` y `/auth/google/callback` requieren autenticación vía `Authorization: Bearer <token>`.

## Gamificación

- **Niveles**: cada nivel N requiere `N × 5` hábitos completados.
- **Insignias**: 24 insignias en 8 categorías (salud, running, meditación, ejercicio, agua, lectura, nutrición, sueño) que se desbloquean al alcanzar rachas de 5, 15 y 30 días.
- **Rachas**: cálculo automático del historial de completados día a día.

## Tareas programadas

- **Diario (8:00 AM)**: envía recordatorio por email de hábitos no completados.
- **Semanal (lunes 9:00 AM)**: envía resumen semanal con estadísticas, nivel, rachas y gráfico de barras de completados diarios.

## Licencia

MIT
