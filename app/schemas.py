from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any

# Precios del día
class MarketPricesResponse(BaseModel):
    cacao_international: float
    cafe_international: float
    cacao_local: float
    cafe_local: float
    last_updated: str
    price_history: Dict[str, Any]
    dates: List[str]

# Artículos de Blog
class BlogPost(BaseModel):
    id: int
    locale: str
    title: str
    summary: str
    content: str
    cover_image: str
    secondary_image: Optional[str] = None
    author: str
    date: str
    category: str

class BlogPostCreate(BaseModel):
    locale: str
    title: str
    summary: str
    content: str
    cover_image: str
    secondary_image: Optional[str] = None
    author: str
    category: str

# Requerimientos B2B (Demandas)
class DemandPublic(BaseModel):
    id: int
    country: str
    country_code: str
    product: str
    product_en: str
    quantity_tons: float
    target_price: str
    destination_port: str
    destination_port_en: str
    date_posted: str
    is_verified: bool

class DemandCreate(BaseModel):
    company_name: str
    company_tax_id: str
    contact_email: EmailStr
    country: str
    country_code: str
    product: str
    product_en: str
    quantity_tons: float
    target_price: str
    destination_port: str
    destination_port_en: str

# Trazabilidad
class SoilMetrics(BaseModel):
    ph: float
    organic_matter: str
    organic_matter_en: str
    type: str
    type_en: str

class WaterMetrics(BaseModel):
    source: str
    source_en: str
    purity_level: str
    irrigation_type: str
    irrigation_type_en: str

class TraceabilityLot(BaseModel):
    lot_code: str
    product: str
    product_en: str
    cooperative: str
    cooperative_en: str
    region: str
    harvest_date: str
    packing_date: str
    soil_metrics: SoilMetrics
    water_metrics: WaterMetrics
    destination_port: str
    destination_port_en: str
    shipment_date: str
    status: str
    status_en: str

# Autenticación
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class UserProfile(BaseModel):
    email: EmailStr
    name: str
    name_en: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile

# Formulario de Contacto
class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    country: str
    product_interest: str
    volume_tons: Optional[float] = None
    message: str

# Puertos Logística
class PortLogistics(BaseModel):
    port: str
    port_en: str
    transit_days: int
    temperature_c: float
    humidity_pct: int
    ventilation_cbm: int

# Cosechas y Entregas (Flujo Productor -> Admin)
class HarvestCreate(BaseModel):
    product: str
    weight_kg: float
    proposed_price_pen_kg: Optional[float] = None
    location: Optional[str] = "No especificada"

class HarvestDelivery(BaseModel):
    id: int
    date: str
    product: str
    weight_kg: float
    proposed_price_pen_kg: Optional[float] = None
    location: str
    status: str
    price_paid_pen: float
    producer_name: str
    producer_email: EmailStr

class HarvestActionRequest(BaseModel):
    action: str  # 'negotiate', 'agree_price', 'complete'
    price_pen_kg: Optional[float] = None

class DirectPurchaseCreate(BaseModel):
    producer_name: str
    product: str
    weight_kg: float
    price_paid_pen_kg: float
    location: Optional[str] = "No especificada"
    humedad_pct: Optional[float] = None
    comprador: Optional[str] = None
    precio_venta_pactado_skg: Optional[float] = None
