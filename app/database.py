import datetime
from typing import Dict, List, Any

# Precios referenciales del día
MARKET_PRICES = {
    "cacao_international": 6450.00,  # USD por tonelada métrica
    "cafe_international": 2.18,      # USD por libra (lb)
    "cacao_local": 21.50,            # PEN por kilogramo (Soles)
    "cafe_local": 13.80,             # PEN por kilogramo (Soles)
    "last_updated": datetime.datetime.now().isoformat()
}

# Historial de precios para simular gráficos
PRICE_HISTORY = {
    "cacao": [6200, 6250, 6300, 6280, 6400, 6450],
    "cafe": [2.05, 2.10, 2.15, 2.12, 2.16, 2.18],
    "dates": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
}

# Base de datos simulada de Blog Posts (Relación de aspecto Portada: 1200x630, Secundaria: 800x450)
BLOG_POSTS = [
    {
        "id": 1,
        "locale": "es",
        "title": "La Alianza con Cooperativas en Satipo: Sostenibilidad y Futuro",
        "summary": "Cómo el trabajo conjunto con productores locales en Satipo está transformando la calidad de exportación de nuestro cacao y café.",
        "content": "<p>En Hallpa Yaku S.A.C., creemos firmemente que la tierra y el agua solo dan sus mejores frutos cuando hay una relación justa y cercana con quienes la labran. Por ello, hemos fortalecido nuestra alianza directa con cooperativas locales en Satipo (región Junín), un área clave en la selva central del Perú.</p><h3>Agricultura de la mano de DEVIDA</h3><p>Gracias a los programas de desarrollo alternativo promovidos en coordinación con comunidades del medio y organizaciones aliadas, decenas de familias agricultoras han transitado hacia un modelo agroecológico tecnificado. Este cambio no solo asegura ingresos estables y dignos para ellos, sino que nos garantiza un cacao criollo fino de aroma de una pureza excepcional.</p><h3>La Importancia de la Trazabilidad</h3><p>Para el mercado internacional, la procedencia limpia y ética ya no es opcional. Es por eso que cada lote que exportamos cuenta con un registro detallado de la cooperativa de origen, el tipo de suelo y el agua utilizada en su riego. Trabajando en equipo con los agricultores locales, llevamos la riqueza de nuestra tierra (Hallpa) y la pureza del agua (Yaku) a los paladares más exigentes del mundo.</p>",
        "cover_image": "https://images.unsplash.com/photo-1516253593875-bd7ba052fbc5?auto=format&fit=crop&q=80&w=1200&h=630",
        "secondary_image": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&q=80&w=800&h=450",
        "author": "Dirección de Sostenibilidad",
        "date": "2026-06-28",
        "category": "Sostenibilidad"
    },
    {
        "id": 1,
        "locale": "en",
        "title": "Alliance with Cooperatives in Satipo: Sustainability and Future",
        "summary": "How working together with local producers in Satipo is transforming the export quality of our cocoa and coffee.",
        "content": "<p>At Hallpa Yaku S.A.C., we firmly believe that land and water only yield their best fruits when there is a fair and close relationship with those who till them. Therefore, we have strengthened our direct alliance with local cooperatives in Satipo (Junin region), a key area in Peru's central jungle.</p><h3>Agriculture hand in hand with local communities</h3><p>Thanks to alternative development programs promoted in coordination with local communities and allied organizations, dozens of farming families have transitioned towards a high-tech agroecological model. This change not only ensures stable and dignified incomes for them, but also guarantees us a fine aroma Creole cocoa of exceptional purity.</p><h3>The Importance of Traceability</h3><p>For the international market, clean and ethical sourcing is no longer optional. This is why every single lot we export has a detailed record of the cooperative of origin, soil type, and irrigation water. Working as a team with local farmers, we bring the richness of our land (Hallpa) and the purity of water (Yaku) to the most demanding palates in the world.</p>",
        "cover_image": "https://images.unsplash.com/photo-1516253593875-bd7ba052fbc5?auto=format&fit=crop&q=80&w=1200&h=630",
        "secondary_image": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&q=80&w=800&h=450",
        "author": "Sustainability Board",
        "date": "2026-06-28",
        "category": "Sustainability"
    },
    {
        "id": 2,
        "locale": "es",
        "title": "Temporada de Cosecha de Palta Hass en los Valles Andinos",
        "summary": "Iniciamos la selección y empaque de nuestra palta de exportación, destacando su cremosidad y calibre de primer nivel.",
        "content": "<p>Los valles andinos y costeros peruanos gozan de un clima privilegiado que permite una producción constante y de altísima calidad. Este mes damos inicio formal a la temporada fuerte de selección y empaque de nuestra Palta Hass premium.</p><h3>Clima y Riego de Alta Pureza</h3><p>Nuestra palta se cultiva con agua de deshielo andino cristalina, lo que favorece una concentración óptima de aceites naturales y le otorga esa cremosidad característica muy cotizada en Europa y Norteamérica. En planta de empaque, realizamos una selección manual rigurosa de calibres y sanidad para asegurar que cada fruta llegue en perfectas condiciones a su destino final.</p>",
        "cover_image": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?auto=format&fit=crop&q=80&w=1200&h=630",
        "secondary_image": "https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2?auto=format&fit=crop&q=80&w=800&h=450",
        "author": "Control de Calidad",
        "date": "2026-07-01",
        "category": "Cosecha"
    },
    {
        "id": 2,
        "locale": "en",
        "title": "Hass Avocado Harvest Season in Andean Valleys",
        "summary": "We start the selection and packing of our export avocado, highlighting its premium creaminess and high calibre.",
        "content": "<p>Peruvian Andean and coastal valleys enjoy a privileged climate that allows a constant and extremely high-quality production. This month we formally start the main season of selection and packing of our premium Hass Avocado.</p><h3>Climate and High-Purity Irrigation</h3><p>Our avocados are grown with crystalline Andean meltwater, which favors an optimal concentration of natural oils and gives them that characteristic creaminess highly sought after in Europe and North America. At the packing plant, we perform a rigorous manual selection of sizes and health to ensure that each fruit arrives in perfect condition at its final destination.</p>",
        "cover_image": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?auto=format&fit=crop&q=80&w=1200&h=630",
        "secondary_image": "https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2?auto=format&fit=crop&q=80&w=800&h=450",
        "author": "Quality Control",
        "date": "2026-07-01",
        "category": "Harvest"
    }
]

# Base de datos simulada de requerimientos de compra B2B (Tablero de Demandas)
DEMANDS = [
    {
        "id": 1,
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
        "id": 2,
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

# Datos de trazabilidad por Lote
LOTS = {
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

# Usuarios simulados y sus roles
USERS = {
    "admin@hallpayaku.com": {
        "email": "admin@hallpayaku.com",
        "name": "Administrador General",
        "name_en": "General Administrator",
        "role": "admin",
        "password_hash": "admin123"  # Contraseña plana para la simulación demo
    },
    "productor@hallpayaku.com": {
        "email": "productor@hallpayaku.com",
        "name": "Jorge Condori (Coop. Satipo)",
        "name_en": "Jorge Condori (Satipo Coop)",
        "role": "productor",
        "password_hash": "productor123"
    },
    "comprador@hallpayaku.com": {
        "email": "comprador@hallpayaku.com",
        "name": "Michael Green (EuroFoods)",
        "name_en": "Michael Green (EuroFoods)",
        "role": "comprador",
        "password_hash": "comprador123"
    }
}

# Datos del simulador de puertos y logística
PORTS_DATA = [
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

# Base de datos simulada de entregas y cosechas de productores
HARVEST_DELIVERIES = [
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

# Simulación de actualización de precios (se llama al consultar para simular cambios)
def update_prices_simulation():
    import random
    # Variación del ±1%
    MARKET_PRICES["cacao_international"] = round(MARKET_PRICES["cacao_international"] * random.uniform(0.99, 1.01), 2)
    MARKET_PRICES["cafe_international"] = round(MARKET_PRICES["cafe_international"] * random.uniform(0.99, 1.01), 2)
    MARKET_PRICES["cacao_local"] = round(MARKET_PRICES["cacao_local"] * random.uniform(0.992, 1.008), 2)
    MARKET_PRICES["cafe_local"] = round(MARKET_PRICES["cafe_local"] * random.uniform(0.992, 1.008), 2)
    MARKET_PRICES["last_updated"] = datetime.datetime.now().isoformat()
