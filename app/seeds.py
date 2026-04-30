from app.database import SessionLocal
from app.models import Badge

BADGES = [
        # Salud Badges
    {
"key":"health_5_days",
"name":"Healthy Start",
"icon":"favorite",
"description":"5 días cuidando tu salud",
"required_streak":5,
"category":"favorite"
},
{
"key":"health_15_days",
"name":"Vital Pulse",
"icon":"favorite",
"description":"15 días manteniendo hábitos saludables",
"required_streak":15,
"category":"favorite"
},
{
"key":"health_30_days",
"name":"Heart Champion",
"icon":"favorite",
"description":"30 días de constancia en salud",
"required_streak":30,
"category":"favorite"
},
# Correr
{
"key":"run_5_days",
"name":"First Stride",
"icon":"directions_run",
"description":"5 días corriendo",
"required_streak":5,
"category":"directions_run"
},
{
"key":"run_15_days",
"name":"Speed Seeker",
"icon":"directions_run",
"description":"15 días de cardio continuo",
"required_streak":15,
"category":"directions_run"
},
{
"key":"run_30_days",
"name":"Marathon Mind",
"icon":"directions_run",
"description":"30 días en movimiento",
"required_streak":30,
"category":"directions_run"
},
# Meditar
{
"key":"mind_5_days",
"name":"Inner Calm",
"icon":"self_improvement",
"description":"5 días practicando mindfulness",
"required_streak":5,
"category":"self_improvement"
},
{
"key":"mind_15_days",
"name":"Zen Flow",
"icon":"self_improvement",
"description":"15 días de enfoque mental",
"required_streak":15,
"category":"self_improvement"
},
{
"key":"mind_30_days",
"name":"Enlightened",
"icon":"self_improvement",
"description":"30 días cultivando tu mente",
"required_streak":30,
"category":"self_improvement"
},
# Ejercicio
{
"key":"exercise_5_days",
"name":"Iron Rookie",
"icon":"exercise",
"description":"5 días entrenando",
"required_streak":5,
"category":"exercise"
},
{
"key":"exercise_15_days",
"name":"Strength Builder",
"icon":"exercise",
"description":"15 días fortaleciendo tu disciplina",
"required_streak":15,
"category":"exercise"
},
{
"key":"exercise_30_days",
"name":"Titan Mode",
"icon":"exercise",
"description":"30 días sin romper la racha",
"required_streak":30,
"category":"exercise"
},
# Agua
{
"key":"water_5_days",
"name":"Fluid Flow",
"icon":"water_drop",
"description":"5 días tomando agua",
"required_streak":5,
"category":"water_drop"
},
{
"key":"water_15_days",
"name":"Hydration Hero",
"icon":"water_drop",
"description":"15 días hidratándote",
"required_streak":15,
"category":"water_drop"
},
{
"key":"water_30_days",
"name":"Ocean Discipline",
"icon":"water_drop",
"description":"30 días de hidratación constante",
"required_streak":30,
"category":"water_drop"
},
# Lectura
{
"key":"reading_5_days",
"name":"Page Turner",
"icon":"menu_book",
"description":"5 días leyendo",
"required_streak":5,
"category":"menu_book"
},
{
"key":"reading_15_days",
"name":"Knowledge Hunter",
"icon":"menu_book",
"description":"15 días aprendiendo",
"required_streak":15,
"category":"menu_book"
},
{
"key":"reading_30_days",
"name":"Wisdom Keeper",
"icon":"menu_book",
"description":"30 días de lectura constante",
"required_streak":30,
"category":"menu_book"
},
# Nutricion
{
"key":"food_5_days",
"name":"Clean Plate",
"icon":"fork_spoon",
"description":"5 días comiendo mejor",
"required_streak":5,
"category":"fork_spoon"
},
{
"key":"food_15_days",
"name":"Nutrition Ninja",
"icon":"fork_spoon",
"description":"15 días cuidando tu alimentación",
"required_streak":15,
"category":"fork_spoon"
},
{
"key":"food_30_days",
"name":"Fuel Master",
"icon":"fork_spoon",
"description":"30 días de nutrición consciente",
"required_streak":30,
"category":"fork_spoon"
},
# Sleep
    ]

def seed_badges():
    db = SessionLocal()
    try:
        for data in BADGES:
            exists = db.query(Badge).filter(Badge.key == data["key"]).first()
            if not exists:
                db.add(Badge(**data))
        db.commit()
        # print(f"Badges seeded: {len(BADGES)}")
    finally:
        db.close()