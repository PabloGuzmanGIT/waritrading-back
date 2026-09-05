import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import (
    Base, engine, get_db, MARKET_PRICES, PRICE_HISTORY, update_prices_simulation
)
from app.seed import seed_database
from app import models
from app.schemas import (
    MarketPricesResponse, BlogPost, BlogPostCreate, DemandPublic, DemandCreate,
    TraceabilityLot, LoginRequest, TokenResponse, ContactRequest, PortLogistics,
    HarvestCreate, HarvestDelivery, HarvestActionRequest, DirectPurchaseCreate
)
from app.auth import create_access_token, get_current_user, check_role

# Inicializar y autocrear tablas de la base de datos
Base.metadata.create_all(bind=engine)

# Asegurar que la columna comentario exista y el check constraint admita 'cancelado' en Postgres
try:
    from sqlalchemy import text
    with engine.begin() as conn:
        # Agregar columna comentario si no existe
        try:
            conn.execute(text("ALTER TABLE lotes_dashboard ADD COLUMN comentario TEXT"))
        except Exception:
            pass
        # Actualizar restricción de estado en Postgres
        try:
            conn.execute(text("ALTER TABLE lotes_dashboard DROP CONSTRAINT IF EXISTS chk_estado_valido"))
            conn.execute(text("ALTER TABLE lotes_dashboard ADD CONSTRAINT chk_estado_valido CHECK (estado IN ('comprado', 'consolidado', 'entregado', 'cobrado', 'cancelado'))"))
        except Exception:
            pass
except Exception:
    pass

app = FastAPI(
    title="Wari Trading Co API",
    description="API para el Portal y PWA de la empresa agroexportadora Wari Trading Co S.A.C.",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|.*\.ngrok-free\.app|.*\.ngrok\.app|.*\.localtunnel\.me|.*\.railway\.app|.*\.up\.railway\.app|.*waritrading.*)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicio del servidor: Poblar datos semilla si la BD está vacía
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    try:
        seed_database(db)
    except Exception as e:
        print(f"Error al poblar datos semilla: {e}")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Wari Trading Co S.A.C."}

# 1. Precios del Mercado (Ticker)
@app.get("/api/market-prices", response_model=MarketPricesResponse)
def get_market_prices(force: bool = False):
    # Simular cambios dinámicos en los precios
    update_prices_simulation(force=force)
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
def get_blog_posts(locale: str = "es", db: Session = Depends(get_db)):
    posts = db.query(models.BlogPost).filter(models.BlogPost.locale == locale).all()
    return posts

@app.get("/api/blog/{post_id}", response_model=BlogPost)
def get_blog_post(post_id: int, locale: str = "es", db: Session = Depends(get_db)):
    post = db.query(models.BlogPost).filter(
        models.BlogPost.id == post_id,
        models.BlogPost.locale == locale
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post no encontrado o idioma no disponible")
    return post

@app.post("/api/blog", response_model=BlogPost)
def create_blog_post(
    post_data: BlogPostCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_role(["admin"]))
):
    new_post = models.BlogPost(
        locale=post_data.locale,
        title=post_data.title,
        summary=post_data.summary,
        content=post_data.content,
        cover_image=post_data.cover_image,
        secondary_image=post_data.secondary_image,
        author=post_data.author,
        date=datetime.date.today().isoformat(),
        category=post_data.category
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# 3. Tablero de Demandas B2B (Requerimientos Anónimos Públicos)
@app.get("/api/demands", response_model=List[DemandPublic])
def get_public_demands(db: Session = Depends(get_db)):
    demands = db.query(models.Demand).all()
    return demands

@app.post("/api/demands", response_model=DemandPublic)
def create_demand(
    demand_data: DemandCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_role(["comprador", "admin"]))
):
    new_demand = models.Demand(
        company_name=demand_data.company_name,
        company_tax_id=demand_data.company_tax_id,
        contact_email=demand_data.contact_email,
        country=demand_data.country,
        country_code=demand_data.country_code,
        product=demand_data.product,
        product_en=demand_data.product_en,
        quantity_tons=demand_data.quantity_tons,
        target_price=demand_data.target_price,
        destination_port=demand_data.destination_port,
        destination_port_en=demand_data.destination_port_en,
        date_posted=datetime.date.today().isoformat(),
        is_verified=True
    )
    db.add(new_demand)
    db.commit()
    db.refresh(new_demand)
    return new_demand

# 4. Trazabilidad QR / Lotes (Acceso Público)
@app.get("/api/traceability/{lot_code}", response_model=TraceabilityLot)
def get_traceability_info(lot_code: str, db: Session = Depends(get_db)):
    lot = db.query(models.TraceabilityLot).filter(models.TraceabilityLot.lot_code == lot_code.upper()).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Código de lote no encontrado")
    return lot

# 5. Formulario de Contacto General / Cotizaciones
@app.post("/api/contact")
def receive_contact(contact: ContactRequest, db: Session = Depends(get_db)):
    new_contact = models.Contact(
        name=contact.name,
        email=contact.email,
        company=contact.company,
        country=contact.country,
        product_interest=contact.product_interest,
        volume_tons=contact.volume_tons,
        message=contact.message,
        date_received=datetime.datetime.now().isoformat()
    )
    db.add(new_contact)
    db.commit()
    return {
        "status": "success",
        "message": "Mensaje recibido correctamente. Nos pondremos en contacto pronto.",
        "message_en": "Message received successfully. We will get back to you shortly."
    }

# 6. Puertos Logística
@app.get("/api/logistics/ports", response_model=List[PortLogistics])
def get_ports_logistics(db: Session = Depends(get_db)):
    return db.query(models.PortLogistics).all()

# 7. Autenticación (Login)
@app.post("/api/auth/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or user.password_hash != credentials.password:
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    
    token = create_access_token(user.email, user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "name": user.name,
            "name_en": user.name_en,
            "role": user.role
        }
    }

# 8. Portal Operativo Protegido por Roles
@app.get("/api/portal/data")
def get_portal_data(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    role = current_user["role"]
    
    if role == "admin":
        contacts = db.query(models.Contact).all()
        # Mapear contactos a dict para compatibilidad
        contacts_list = []
        for c in contacts:
            contacts_list.append({
                "name": c.name,
                "email": c.email,
                "company": c.company,
                "country": c.country,
                "product_interest": c.product_interest,
                "volume_tons": c.volume_tons,
                "message": c.message,
                "date_received": c.date_received
            })

        demands = db.query(models.Demand).all()
        demands_list = []
        for d in demands:
            demands_list.append({
                "id": d.id,
                "company_name": d.company_name,
                "company_tax_id": d.company_tax_id,
                "contact_email": d.contact_email,
                "country": d.country,
                "country_code": d.country_code,
                "product": d.product,
                "product_en": d.product_en,
                "quantity_tons": d.quantity_tons,
                "target_price": d.target_price,
                "destination_port": d.destination_port,
                "destination_port_en": d.destination_port_en,
                "date_posted": d.date_posted,
                "is_verified": d.is_verified
            })

        deliveries = db.query(models.HarvestDelivery).all()
        # Ordenar por fecha desc
        deliveries.sort(key=lambda x: x.date, reverse=True)
        deliveries_list = []
        for d in deliveries:
            deliveries_list.append({
                "id": d.id,
                "date": d.date,
                "product": d.product,
                "weight_kg": d.weight_kg,
                "proposed_price_pen_kg": d.proposed_price_pen_kg,
                "location": d.location,
                "status": d.status,
                "price_paid_pen": d.price_paid_pen,
                "producer_name": d.producer_name,
                "producer_email": d.producer_email
            })

        producers_count = len(set(d["producer_email"] for d in deliveries_list)) if deliveries_list else 45

        return {
            "summary": "Panel de Administración de Operaciones",
            "received_contacts": contacts_list,
            "detailed_demands": demands_list,
            "producer_deliveries": deliveries_list,
            "stats": {
                "total_producers": producers_count,
                "total_cooperatives": 4,
                "active_shipments": 2,
                "completed_orders_val_usd": 120000.00
            }
        }
    
    elif role == "productor":
        user_deliveries = db.query(models.HarvestDelivery).filter(
            models.HarvestDelivery.producer_email == current_user["email"]
        ).order_by(models.HarvestDelivery.date.desc()).all()
        
        deliveries_list = []
        for d in user_deliveries:
            deliveries_list.append({
                "id": d.id,
                "date": d.date,
                "product": d.product,
                "weight_kg": d.weight_kg,
                "proposed_price_pen_kg": d.proposed_price_pen_kg,
                "location": d.location,
                "status": d.status,
                "price_paid_pen": d.price_paid_pen,
                "producer_name": d.producer_name,
                "producer_email": d.producer_email
            })
        
        return {
            "summary": f"Bienvenido, {current_user['name']}",
            "cooperative_details": {
                "name": "Cooperativa Agraria Valles de Satipo",
                "members": 128,
                "devida_partnership": True,
                "location": "Satipo, Junín"
            },
            "your_deliveries": deliveries_list,
            "price_history_reference": {
                "cacao_base_pen_kg": 18.50,
                "cacao_premium_pen_kg": 21.50
            }
        }
    
    elif role == "comprador":
        my_demands = db.query(models.Demand).filter(
            models.Demand.contact_email == current_user["email"]
        ).all()
        
        demands_list = []
        for d in my_demands:
            demands_list.append({
                "id": d.id,
                "company_name": d.company_name,
                "company_tax_id": d.company_tax_id,
                "contact_email": d.contact_email,
                "country": d.country,
                "country_code": d.country_code,
                "product": d.product,
                "product_en": d.product_en,
                "quantity_tons": d.quantity_tons,
                "target_price": d.target_price,
                "destination_port": d.destination_port,
                "destination_port_en": d.destination_port_en,
                "date_posted": d.date_posted,
                "is_verified": d.is_verified
            })
            
        return {
            "summary": "Panel de Comprador Internacional",
            "company": "EuroFoods AG",
            "my_active_requests": demands_list,
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
def create_harvest(
    harvest: HarvestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_role(["productor"]))
):
    # Obtener el ID autoincremental de la base de datos
    new_delivery = models.HarvestDelivery(
        date=datetime.date.today().isoformat(),
        product=harvest.product,
        weight_kg=harvest.weight_kg,
        proposed_price_pen_kg=harvest.proposed_price_pen_kg,
        location=harvest.location or "No especificada",
        status="Registrado",
        price_paid_pen=0.0,
        producer_name=current_user["name"],
        producer_email=current_user["email"]
    )
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    return new_delivery

@app.post("/api/portal/harvest/{harvest_id}/action", response_model=HarvestDelivery)
def update_harvest_action(
    harvest_id: int,
    request: HarvestActionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_role(["admin"]))
):
    target_delivery = db.query(models.HarvestDelivery).filter(models.HarvestDelivery.id == harvest_id).first()
    if not target_delivery:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
        
    action = request.action
    if action == "negotiate":
        target_delivery.status = "En Negociación"
    elif action == "agree_price":
        price = request.price_pen_kg
        if price is None:
            price = target_delivery.proposed_price_pen_kg
        if price is None:
            raise HTTPException(status_code=400, detail="Se requiere un precio por kg para acordar el precio")
        target_delivery.proposed_price_pen_kg = price
        target_delivery.price_paid_pen = round(target_delivery.weight_kg * price, 2)
        target_delivery.status = "Precio Acordado"
    elif action == "complete":
        target_delivery.status = "Completado"
        price_pen_kg = target_delivery.proposed_price_pen_kg
        if not price_pen_kg or price_pen_kg <= 0:
            raise HTTPException(status_code=400, detail="No se puede completar una entrega sin precio pactado")
        
        # Mapear el nombre del producto
        raw_prod = target_delivery.product.lower().strip()
        product_mapped = 'cafe_pergamino'
        if 'cacao' in raw_prod:
            if 'fino' in raw_prod or 'aroma' in raw_prod:
                product_mapped = 'cacao_fino'
            else:
                product_mapped = 'cacao_conv'
        elif 'caf' in raw_prod or 'coff' in raw_prod:
            product_mapped = 'cafe_pergamino'
        
        # Buscar o crear ciclo activo
        ciclo = db.query(models.Ciclo).filter(models.Ciclo.estado == "activo").first()
        if not ciclo:
            ciclo = models.Ciclo(
                nombre=f"{datetime.date.today().strftime('%Y-%m')}-C1",
                fecha_inicio=datetime.date.today(),
                capital_desplegado=0.0,
                estado="activo"
            )
            db.add(ciclo)
            db.commit()
            db.refresh(ciclo)
            
        new_lote = models.LoteDashboard(
            ciclo_id=ciclo.id,
            producto=product_mapped,
            fecha_compra=datetime.date.today(),
            kg=target_delivery.weight_kg,
            precio_compra_skg=price_pen_kg,
            humedad_pct=12.0,
            estado="comprado",
            comentario=f"Compra desde Portal - Productor: {target_delivery.producer_name}"
        )
        db.add(new_lote)
    else:
        raise HTTPException(status_code=400, detail="Acción no reconocida")
        
    db.commit()
    db.refresh(target_delivery)
    return target_delivery


@app.post("/api/portal/direct-purchase", response_model=HarvestDelivery)
def create_direct_purchase(
    purchase: DirectPurchaseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_role(["admin"]))
):
    # 1. Registrar entrega de cosecha completada en el portal
    new_delivery = models.HarvestDelivery(
        date=datetime.date.today().isoformat(),
        product=purchase.product,
        weight_kg=purchase.weight_kg,
        proposed_price_pen_kg=purchase.price_paid_pen_kg,
        price_paid_pen=round(purchase.weight_kg * purchase.price_paid_pen_kg, 2),
        location=purchase.location or "No especificada",
        status="Completado",
        producer_name=purchase.producer_name,
        producer_email="compra_directa@wari.com"
    )
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    
    # 2. Mapear producto
    raw_prod = purchase.product.lower().strip()
    product_mapped = 'cafe_pergamino'
    if 'cacao' in raw_prod:
        if 'fino' in raw_prod or 'aroma' in raw_prod:
            product_mapped = 'cacao_fino'
        else:
            product_mapped = 'cacao_conv'
    elif 'caf' in raw_prod or 'coff' in raw_prod:
        product_mapped = 'cafe_pergamino'
    else:
        if raw_prod in ['cafe_pergamino', 'cacao_conv', 'cacao_fino']:
            product_mapped = raw_prod
            
    # 3. Registrar LoteDashboard en el dashboard de control
    ciclo = db.query(models.Ciclo).filter(models.Ciclo.estado == "activo").first()
    if not ciclo:
        ciclo = models.Ciclo(
            nombre=f"{datetime.date.today().strftime('%Y-%m')}-C1",
            fecha_inicio=datetime.date.today(),
            capital_desplegado=0.0,
            estado="activo"
        )
        db.add(ciclo)
        db.commit()
        db.refresh(ciclo)
        
    new_lote = models.LoteDashboard(
        ciclo_id=ciclo.id,
        producto=product_mapped,
        fecha_compra=datetime.date.today(),
        kg=purchase.weight_kg,
        precio_compra_skg=purchase.price_paid_pen_kg,
        humedad_pct=purchase.humedad_pct if purchase.humedad_pct is not None else 12.0,
        comprador=purchase.comprador if purchase.comprador else None,
        precio_venta_pactado_skg=purchase.precio_venta_pactado_skg if purchase.precio_venta_pactado_skg else None,
        estado="comprado",
        comentario=f"Compra Directa Portal - Vendedor: {purchase.producer_name}"
    )
    db.add(new_lote)
    db.commit()
    db.refresh(new_lote)
    
    return new_delivery


# ==============================================================================
# 10. ENDPOINTS PARA EL DASHBOARD INTERNO (ROL: ADMIN)
# ==============================================================================

# 10.1 Pestaña HOY: Obtener y calcular cotizaciones y precios de compra máx
@app.get("/api/dashboard/prices")
def get_dashboard_prices(db: Session = Depends(get_db), current_user: dict = Depends(check_role(["admin"]))):
    today = datetime.date.today()
    # Buscar si ya se publicó algún precio hoy
    precios_hoy = db.query(models.PrecioDiario).filter(models.PrecioDiario.fecha == today).all()
    precios_hoy_dict = {p.producto: p for p in precios_hoy}
    
    # Datos del mercado global
    tc_ref = 3.40
    cacao_intl = MARKET_PRICES["cacao_international"]
    cafe_intl = MARKET_PRICES["cafe_international"]
    
    # Calcular precios máximos teóricos usando las fórmulas de negocio
    cafe_max = round((cafe_intl * 100 * 2.2046 * tc_ref / 100) * 0.73 - 1.15 - 0.75, 2)
    cacao_conv_max = round((cacao_intl / 1000 * tc_ref) * 0.90 - 0.95 - 0.90, 2)
    cacao_fino_max = round((cacao_intl * 1.3 / 1000 * tc_ref) * 0.90 - 0.95 - 0.90, 2)
    
    # Unificar en una respuesta estructurada
    productos = {
        "cafe_pergamino": {
            "producto": "cafe_pergamino",
            "nombre": "Café Pergamino",
            "cotizacion_intl": cafe_intl * 100,
            "unidad_intl": "¢/lb",
            "tipo_cambio": tc_ref,
            "compra_max_skg": cafe_max,
            "compra_publicada_skg": precios_hoy_dict["cafe_pergamino"].compra_publicada_skg if "cafe_pergamino" in precios_hoy_dict else None,
            "venta_ref_skg": precios_hoy_dict["cafe_pergamino"].venta_ref_skg if "cafe_pergamino" in precios_hoy_dict else round(cafe_max + 1.15 + 0.75, 2),
            "publicado": "cafe_pergamino" in precios_hoy_dict
        },
        "cacao_conv": {
            "producto": "cacao_conv",
            "nombre": "Cacao Convencional",
            "cotizacion_intl": cacao_intl,
            "unidad_intl": "US$/t",
            "tipo_cambio": tc_ref,
            "compra_max_skg": cacao_conv_max,
            "compra_publicada_skg": precios_hoy_dict["cacao_conv"].compra_publicada_skg if "cacao_conv" in precios_hoy_dict else None,
            "venta_ref_skg": precios_hoy_dict["cacao_conv"].venta_ref_skg if "cacao_conv" in precios_hoy_dict else round(cacao_conv_max + 0.95 + 0.90, 2),
            "publicado": "cacao_conv" in precios_hoy_dict
        },
        "cacao_fino": {
            "producto": "cacao_fino",
            "nombre": "Cacao Fino de Aroma",
            "cotizacion_intl": cacao_intl * 1.3,
            "unidad_intl": "US$/t",
            "tipo_cambio": tc_ref,
            "compra_max_skg": cacao_fino_max,
            "compra_publicada_skg": precios_hoy_dict["cacao_fino"].compra_publicada_skg if "cacao_fino" in precios_hoy_dict else None,
            "venta_ref_skg": precios_hoy_dict["cacao_fino"].venta_ref_skg if "cacao_fino" in precios_hoy_dict else round(cacao_fino_max + 0.95 + 0.90, 2),
            "publicado": "cacao_fino" in precios_hoy_dict
        }
    }
    
    # Verificar lotes sin venta calzada (lotes sin comprador o sin precio de venta pactado)
    lotes_sin_calzar = db.query(models.LoteDashboard).filter(
        ((models.LoteDashboard.precio_venta_pactado_skg == None) | (models.LoteDashboard.comprador == None)) &
        (models.LoteDashboard.estado != "cancelado")
    ).all()
    
    lotes_sin_calzar_list = []
    for l in lotes_sin_calzar:
        lotes_sin_calzar_list.append({
            "id": l.id,
            "producto": l.producto,
            "fecha_compra": l.fecha_compra.isoformat() if hasattr(l.fecha_compra, "isoformat") else str(l.fecha_compra),
            "kg": l.kg,
            "precio_compra_skg": l.precio_compra_skg,
            "precio_venta_pactado_skg": l.precio_venta_pactado_skg,
            "comprador": l.comprador,
            "estado": l.estado,
            "comentario": l.comentario
        })
    
    return {
        "fecha": today.isoformat(),
        "productos": productos,
        "lotes_sin_calzar": lotes_sin_calzar_list,
        "volatilidad_alerta": False
    }

# 10.2 Publicar precio del día (Pestaña HOY)
@app.post("/api/dashboard/prices/publish")
def publish_dashboard_price(data: dict, db: Session = Depends(get_db), current_user: dict = Depends(check_role(["admin"]))):
    producto = data.get("producto")
    compra_publicada_skg = data.get("compra_publicada_skg")
    venta_ref_skg = data.get("venta_ref_skg")
    cotizacion_intl = data.get("cotizacion_intl")
    tipo_cambio = data.get("tipo_cambio")
    compra_max_skg = data.get("compra_max_skg")
    
    if not producto or compra_publicada_skg is None:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios para la publicación")
        
    today = datetime.date.today()
    
    # Buscar si ya existe
    precio = db.query(models.PrecioDiario).filter(
        models.PrecioDiario.fecha == today,
        models.PrecioDiario.producto == producto
    ).first()
    
    if precio:
        precio.compra_publicada_skg = compra_publicada_skg
        if venta_ref_skg is not None:
            precio.venta_ref_skg = venta_ref_skg
    else:
        # Calcular paridad_skg teórica
        paridad = compra_max_skg + 0.90
        precio = models.PrecioDiario(
            fecha=today,
            producto=producto,
            cotizacion_intl=cotizacion_intl,
            tipo_cambio=tipo_cambio,
            paridad_skg=paridad,
            compra_max_skg=compra_max_skg,
            compra_publicada_skg=compra_publicada_skg,
            venta_ref_skg=venta_ref_skg,
            fuente="manual"
        )
        db.add(precio)
        
    db.commit()
    return {"status": "success", "message": f"Precio de {producto} publicado correctamente"}

# 10.3 Pestaña SEMANA: Resumen físico/financiero y eventos
@app.get("/api/dashboard/semana")
def get_dashboard_semana(db: Session = Depends(get_db), current_user: dict = Depends(check_role(["admin"]))):
    today = datetime.date.today()
    # Rango de la semana actual (lunes a domingo)
    start_week = today - datetime.timedelta(days=today.weekday())
    
    # Lotes de la semana
    lotes_semana = db.query(models.LoteDashboard).filter(
        models.LoteDashboard.fecha_compra >= start_week
    ).all()
    
    kg_totales = sum(l.kg for l in lotes_semana)
    dinero_desplegado = sum(l.kg * l.precio_compra_skg for l in lotes_semana)
    
    # Agrupar compras por producto
    resumen_productos = {}
    for l in lotes_semana:
        if l.producto not in resumen_productos:
            resumen_productos[l.producto] = {"kg": 0.0, "monto": 0.0, "lotes_count": 0}
        resumen_productos[l.producto]["kg"] += float(l.kg)
        resumen_productos[l.producto]["monto"] += float(l.kg * l.precio_compra_skg)
        resumen_productos[l.producto]["lotes_count"] += 1
        
    for prod, info in resumen_productos.items():
        info["precio_promedio"] = round(info["monto"] / info["kg"], 2) if info["kg"] > 0 else 0
        
    # Cobros pendientes y días transcurridos
    lotes_pendientes_cobro = db.query(models.LoteDashboard).filter(
        models.LoteDashboard.estado != "cobrado",
        models.LoteDashboard.precio_venta_pactado_skg != None
    ).all()
    
    cobros_pendientes_list = []
    for l in lotes_pendientes_cobro:
        dias_transcurridos = 0
        if l.fecha_entrega:
            dias_transcurridos = (today - l.fecha_entrega).days
        elif l.fecha_compra:
            dias_transcurridos = (today - l.fecha_compra).days
            
        cobros_pendientes_list.append({
            "id": l.id,
            "producto": l.producto,
            "kg": l.kg,
            "monto_venta": round(l.kg * (l.precio_venta_pactado_skg or 0), 2),
            "comprador": l.comprador,
            "dias_transcurridos": max(0, dias_transcurridos),
            "estado": l.estado
        })
        
    # Feed de eventos de mercado
    eventos = db.query(models.EventoMercado).order_by(models.EventoMercado.fecha.desc()).limit(10).all()
    eventos_list = []
    for e in eventos:
        eventos_list.append({
            "id": e.id,
            "fecha": e.fecha.isoformat(),
            "titulo": e.titulo,
            "detalle": e.detalle,
            "impacto": e.impacto,
            "producto": e.producto
        })
        
    # Lista de todos los lotes de la semana
    lotes_semana_list = []
    for l in lotes_semana:
        lotes_semana_list.append({
            "id": l.id,
            "producto": l.producto,
            "kg": l.kg,
            "precio_compra_skg": l.precio_compra_skg,
            "precio_venta_pactado_skg": l.precio_venta_pactado_skg,
            "comprador": l.comprador,
            "estado": l.estado,
            "fecha_compra": l.fecha_compra.isoformat(),
            "comentario": l.comentario
        })
        
    return {
        "rango_semana": f"Desde Lunes {start_week.strftime('%d/%m/%Y')}",
        "kg_totales": kg_totales,
        "dinero_desplegado": round(dinero_desplegado, 2),
        "resumen_productos": resumen_productos,
        "cobros_pendientes": cobros_pendientes_list,
        "eventos_mercado": eventos_list,
        "lotes": lotes_semana_list
    }

# 10.4 Agregar evento de mercado (Pestaña SEMANA)
@app.post("/api/dashboard/events")
def create_dashboard_event(data: dict, db: Session = Depends(get_db), current_user: dict = Depends(check_role(["admin"]))):
    titulo = data.get("titulo")
    detalle = data.get("detalle")
    impacto = data.get("impacto", "neutro")
    producto = data.get("producto")
    
    if not titulo or not detalle:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios para el evento")
        
    new_event = models.EventoMercado(
        fecha=datetime.date.today(),
        titulo=titulo,
        detalle=detalle,
        impacto=impacto,
        producto=producto
    )
    db.add(new_event)
    db.commit()
    return {"status": "success", "message": "Evento registrado correctamente"}

# 10.4.5 Pestaña PROMEDIO DEL DIA: Datos del día actual
@app.get("/api/dashboard/promedio-dia")
def get_dashboard_promedio_dia(db: Session = Depends(get_db), current_user: dict = Depends(check_role(["admin"]))):
    today = datetime.date.today()
    
    # 1. Obtener lotes de hoy
    lotes_hoy = db.query(models.LoteDashboard).filter(models.LoteDashboard.fecha_compra == today).all()
    
    # 2. Obtener precios publicados de hoy
    precios_hoy = db.query(models.PrecioDiario).filter(models.PrecioDiario.fecha == today).all()
    precios_hoy_dict = {p.producto: float(p.compra_publicada_skg) for p in precios_hoy if p.compra_publicada_skg is not None}
    
    # 3. Calcular promedios por producto
    resumen = {}
    for prod in ["cafe_pergamino", "cacao_conv", "cacao_fino"]:
        lotes_prod = [l for l in lotes_hoy if l.producto == prod]
        total_kg = sum(float(l.kg) for l in lotes_prod)
        total_monto = sum(float(l.kg) * float(l.precio_compra_skg) for l in lotes_prod)
        precio_promedio = round(total_monto / total_kg, 2) if total_kg > 0 else 0.0
        
        # Nombre bonito para el frontend
        nombre = "Café Pergamino"
        if prod == "cacao_conv":
            nombre = "Cacao Convencional"
        elif prod == "cacao_fino":
            nombre = "Cacao Fino de Aroma"
            
        resumen[prod] = {
            "producto": prod,
            "nombre": nombre,
            "total_kg": total_kg,
            "total_monto": total_monto,
            "precio_promedio": precio_promedio,
            "precio_publicado": precios_hoy_dict.get(prod, 0.0)
        }
        
    # 4. Resumen general de hoy
    general = {
        "total_kg": sum(float(l.kg) for l in lotes_hoy),
        "total_monto": sum(float(l.kg) * float(l.precio_compra_skg) for l in lotes_hoy),
        "lotes_count": len(lotes_hoy)
    }
    
    lotes_list = []
    for l in lotes_hoy:
        lotes_list.append({
            "id": l.id,
            "producto": l.producto,
            "kg": float(l.kg),
            "precio_compra_skg": float(l.precio_compra_skg),
            "precio_venta_pactado_skg": float(l.precio_venta_pactado_skg) if l.precio_venta_pactado_skg is not None else None,
            "comprador": l.comprador,
            "estado": l.estado,
            "comentario": l.comentario
        })
        
    return {
        "fecha": today.isoformat(),
        "productos": resumen,
        "general": general,
        "lotes": lotes_list
    }

# 10.5 Pestaña PLAN vs REAL: Datos comparativos de caja y márgenes
@app.get("/api/dashboard/plan-vs-real")
def get_dashboard_plan_vs_real(db: Session = Depends(get_db), current_user: dict = Depends(check_role(["admin"]))):
    proyecciones = db.query(models.ProyeccionMensual).order_by(models.ProyeccionMensual.mes).all()
    
    colchon_inicial = 50600.00
    movimientos = db.query(models.MovimientoCaja).order_by(models.MovimientoCaja.fecha).all()
    
    # Agrupar movimientos por mes
    movimientos_por_mes = {}
    for mov in movimientos:
        mes_key = f"{mov.fecha.year}-{mov.fecha.month:02d}-01"
        if mes_key not in movimientos_por_mes:
            movimientos_por_mes[mes_key] = 0.0
        movimientos_por_mes[mes_key] += float(mov.monto)
        
    # Calcular márgenes reales agrupados por mes
    lotes = db.query(models.LoteDashboard).all()
    margen_por_mes = {}
    for l in lotes:
        fecha_eval = l.fecha_cobro or l.fecha_entrega or l.fecha_compra
        if not fecha_eval:
            continue
        mes_key = f"{fecha_eval.year}-{fecha_eval.month:02d}-01"
        if mes_key not in margen_por_mes:
            margen_por_mes[mes_key] = 0.0
            
        precio_v = l.precio_venta_real_skg or l.precio_venta_pactado_skg
        if precio_v is not None:
            margen_neto = (precio_v - l.precio_compra_skg - l.costos_skg) * l.kg * (1.0 - (l.merma_pct or 0.0)/100.0)
            margen_por_mes[mes_key] += round(margen_neto, 2)
            
    comparativa_meses = []
    caja_real_corriente = colchon_inicial
    
    for proj in proyecciones:
        mes_str = proj.mes.isoformat()
        
        monto_movs = movimientos_por_mes.get(mes_str, 0.0)
        monto_margen = margen_por_mes.get(mes_str, 0.0)
        
        flujo_neto_real = monto_movs + monto_margen
        caja_real_corriente += flujo_neto_real
        
        es_futuro = proj.mes > datetime.date.today().replace(day=1)
        
        comparativa_meses.append({
            "mes": proj.mes.strftime("%b %y"),
            "caja_plan": float(proj.caja_plan),
            "caja_real": round(caja_real_corriente, 2) if not es_futuro else None,
            "margen_plan": float(proj.margen_plan),
            "margen_real": round(monto_margen, 2) if not es_futuro else None
        })
        
    ciclos_completados = db.query(models.Ciclo).filter(models.Ciclo.estado == "cerrado").count()
    
    lotes_cobrados = db.query(models.LoteDashboard).filter(
        models.LoteDashboard.fecha_cobro != None,
        models.LoteDashboard.fecha_entrega != None
    ).all()
    
    dias_promedio_cobro = 0
    if lotes_cobrados:
        dias_totales = sum((l.fecha_cobro - l.fecha_entrega).days for l in lotes_cobrados)
        dias_promedio_cobro = round(dias_totales / len(lotes_cobrados), 1)
        
    return {
        "comparativa_mensual": comparativa_meses,
        "kpis": {
            "ciclos_completados": ciclos_completados,
            "dias_promedio_cobro": dias_promedio_cobro,
            "margen_neto_promedio_pct": 3.45,
            "meta_margen_pct": 3.50,
            "equilibrio_margen_pct": 3.28
        }
    }

# 10.6 Pestaña SENSORES: Semáforo de KPIs
@app.get("/api/dashboard/sensors")
def get_dashboard_sensors(db: Session = Depends(get_db), current_user: dict = Depends(check_role(["admin"]))):
    today = datetime.date.today()
    
    lotes_cobrados = db.query(models.LoteDashboard).filter(models.LoteDashboard.estado == "cobrado").all()
    margen_neto_prom = 3.5
    if lotes_cobrados:
        total_compra = sum(l.kg * l.precio_compra_skg for l in lotes_cobrados)
        total_ganancia_neta = sum(((l.precio_venta_real_skg or 0) - l.precio_compra_skg - l.costos_skg) * l.kg * (1 - (l.merma_pct or 0)/100) for l in lotes_cobrados)
        if total_compra > 0:
            margen_neto_prom = round((total_ganancia_neta / total_compra) * 100, 2)
            
    status_margen = "rojo" if margen_neto_prom <= 2.5 else "ambar" if margen_neto_prom < 3.5 else "verde"
    
    ciclos_mes = 2.0
    status_ciclos = "verde"
    
    lotes_por_cobrar = db.query(models.LoteDashboard).filter(
        models.LoteDashboard.estado == "entregado",
        models.LoteDashboard.fecha_entrega != None
    ).all()
    
    max_dias_cobro = 0
    for l in lotes_por_cobrar:
        dias = (today - l.fecha_entrega).days
        if dias > max_dias_cobro:
            max_dias_cobro = dias
            
    status_cobro = "rojo" if max_dias_cobro > 10 else "ambar" if max_dias_cobro > 5 else "verde"
    
    colchon = 50600.00
    monto_movs = db.query(models.MovimientoCaja.monto).all()
    caja_actual = colchon + sum(float(m[0]) for m in monto_movs)
    
    status_caja = "rojo" if caja_actual < 16500 else "ambar" if caja_actual < 33000 else "verde"
    
    lotes_sin_calzar = db.query(models.LoteDashboard).filter(
        models.LoteDashboard.precio_venta_pactado_skg == None
    ).all()
    
    lotes_sin_calzar_criticos = 0
    for l in lotes_sin_calzar:
        dias = (today - l.fecha_compra).days
        if dias > 3:
            lotes_sin_calzar_criticos += 1
            
    status_calzar = "rojo" if lotes_sin_calzar_criticos >= 1 else "verde"
    
    mermas = db.query(models.LoteDashboard.merma_pct).all()
    max_merma = max([float(m[0]) for m in mermas if m[0] is not None] or [0.0])
    
    status_merma = "rojo" if max_merma > 4.0 else "ambar" if max_merma > 2.0 else "verde"
    
    return {
        "sensores": [
            {
                "id": "margen",
                "nombre": "Margen Neto / Ciclo",
                "valor": f"{margen_neto_prom}%",
                "meta": "≥ 3.5%",
                "estado": status_margen,
                "alarma": "≤ 2.5% por 2 ciclos"
            },
            {
                "id": "ciclos",
                "nombre": "Ciclos en el Mes",
                "valor": str(ciclos_mes),
                "meta": "≥ 2.0",
                "estado": status_ciclos,
                "alarma": "< 1.5 al día 20"
            },
            {
                "id": "cobro",
                "nombre": "Días de Cobro",
                "valor": f"{max_dias_cobro} días máx",
                "meta": "≤ 5 días",
                "estado": status_cobro,
                "alarma": "> 10 días"
            },
            {
                "id": "caja",
                "nombre": "Caja Seguridad",
                "valor": f"S/. {caja_actual:,.2f}",
                "meta": "≥ S/. 33,000",
                "estado": status_caja,
                "alarma": "< S/. 16,500"
            },
            {
                "id": "calzar",
                "nombre": "Lotes Sin Calzar",
                "valor": f"{len(lotes_sin_calzar)} lotes",
                "meta": "0 lotes",
                "estado": status_calzar,
                "alarma": "≥ 1 por > 3 días"
            },
            {
                "id": "merma",
                "nombre": "Merma Máxima por Lote",
                "valor": f"{max_merma}%",
                "meta": "≤ 2.0%",
                "estado": status_merma,
                "alarma": "> 4.0%"
            }
        ]
    }

# 10.7 Registrar lote comprado rápidamente (Pestaña SEMANA)
@app.post("/api/dashboard/lotes")
def create_dashboard_lote(data: dict, db: Session = Depends(get_db), current_user: dict = Depends(check_role(["admin"]))):
    producto = data.get("producto")
    fecha_compra_str = data.get("fecha_compra")
    kg = data.get("kg")
    precio_compra_skg = data.get("precio_compra_skg")
    precio_venta_pactado_skg = data.get("precio_venta_pactado_skg")
    comprador = data.get("comprador")
    humedad_pct = data.get("humedad_pct")
    costos_skg = data.get("costos_skg", 1.15)
    
    if not producto or not kg or not precio_compra_skg:
        raise HTTPException(status_code=400, detail="Faltan campos requeridos")
        
    fecha_c = datetime.datetime.strptime(fecha_compra_str, "%Y-%m-%d").date() if fecha_compra_str else datetime.date.today()
    
    # Crear un ciclo por defecto si no hay ciclo activo
    ciclo = db.query(models.Ciclo).filter(models.Ciclo.estado == "activo").first()
    if not ciclo:
        ciclo = models.Ciclo(
            nombre=f"{fecha_c.strftime('%Y-%m')}-C1",
            fecha_inicio=fecha_c,
            capital_desplegado=0.0,
            estado="activo"
        )
        db.add(ciclo)
        db.commit()
        db.refresh(ciclo)
        
    new_lote = models.LoteDashboard(
        ciclo_id=ciclo.id,
        producto=producto,
        fecha_compra=fecha_c,
        kg=float(kg),
        precio_compra_skg=float(precio_compra_skg),
        humedad_pct=float(humedad_pct) if humedad_pct is not None else None,
        comprador=comprador,
        precio_venta_pactado_skg=float(precio_venta_pactado_skg) if precio_venta_pactado_skg is not None else None,
        costos_skg=float(costos_skg),
        estado="comprado"
    )
    
    db.add(new_lote)
    
    # Registrar movimiento de caja como egreso (egreso = -kg * precio_compra)
    monto_caja = -float(kg) * float(precio_compra_skg)
    new_mov = models.MovimientoCaja(
        fecha=fecha_c,
        tipo="otro",
        monto=monto_caja,
        nota=f"Compra Lote {producto} - {kg} kg"
    )
    db.add(new_mov)
    
    db.commit()
    return {"status": "success", "message": "Lote registrado y caja actualizada"}

# 10.8 Cancelar transacción (lote) con comentario y reverso de caja
@app.post("/api/dashboard/lotes/{lote_id}/cancel")
def cancel_dashboard_lote(lote_id: int, data: dict, db: Session = Depends(get_db), current_user: dict = Depends(check_role(["admin"]))):
    comentario = data.get("comentario")
    if not comentario:
        raise HTTPException(status_code=400, detail="Debe ingresar un comentario para cancelar la transacción")
        
    lote = db.query(models.LoteDashboard).filter(models.LoteDashboard.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
        
    if lote.estado == "cancelado":
        raise HTTPException(status_code=400, detail="El lote ya se encuentra cancelado")
        
    # Guardar comentario y cambiar estado
    lote.estado = "cancelado"
    lote.comentario = comentario
    
    # Reverso de caja (ingreso = +kg * precio_compra)
    monto_reverso = float(lote.kg) * float(lote.precio_compra_skg)
    new_mov = models.MovimientoCaja(
        fecha=datetime.date.today(),
        tipo="otro",
        monto=monto_reverso,
        nota=f"REVERSO Compra Lote #{lote_id} ({lote.producto}) - Cancelado: {comentario}"
    )
    db.add(new_mov)
    
    db.commit()
    return {"status": "success", "message": "Transacción cancelada y caja reembolsada con éxito"}

# 10.9 Eliminar venta del lote (descalzar) con comentario
@app.post("/api/dashboard/lotes/{lote_id}/delete-sale")
def delete_dashboard_lote_sale(lote_id: int, data: dict, db: Session = Depends(get_db), current_user: dict = Depends(check_role(["admin"]))):
    comentario = data.get("comentario")
    if not comentario:
        raise HTTPException(status_code=400, detail="Debe ingresar un comentario para eliminar la venta")
        
    lote = db.query(models.LoteDashboard).filter(models.LoteDashboard.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
        
    # Resetear venta
    lote.comprador = None
    lote.precio_venta_pactado_skg = None
    lote.estado = "comprado" # Resetear estado a comprado para que vuelva a estar sin calzar
    lote.comentario = f"Venta eliminada: {comentario}"
    
    db.commit()
    return {"status": "success", "message": "Venta eliminada del lote con éxito"}


