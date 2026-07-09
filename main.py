import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from app.database import (
    MARKET_PRICES, PRICE_HISTORY, BLOG_POSTS, DEMANDS, LOTS, USERS, PORTS_DATA,
    HARVEST_DELIVERIES, update_prices_simulation
)
from app.schemas import (
    MarketPricesResponse, BlogPost, BlogPostCreate, DemandPublic, DemandCreate,
    TraceabilityLot, LoginRequest, TokenResponse, ContactRequest, PortLogistics,
    HarvestCreate, HarvestDelivery, HarvestActionRequest
)
from app.auth import create_access_token, get_current_user, check_role

app = FastAPI(
    title="Wari Trading API",
    description="API para el Portal y PWA de la empresa agroexportadora Wari Trading S.A.C.",
    version="1.0.0"
)

# Configuración de CORS para permitir solicitudes desde el frontend de Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|.*\.ngrok-free\.app|.*\.ngrok\.app|.*\.localtunnel\.me)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacén en memoria para mensajes de contacto recibidos
RECEIVED_CONTACTS = []

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Wari Trading S.A.C."}

# 1. Precios del Mercado (Ticker)
@app.get("/api/market-prices", response_model=MarketPricesResponse)
def get_market_prices():
    # Simular cambios dinámicos en los precios como si se actualizara dos veces al día
    update_prices_simulation()
    return {
        "cacao_international": MARKET_PRICES["cacao_international"],
        "cafe_international": MARKET_PRICES["cafe_international"],
        "cacao_local": MARKET_PRICES["cacao_local"],
        "cafe_local": MARKET_PRICES["cafe_local"],
        "last_updated": MARKET_PRICES["last_updated"],
        "price_history": PRICE_HISTORY,
        "dates": PRICE_HISTORY["dates"]
    }

# 2. Blog / Noticias
@app.get("/api/blog", response_model=List[BlogPost])
def get_blog_posts(locale: str = "es"):
    posts = [p for p in BLOG_POSTS if p["locale"] == locale]
    return posts

@app.get("/api/blog/{post_id}", response_model=BlogPost)
def get_blog_post(post_id: int, locale: str = "es"):
    for post in BLOG_POSTS:
        if post["id"] == post_id and post["locale"] == locale:
            return post
    raise HTTPException(status_code=404, detail="Blog post no encontrado o idioma no disponible")

@app.post("/api/blog", response_model=BlogPost)
def create_blog_post(post_data: BlogPostCreate, current_user: dict = Depends(check_role(["admin"]))):
    new_id = max([p["id"] for p in BLOG_POSTS]) + 1 if BLOG_POSTS else 1
    new_post = {
        "id": new_id,
        "locale": post_data.locale,
        "title": post_data.title,
        "summary": post_data.summary,
        "content": post_data.content,
        "cover_image": post_data.cover_image,
        "secondary_image": post_data.secondary_image,
        "author": post_data.author,
        "date": datetime.date.today().isoformat(),
        "category": post_data.category
    }
    # Añadir a la base de datos
    BLOG_POSTS.append(new_post)
    return new_post

# 3. Tablero de Demandas B2B (Requerimientos Anónimos Públicos)
@app.get("/api/demands", response_model=List[DemandPublic])
def get_public_demands():
    # Hacemos los requerimientos anónimos: ocultamos datos del cliente (nombre, email, tax_id)
    public_list = []
    for d in DEMANDS:
        public_list.append(
            DemandPublic(
                id=d["id"],
                country=d["country"],
                country_code=d["country_code"],
                product=d["product"],
                product_en=d["product_en"],
                quantity_tons=d["quantity_tons"],
                target_price=d["target_price"],
                destination_port=d["destination_port"],
                destination_port_en=d["destination_port_en"],
                date_posted=d["date_posted"],
                is_verified=d["is_verified"]
            )
        )
    return public_list

@app.post("/api/demands", response_model=DemandPublic)
def create_demand(demand_data: DemandCreate, current_user: dict = Depends(check_role(["comprador", "admin"]))):
    new_id = max([d["id"] for d in DEMANDS]) + 1 if DEMANDS else 1
    new_demand = {
        "id": new_id,
        "company_name": demand_data.company_name,
        "company_tax_id": demand_data.company_tax_id,
        "contact_email": demand_data.contact_email,
        "country": demand_data.country,
        "country_code": demand_data.country_code,
        "product": demand_data.product,
        "product_en": demand_data.product_en,
        "quantity_tons": demand_data.quantity_tons,
        "target_price": demand_data.target_price,
        "destination_port": demand_data.destination_port,
        "destination_port_en": demand_data.destination_port_en,
        "date_posted": datetime.date.today().isoformat(),
        "is_verified": True
    }
    DEMANDS.append(new_demand)
    return DemandPublic(**new_demand)

# 4. Trazabilidad QR / Lotes (Acceso Público)
@app.get("/api/traceability/{lot_code}", response_model=TraceabilityLot)
def get_traceability_info(lot_code: str):
    lot = LOTS.get(lot_code.upper())
    if not lot:
        raise HTTPException(status_code=404, detail="Código de lote no encontrado")
    return lot

# 5. Formulario de Contacto General / Cotizaciones
@app.post("/api/contact")
def receive_contact(contact: ContactRequest):
    contact_dict = contact.model_dump()
    contact_dict["date_received"] = datetime.datetime.now().isoformat()
    RECEIVED_CONTACTS.append(contact_dict)
    return {
        "status": "success",
        "message": "Mensaje recibido correctamente. Nos pondremos en contacto pronto.",
        "message_en": "Message received successfully. We will get back to you shortly."
    }

# 6. Puertos Logística
@app.get("/api/logistics/ports", response_model=List[PortLogistics])
def get_ports_logistics():
    return PORTS_DATA

# 7. Autenticación (Login)
@app.post("/api/auth/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    user = USERS.get(credentials.email)
    if not user or user["password_hash"] != credentials.password:
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    
    token = create_access_token(user["email"], user["role"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": user["email"],
            "name": user["name"],
            "name_en": user["name_en"],
            "role": user["role"]
        }
    }

# 8. Portal Operativo Protegido por Roles
@app.get("/api/portal/data")
def get_portal_data(current_user: dict = Depends(get_current_user)):
    role = current_user["role"]
    
    if role == "admin":
        return {
            "summary": "Panel de Administración de Operaciones",
            "received_contacts": RECEIVED_CONTACTS,
            "detailed_demands": DEMANDS,  # Vista completa con nombres reales de empresas
            "producer_deliveries": HARVEST_DELIVERIES,  # Todas las entregas registradas por los productores
            "stats": {
                "total_producers": len(set(d["producer_email"] for d in HARVEST_DELIVERIES)) or 45,
                "total_cooperatives": 4,
                "active_shipments": 2,
                "completed_orders_val_usd": 120000.00
            }
        }
    
    elif role == "productor":
        # Filtrar las entregas para este productor específico por su correo
        user_deliveries = [
            d for d in HARVEST_DELIVERIES 
            if d.get("producer_email") == current_user["email"]
        ]
        # Ordenar por fecha desc (las más recientes arriba)
        user_deliveries.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "summary": f"Bienvenido, {current_user['name']}",
            "cooperative_details": {
                "name": "Cooperativa Agraria Valles de Satipo",
                "members": 128,
                "devida_partnership": True,
                "location": "Satipo, Junín"
            },
            "your_deliveries": user_deliveries,
            "price_history_reference": {
                "cacao_base_pen_kg": 18.50,
                "cacao_premium_pen_kg": 21.50
            }
        }
    
    elif role == "comprador":
        # Retorna solo las demandas de este comprador
        my_demands = [d for d in DEMANDS if d.get("contact_email") == current_user["email"]]
        return {
            "summary": "Panel de Comprador Internacional",
            "company": "EuroFoods AG",
            "my_active_requests": my_demands,
            "logistics_status": [
                {
                    "lot_code": "HY-2026-PL01",
                    "product": "Palta Hass",
                    "destination": "Puerto de Róterdam",
                    "eta": "2026-07-13",
                    "status": "En Tránsito Marítimo"
                }
            ]
        }
    
    raise HTTPException(status_code=400, detail="Rol no reconocido")

# 9. Endpoints de Cosechas y Entregas (Flujo Productor / Administrador)
@app.post("/api/portal/harvest", response_model=HarvestDelivery)
def create_harvest(harvest: HarvestCreate, current_user: dict = Depends(check_role(["productor"]))):
    new_id = max([d["id"] for d in HARVEST_DELIVERIES]) + 1 if HARVEST_DELIVERIES else 1
    new_delivery = {
        "id": new_id,
        "date": datetime.date.today().isoformat(),
        "product": harvest.product,
        "weight_kg": harvest.weight_kg,
        "proposed_price_pen_kg": harvest.proposed_price_pen_kg,
        "location": harvest.location or "No especificada",
        "status": "Registrado",
        "price_paid_pen": 0.0,
        "producer_name": current_user["name"],
        "producer_email": current_user["email"]
    }
    HARVEST_DELIVERIES.append(new_delivery)
    return new_delivery

@app.post("/api/portal/harvest/{harvest_id}/action", response_model=HarvestDelivery)
def update_harvest_action(harvest_id: int, request: HarvestActionRequest, current_user: dict = Depends(check_role(["admin"]))):
    target_delivery = None
    for d in HARVEST_DELIVERIES:
        if d["id"] == harvest_id:
            target_delivery = d
            break
            
    if not target_delivery:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
        
    action = request.action
    if action == "negotiate":
        target_delivery["status"] = "En Negociación"
    elif action == "agree_price":
        price = request.price_pen_kg
        if price is None:
            price = target_delivery.get("proposed_price_pen_kg")
        if price is None:
            raise HTTPException(status_code=400, detail="Se requiere un precio por kg para acordar el precio")
        target_delivery["proposed_price_pen_kg"] = price
        target_delivery["price_paid_pen"] = round(target_delivery["weight_kg"] * price, 2)
        target_delivery["status"] = "Precio Acordado"
    elif action == "complete":
        target_delivery["status"] = "Completado"
    else:
        raise HTTPException(status_code=400, detail="Acción no reconocida")
        
    return target_delivery
