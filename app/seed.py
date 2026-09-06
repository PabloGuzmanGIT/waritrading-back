import datetime
from sqlalchemy.orm import Session
from app import models
from app.database import settings
from app.security import hash_password

# Datos semilla de usuarios. La contraseña se toma de variables de entorno
# (SEED_*_PASSWORD) para no dejar credenciales fijas en el repo; los defaults
# de database.py son solo para desarrollo local.
USERS_SEED = {
    "admin@hallpayaku.com": {
        "email": "admin@hallpayaku.com",
        "name": "Administrador General",
        "name_en": "General Administrator",
        "role": "admin",
        "password": settings.SEED_ADMIN_PASSWORD,
    },
    "productor@hallpayaku.com": {
        "email": "productor@hallpayaku.com",
        "name": "Jorge Condori (Coop. Satipo)",
        "name_en": "Jorge Condori (Satipo Coop)",
        "role": "productor",
        "password": settings.SEED_PRODUCTOR_PASSWORD,
    },
    "comprador@hallpayaku.com": {
        "email": "comprador@hallpayaku.com",
        "name": "Michael Green (EuroFoods)",
        "name_en": "Michael Green (EuroFoods)",
        "role": "comprador",
        "password": settings.SEED_COMPRADOR_PASSWORD,
    }
}

# Datos semilla de artículos de blog
BLOG_POSTS_SEED = [
    {
        "locale": "es",
        "title": "Cómo compramos en el VRAEM: precio del día y pago al contado",
        "summary": "El precio máximo de compra se recalcula cada mañana con la cotización internacional y el tipo de cambio. Así funciona para el productor y para el comprador.",
        "content": "<p>Cada mañana publicamos el precio máximo de compra de café pergamino y cacao para nuestros puntos de acopio en el VRAEM. Ese precio se calcula a partir de la cotización internacional del día (café arábica en ICE, cacao en la bolsa de Nueva York/Londres) y el tipo de cambio USD/PEN, descontando rendimiento y costos.</p><h3>Por qué se recalcula a diario</h3><p>En semanas volátiles, usar la cotización del día anterior puede significar comprar por encima de la paridad de exportación. Recalcular cada mañana protege el margen y le da al productor una referencia clara y verificable.</p><h3>Pago al contado</h3><p>Liquidamos en el punto de acopio contra peso neto certificado, con comprobante. Sin descuentos sorpresa ni plazos.</p>",
        "cover_image": "/images/beans.png",
        "secondary_image": "/images/apurimac_jungle.png",
        "author": "Equipo de Acopio",
        "date": "2026-08-25",
        "category": "Cómo trabajamos"
    },
    {
        "locale": "en",
        "title": "How we buy in the VRAEM: daily price and cash payment",
        "summary": "The maximum purchase price is recalculated every morning from the international quote and the exchange rate. Here is how it works for producer and buyer.",
        "content": "<p>Every morning we publish the maximum purchase price for parchment coffee and cocoa at our collection points in the VRAEM. That price is derived from the day's international quote (arabica coffee on ICE, cocoa on NY/London) and the USD/PEN exchange rate, net of yield and costs.</p><h3>Why it is recalculated daily</h3><p>In volatile weeks, using yesterday's quote can mean buying above export parity. Recalculating every morning protects the margin and gives the producer a clear, verifiable reference.</p><h3>Cash payment</h3><p>We settle at the collection point against certified net weight, with a receipt. No surprise deductions, no payment terms.</p>",
        "cover_image": "/images/beans.png",
        "secondary_image": "/images/apurimac_jungle.png",
        "author": "Sourcing Team",
        "date": "2026-08-25",
        "category": "How we work"
    },
    {
        "locale": "es",
        "title": "Calendario de cosecha de café y cacao en el VRAEM",
        "summary": "Cuándo hay volumen de café pergamino y de cacao CCN-51 en el valle, y cómo planificar tus pedidos.",
        "content": "<p>El café en el VRAEM se cosecha principalmente entre abril y setiembre, con el pico entre mayo y julio. El pergamino disponible para acopio se concentra en esa ventana.</p><h3>Cacao</h3><p>El cacao (CCN-51 y corriente) tiene producción durante casi todo el año, con un pico marcado entre mayo y agosto y una campaña menor hacia fin de año.</p><h3>Planificación</h3><p>Para pedidos de exportación conviene cerrar el compromiso en junio–julio, cuando las casas exportadoras arman embarques. Escríbenos con tu volumen y ventana objetivo y te confirmamos disponibilidad.</p>",
        "cover_image": "/images/apurimac_jungle.png",
        "secondary_image": "/images/beans.png",
        "author": "Equipo de Acopio",
        "date": "2026-08-18",
        "category": "Mercado"
    },
    {
        "locale": "en",
        "title": "Coffee and cocoa harvest calendar in the VRAEM",
        "summary": "When parchment coffee and CCN-51 cocoa volume is available in the valley, and how to plan your orders.",
        "content": "<p>Coffee in the VRAEM is harvested mainly between April and September, peaking from May to July. Parchment available for collection is concentrated in that window.</p><h3>Cocoa</h3><p>Cocoa (CCN-51 and common bean) produces almost year-round, with a clear peak between May and August and a smaller campaign towards year-end.</p><h3>Planning</h3><p>For export orders it is best to commit in June–July, when export houses build shipments. Send us your volume and target window and we'll confirm availability.</p>",
        "cover_image": "/images/apurimac_jungle.png",
        "secondary_image": "/images/beans.png",
        "author": "Sourcing Team",
        "date": "2026-08-18",
        "category": "Market"
    },
    {
        "locale": "es",
        "title": "Qué necesita un comprador de la UE para cumplir con EUDR",
        "summary": "Geolocalización de parcelas, debida diligencia y expediente de origen: lo que preparamos por lote.",
        "content": "<p>El Reglamento de la UE contra la deforestación (EUDR) exige que el importador demuestre que el café o el cacao no proviene de tierras deforestadas después de 2020 y que cuenta con la geolocalización de las parcelas de origen.</p><h3>Lo que entregamos</h3><p>Identificamos cada lote desde el punto de acopio. Para compradores en la UE coordinamos con las cooperativas y organizaciones de la zona la geolocalización de las parcelas (punto GPS o polígono) y la documentación de debida diligencia, con verificación contra fuentes públicas como Global Forest Watch y Whisp, exportable en GeoJSON.</p><h3>Certificación</h3><p>La certificación orgánica o de comercio justo pertenece a la cooperativa de origen; nosotros canalizamos esos lotes, no emitimos certificados.</p>",
        "cover_image": "/images/figs.png",
        "secondary_image": "/images/apurimac_jungle.png",
        "author": "Trazabilidad",
        "date": "2026-08-10",
        "category": "EUDR"
    },
    {
        "locale": "en",
        "title": "What an EU buyer needs to comply with EUDR",
        "summary": "Plot geolocation, due diligence and an origin file: what we prepare per lot.",
        "content": "<p>The EU Deforestation Regulation (EUDR) requires the importer to prove that coffee or cocoa does not come from land deforested after 2020 and to hold the geolocation of the origin plots.</p><h3>What we provide</h3><p>We identify each lot from the collection point. For EU buyers we coordinate with the cooperatives and local organisations the geolocation of the plots (GPS point or polygon) and the due-diligence documentation, screened against public sources such as Global Forest Watch and Whisp, exportable as GeoJSON.</p><h3>Certification</h3><p>Organic or fair-trade certification belongs to the cooperative of origin; we channel those lots, we do not issue certificates.</p>",
        "cover_image": "/images/figs.png",
        "secondary_image": "/images/apurimac_jungle.png",
        "author": "Traceability",
        "date": "2026-08-10",
        "category": "EUDR"
    }
]

# Datos semilla de demandas B2B
DEMANDS_SEED = [
    {
        "company_name": "EuroFoods AG",
        "company_tax_id": "DE123456789",
        "contact_email": "purchasing@eurofoods.de",
        "country": "Alemania",
        "country_code": "DE",
        "product": "Palta Hass Fresca",
        "product_en": "Fresh Hass Avocado",
        "quantity_tons": 22.0,
        "target_price": "2.40 USD/kg",
        "destination_port": "Puerto de Hamburgo",
        "destination_port_en": "Port of Hamburg",
        "date_posted": "2026-07-01",
        "is_verified": True
    },
    {
        "company_name": "Organic Source Imports Inc.",
        "company_tax_id": "US987654321",
        "contact_email": "sourcing@organicsource.com",
        "country": "Estados Unidos",
        "country_code": "US",
        "product": "Cacao Orgánico Fino de Aroma (Granos)",
        "product_en": "Organic Fine Aroma Cocoa (Beans)",
        "quantity_tons": 12.5,
        "target_price": "6,600 USD/MT",
        "destination_port": "Puerto de Los Ángeles",
        "destination_port_en": "Port of Los Angeles",
        "date_posted": "2026-07-02",
        "is_verified": True
    }
]

# Datos semilla de lotes de trazabilidad
LOTS_SEED = {
    "HY-2026-PL01": {
        "lot_code": "HY-2026-PL01",
        "product": "Palta Hass",
        "product_en": "Hass Avocado",
        "cooperative": "Cooperativa Agraria Valles de Satipo",
        "cooperative_en": "Satipo Valleys Agricultural Cooperative",
        "region": "Satipo, Junín, Perú",
        "harvest_date": "2026-06-15",
        "packing_date": "2026-06-18",
        "soil_metrics": {
            "ph": 6.2,
            "organic_matter": "4.5% (Alto)",
            "organic_matter_en": "4.5% (High)",
            "type": "Franco-arenoso",
            "type_en": "Sandy loam"
        },
        "water_metrics": {
            "source": "Manantial andino natural",
            "source_en": "Natural Andean spring water",
            "purity_level": "99.2%",
            "irrigation_type": "Goteo eficiente",
            "irrigation_type_en": "Efficient drip irrigation"
        },
        "destination_port": "Puerto de Róterdam, Países Bajos",
        "destination_port_en": "Port of Rotterdam, Netherlands",
        "shipment_date": "2026-06-22",
        "status": "En Tránsito Marítimo",
        "status_en": "In Maritime Transit"
    },
    "HY-2026-CC03": {
        "lot_code": "HY-2026-CC03",
        "product": "Cacao Orgánico Fino de Aroma",
        "product_en": "Organic Fine Aroma Cocoa",
        "cooperative": "Asociación Agropecuaria del Cacao Oxapampa (DEVIDA)",
        "cooperative_en": "Oxapampa Cocoa Agricultural Association (DEVIDA)",
        "region": "Oxapampa, Pasco, Perú",
        "harvest_date": "2026-06-10",
        "packing_date": "2026-06-12",
        "soil_metrics": {
            "ph": 6.6,
            "organic_matter": "5.1% (Excelente)",
            "organic_matter_en": "5.1% (Excellent)",
            "type": "Franco-arcilloso",
            "type_en": "Clay loam"
        },
        "water_metrics": {
            "source": "Río de Cuenca Protegida",
            "source_en": "Protected Watershed River",
            "purity_level": "98.9%",
            "irrigation_type": "Gravedad controlado",
            "irrigation_type_en": "Controlled gravity irrigation"
        },
        "destination_port": "Puerto de Hamburgo, Alemania",
        "destination_port_en": "Port of Hamburg, Germany",
        "shipment_date": "2026-06-17",
        "status": "Entregado",
        "status_en": "Delivered"
    }
}

# Datos semilla de puertos
PORTS_DATA_SEED = [
    {
        "port": "Puerto de Róterdam (Holanda)",
        "port_en": "Port of Rotterdam (Netherlands)",
        "transit_days": 21,
        "temperature_c": 5.5,
        "humidity_pct": 85,
        "ventilation_cbm": 15
    },
    {
        "port": "Puerto de Hamburgo (Alemania)",
        "port_en": "Port of Hamburg (Germany)",
        "transit_days": 23,
        "temperature_c": 5.5,
        "humidity_pct": 85,
        "ventilation_cbm": 15
    },
    {
        "port": "Puerto de Los Ángeles (EE.UU.)",
        "port_en": "Port of Los Angeles (USA)",
        "transit_days": 12,
        "temperature_c": 6.0,
        "humidity_pct": 90,
        "ventilation_cbm": 20
    },
    {
        "port": "Puerto de Shanghái (China)",
        "port_en": "Port of Shanghai (China)",
        "transit_days": 32,
        "temperature_c": 5.0,
        "humidity_pct": 80,
        "ventilation_cbm": 10
    }
]

# Datos semilla de entregas de productores
HARVEST_DELIVERIES_SEED = [
    {
        "id": 1,
        "date": "2026-06-15",
        "product": "Palta Hass",
        "weight_kg": 4500.0,
        "proposed_price_pen_kg": 4.05,
        "location": "Satipo, Junín",
        "status": "Completado",
        "price_paid_pen": 18225.00,
        "producer_name": "Jorge Condori (Coop. Satipo)",
        "producer_email": "productor@hallpayaku.com"
    },
    {
        "id": 2,
        "date": "2026-06-28",
        "product": "Cacao Orgánico",
        "weight_kg": 850.0,
        "proposed_price_pen_kg": 21.50,
        "location": "Satipo, Junín",
        "status": "En Negociación",
        "price_paid_pen": 0.00,
        "producer_name": "Jorge Condori (Coop. Satipo)",
        "producer_email": "productor@hallpayaku.com"
    }
]

def seed_database(db: Session):
    # 1. Usuarios
    if db.query(models.User).count() == 0:
        for email, u in USERS_SEED.items():
            user = models.User(
                email=u["email"],
                name=u["name"],
                name_en=u["name_en"],
                role=u["role"],
                password_hash=hash_password(u["password"]),
            )
            db.add(user)
        print("Semilla: Usuarios cargados con éxito.")

    # 2. Artículos de Blog
    if db.query(models.BlogPost).count() == 0:
        for p in BLOG_POSTS_SEED:
            post = models.BlogPost(
                locale=p["locale"],
                title=p["title"],
                summary=p["summary"],
                content=p["content"],
                cover_image=p["cover_image"],
                secondary_image=p.get("secondary_image"),
                author=p["author"],
                date=p["date"],
                category=p["category"]
            )
            db.add(post)
        print("Semilla: Artículos de blog cargados con éxito.")

    # 3. Demandas B2B
    if db.query(models.Demand).count() == 0:
        for d in DEMANDS_SEED:
            demand = models.Demand(
                company_name=d["company_name"],
                company_tax_id=d["company_tax_id"],
                contact_email=d["contact_email"],
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
            db.add(demand)
        print("Semilla: Demandas B2B cargadas con éxito.")

    # 4. Lotes de Trazabilidad
    if db.query(models.TraceabilityLot).count() == 0:
        for lot_code, l in LOTS_SEED.items():
            lot = models.TraceabilityLot(
                lot_code=l["lot_code"],
                product=l["product"],
                product_en=l["product_en"],
                cooperative=l["cooperative"],
                cooperative_en=l["cooperative_en"],
                region=l["region"],
                harvest_date=l["harvest_date"],
                packing_date=l["packing_date"],
                soil_metrics=l["soil_metrics"],
                water_metrics=l["water_metrics"],
                destination_port=l["destination_port"],
                destination_port_en=l["destination_port_en"],
                shipment_date=l["shipment_date"],
                status=l["status"],
                status_en=l["status_en"]
            )
            db.add(lot)
        print("Semilla: Lotes de trazabilidad cargados con éxito.")

    # 5. Puertos
    if db.query(models.PortLogistics).count() == 0:
        for p in PORTS_DATA_SEED:
            port = models.PortLogistics(
                port=p["port"],
                port_en=p["port_en"],
                transit_days=p["transit_days"],
                temperature_c=p["temperature_c"],
                humidity_pct=p["humidity_pct"],
                ventilation_cbm=p["ventilation_cbm"]
            )
            db.add(port)
        print("Semilla: Puertos cargados con éxito.")

    # 6. Entregas de Productores
    if db.query(models.HarvestDelivery).count() == 0:
        for h in HARVEST_DELIVERIES_SEED:
            delivery = models.HarvestDelivery(
                id=h["id"],
                date=h["date"],
                product=h["product"],
                weight_kg=h["weight_kg"],
                proposed_price_pen_kg=h["proposed_price_pen_kg"],
                location=h["location"],
                status=h["status"],
                price_paid_pen=h["price_paid_pen"],
                producer_name=h["producer_name"],
                producer_email=h["producer_email"]
            )
            db.add(delivery)
        print("Semilla: Entregas de productores cargadas con éxito.")

    # 7. Proyección Mensual (Escenario Base del Dashboard)
    if db.query(models.ProyeccionMensual).count() == 0:
        metas = [
            ('2026-08-01', 20300, 0, 2500, 68400),
            ('2026-09-01', 20300, 16500, 2500, 69700),
            ('2026-10-01', 20300, 16500, 2500, 71000),
            ('2026-11-01', 20300, 16500, 2500, 72300),
            ('2026-12-01', 14600, 16500, 2500, 67900),
            ('2027-01-01', 11300, 16500, 2500, 60200),
            ('2027-02-01', 11300, 16500, 2500, 52500),
            ('2027-03-01', 16400, 16500, 2500, 49900),
            ('2027-04-01', 20300, 16500, 2500, 51200),
            ('2027-05-01', 20300, 16500, 2500, 52500),
            ('2027-06-01', 22300, 16500, 2500, 55800),
            ('2027-07-01', 22300, 16500, 2500, 59100)
        ]
        for m_str, margen, cuota, gastos, caja in metas:
            dt = datetime.datetime.strptime(m_str, "%Y-%m-%d").date()
            meta_obj = models.ProyeccionMensual(
                mes=dt,
                margen_plan=margen,
                cuota_plan=cuota,
                gastos_plan=gastos,
                caja_plan=caja
            )
            db.add(meta_obj)
        print("Semilla: Proyecciones mensuales cargadas con éxito.")

    # 8. Ciclos y Lotes de Dashboard de Prueba
    if db.query(models.Ciclo).count() == 0:
        c1 = models.Ciclo(nombre="2026-08-C1", fecha_inicio=datetime.date(2026, 8, 1), fecha_fin=datetime.date(2026, 8, 15), capital_desplegado=150000.0, estado="cerrado")
        c2 = models.Ciclo(nombre="2026-08-C2", fecha_inicio=datetime.date(2026, 8, 16), fecha_fin=datetime.date(2026, 8, 30), capital_desplegado=140000.0, estado="cerrado")
        c3 = models.Ciclo(nombre="2026-09-C1", fecha_inicio=datetime.date(2026, 9, 1), fecha_fin=datetime.date(2026, 9, 15), capital_desplegado=160000.0, estado="activo")
        db.add_all([c1, c2, c3])
        db.commit()

        # Agregar lotes iniciales
        l1 = models.LoteDashboard(ciclo_id=c1.id, producto="cafe_pergamino", fecha_compra=datetime.date(2026, 8, 5), kg=5200, precio_compra_skg=16.20, comprador="Machu Picchu Foods", precio_venta_pactado_skg=19.50, fecha_entrega=datetime.date(2026, 8, 8), fecha_cobro=datetime.date(2026, 8, 12), precio_venta_real_skg=19.50, merma_pct=1.8, costos_skg=1.15, estado="cobrado")
        l2 = models.LoteDashboard(ciclo_id=c1.id, producto="cacao_conv", fecha_compra=datetime.date(2026, 8, 10), kg=3800, precio_compra_skg=13.80, comprador="ofi/Olam", precio_venta_pactado_skg=16.80, fecha_entrega=datetime.date(2026, 8, 12), fecha_cobro=datetime.date(2026, 8, 14), precio_venta_real_skg=16.80, merma_pct=1.2, costos_skg=0.95, estado="cobrado")
        
        l3 = models.LoteDashboard(ciclo_id=c2.id, producto="cafe_pergamino", fecha_compra=datetime.date(2026, 8, 18), kg=6100, precio_compra_skg=16.50, comprador="Sumaqao", precio_venta_pactado_skg=19.80, fecha_entrega=datetime.date(2026, 8, 22), fecha_cobro=datetime.date(2026, 8, 26), precio_venta_real_skg=19.80, merma_pct=2.0, costos_skg=1.15, estado="cobrado")
        
        l4 = models.LoteDashboard(ciclo_id=c3.id, producto="cacao_fino", fecha_compra=datetime.date(2026, 9, 3), kg=2500, precio_compra_skg=21.00, comprador="Cacaosuyo", precio_venta_pactado_skg=26.50, fecha_entrega=datetime.date(2026, 9, 5), fecha_cobro=None, precio_venta_real_skg=None, merma_pct=0.0, costos_skg=0.95, estado="entregado") # Entregado pero sin cobrar
        l5 = models.LoteDashboard(ciclo_id=c3.id, producto="cafe_pergamino", fecha_compra=datetime.date(2026, 9, 8), kg=4200, precio_compra_skg=16.10, comprador=None, precio_venta_pactado_skg=None, fecha_entrega=None, fecha_cobro=None, precio_venta_real_skg=None, merma_pct=0.0, costos_skg=1.15, estado="comprado") # Alerta: Lote sin calzar
        
        db.add_all([l1, l2, l3, l4, l5])
        
        # Movimientos de caja (Flujo real)
        # Ingreso = kg * precio_venta * (1 - merma) - flete
        # Egreso = -kg * precio_compra
        m1 = models.MovimientoCaja(fecha=datetime.date(2026, 8, 5), tipo="otro", monto=-5200*16.20, nota="Egreso: Compra lote café C1")
        m2 = models.MovimientoCaja(fecha=datetime.date(2026, 8, 12), tipo="margen_cobrado", monto=5200*19.50*(1-0.018) - (5200*1.15), nota="Ingreso: Cobro lote café C1")
        
        m3 = models.MovimientoCaja(fecha=datetime.date(2026, 8, 10), tipo="otro", monto=-3800*13.80, nota="Egreso: Compra lote cacao C1")
        m4 = models.MovimientoCaja(fecha=datetime.date(2026, 8, 14), tipo="margen_cobrado", monto=3800*16.80*(1-0.012) - (3800*0.95), nota="Ingreso: Cobro lote cacao C1")
        
        m5 = models.MovimientoCaja(fecha=datetime.date(2026, 8, 18), tipo="otro", monto=-6100*16.50, nota="Egreso: Compra lote café C2")
        m6 = models.MovimientoCaja(fecha=datetime.date(2026, 8, 26), tipo="margen_cobrado", monto=6100*19.80*(1-0.02) - (6100*1.15), nota="Ingreso: Cobro lote café C2")
        
        m7 = models.MovimientoCaja(fecha=datetime.date(2026, 8, 31), tipo="gasto_fijo", monto=-2500.0, nota="Egreso: Gastos fijos Agosto")
        m8 = models.MovimientoCaja(fecha=datetime.date(2026, 9, 3), tipo="otro", monto=-2500*21.00, nota="Egreso: Compra cacao fino C3")
        
        db.add_all([m1, m2, m3, m4, m5, m6, m7, m8])
        print("Semilla: Ciclos, lotes y caja cargados con éxito.")

    # 9. Eventos de mercado iniciales
    if db.query(models.EventoMercado).count() == 0:
        e1 = models.EventoMercado(fecha=datetime.date(2026, 9, 1), titulo="Heladas en Brasil disparan cotización", detalle="Las bajas temperaturas en las regiones cafetaleras de Minas Gerais reducen proyecciones de cosecha e incrementan el valor internacional del café KC.", impacto="alcista", producto="cafe_pergamino")
        e2 = models.EventoMercado(fecha=datetime.date(2026, 9, 5), titulo="Buen clima en África Occidental estabiliza cacao", detalle="Lluvias favorables en Costa de Marfil alivian tensiones en el suministro de granos para la temporada principal que inicia en octubre.", impacto="bajista", producto="cacao_conv")
        db.add_all([e1, e2])
        print("Semilla: Eventos de mercado cargados con éxito.")

    db.commit()
