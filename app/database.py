import datetime
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Valor centinela: si SECRET_KEY sigue siendo esto en producción, algo está mal.
DEV_SECRET_KEY = "dev-insecure-not-for-production"

# Contraseñas semilla que NO se permiten en producción (defaults de desarrollo
# y valores triviales conocidos).
WEAK_SEED_PASSWORDS = frozenset({
    "", "admin123", "productor123", "comprador123",
    "changeme", "password", "123456", "secret",
})

# Configuración de variables de entorno usando pydantic-settings
class Settings(BaseSettings):
    # Entorno de ejecución. En "production" se aplican validaciones estrictas
    # (SECRET_KEY obligatoria, contraseñas semilla fuertes, CORS sin regex de dev).
    APP_ENV: str = "development"

    # La variable DATABASE_URL se lee automáticamente de .env o del entorno real (Railway)
    # Hacemos fallback a SQLite local si no está configurada
    DATABASE_URL: str = "sqlite:///./sql_app.db"

    # Clave para firmar los JWT. OBLIGATORIO setearla en producción (Railway).
    SECRET_KEY: str = DEV_SECRET_KEY

    # Orígenes permitidos para CORS, separados por coma.
    # Ej: "https://waritradingfoods.com,https://www.waritradingfoods.com"
    # En local siempre se permiten localhost / ngrok / localtunnel (ver main.py).
    CORS_ORIGINS: str = ""

    # Contraseñas de los usuarios semilla. En producción setear valores reales;
    # los defaults son solo para desarrollo local.
    SEED_ADMIN_PASSWORD: str = "admin123"
    SEED_PRODUCTOR_PASSWORD: str = "productor123"
    SEED_COMPRADOR_PASSWORD: str = "comprador123"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.strip().lower() in {"production", "prod"}


settings = Settings()


def assert_production_config() -> None:
    """Falla rápido si la app arranca en producción con configuración insegura.

    Se invoca al importar main.py. No valida las contraseñas semilla aquí porque
    solo importan al sembrar una BD vacía (ver `seed.py`).
    """
    if not settings.is_production:
        return

    problems = []
    if settings.SECRET_KEY == DEV_SECRET_KEY or len(settings.SECRET_KEY) < 32:
        problems.append(
            "SECRET_KEY no está configurada o es demasiado corta. Generá una con:\n"
            '  python -c "import secrets; print(secrets.token_urlsafe(48))"'
        )
    if not settings.cors_origins_list:
        problems.append(
            "CORS_ORIGINS está vacío. Listá los dominios del frontend separados por coma."
        )

    if problems:
        raise RuntimeError(
            "Configuración de producción insegura (APP_ENV=production):\n- "
            + "\n- ".join(problems)
        )

# Corregir URL si es del formato postgres:// (que Railway entrega y SQLAlchemy v2+ rechaza)
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Configurar motor de base de datos
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para obtener la sesión en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# MANTENER SIMULACIÓN DE TICKER DE PRECIOS PARA COMPATIBILIDAD TEMPORAL
# ==============================================================================

MARKET_PRICES = {
    "cacao_international": 5150.00,  # USD por tonelada métrica (~US$5,150/t)
    "cafe_international": 3.42,      # USD por libra (lb) (~342 ¢/lb)
    "cacao_local": 13.91,            # PEN por kilogramo (Soles)
    "cafe_local": 15.82,             # PEN por kilogramo (Soles)
    "last_updated": datetime.datetime.now().isoformat()
}

PRICE_HISTORY = {
    "cacao": [5050, 5080, 5100, 5090, 5120, 5150],
    "cafe": [3.10, 3.18, 3.25, 3.30, 3.38, 3.42],
    "dates": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
}

def update_prices_simulation(force: bool = False):
    import random
    import datetime
    
    try:
        last_up = datetime.datetime.fromisoformat(MARKET_PRICES["last_updated"])
    except Exception:
        last_up = datetime.datetime.now() - datetime.timedelta(hours=5)
        
    now = datetime.datetime.now()
    diff = now - last_up
    
    if force or diff.total_seconds() >= 4 * 3600:
        try:
            import yfinance as yf
            tickers = yf.Tickers('KC=F CC=F')
            price_cafe_centavos = tickers.tickers['KC=F'].fast_info['lastPrice']
            price_cacao_usd = tickers.tickers['CC=F'].fast_info['lastPrice']
            
            if price_cafe_centavos and price_cacao_usd:
                MARKET_PRICES["cafe_international"] = round(float(price_cafe_centavos) / 100, 2)
                MARKET_PRICES["cacao_international"] = round(float(price_cacao_usd), 2)
                
                # Recalcular precios locales matemáticamente alineados con la estrategia
                tc_ref = 3.40
                cafe_intl = MARKET_PRICES["cafe_international"]
                cacao_intl = MARKET_PRICES["cacao_international"]
                
                cafe_max = (cafe_intl * 2.2046 * tc_ref) * 0.73 - 1.15 - 0.75
                cacao_conv_max = (cacao_intl / 1000 * tc_ref) * 0.90 - 0.95 - 0.90
                
                MARKET_PRICES["cafe_local"] = round(cafe_max, 2)
                MARKET_PRICES["cacao_local"] = round(cacao_conv_max, 2)
                MARKET_PRICES["last_updated"] = now.isoformat()
                return
        except Exception:
            pass
            
        # Fallback: Simulación si falla la red o API
        MARKET_PRICES["cacao_international"] = round(MARKET_PRICES["cacao_international"] * random.uniform(0.99, 1.01), 2)
        MARKET_PRICES["cafe_international"] = round(MARKET_PRICES["cafe_international"] * random.uniform(0.99, 1.01), 2)
        
        tc_ref = 3.40
        cafe_intl = MARKET_PRICES["cafe_international"]
        cacao_intl = MARKET_PRICES["cacao_international"]
        
        cafe_max = (cafe_intl * 2.2046 * tc_ref) * 0.73 - 1.15 - 0.75
        cacao_conv_max = (cacao_intl / 1000 * tc_ref) * 0.90 - 0.95 - 0.90
        
        MARKET_PRICES["cafe_local"] = round(cafe_max, 2)
        MARKET_PRICES["cacao_local"] = round(cacao_conv_max, 2)
        MARKET_PRICES["last_updated"] = now.isoformat()
