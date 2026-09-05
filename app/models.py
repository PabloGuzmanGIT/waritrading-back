import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, JSON, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base

# 1. Usuarios
class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_en = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, productor, comprador
    password_hash = Column(String, nullable=False)

# 2. Artículos de Blog
class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    locale = Column(String, nullable=False)  # es, en
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    content = Column(String, nullable=False)
    cover_image = Column(String, nullable=False)
    secondary_image = Column(String, nullable=True)
    author = Column(String, nullable=False)
    date = Column(String, nullable=False)  # YYYY-MM-DD
    category = Column(String, nullable=False)

# 3. Tablero de Demandas B2B (Requerimientos Anónimos Públicos)
class Demand(Base):
    __tablename__ = "demands"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String, nullable=False)
    company_tax_id = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    country = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    product = Column(String, nullable=False)
    product_en = Column(String, nullable=False)
    quantity_tons = Column(Float, nullable=False)
    target_price = Column(String, nullable=False)
    destination_port = Column(String, nullable=False)
    destination_port_en = Column(String, nullable=False)
    date_posted = Column(String, nullable=False)  # YYYY-MM-DD
    is_verified = Column(Boolean, default=True)

# 4. Trazabilidad QR / Lotes (Acceso Público)
class TraceabilityLot(Base):
    __tablename__ = "traceability_lots"

    lot_code = Column(String, primary_key=True, index=True)
    product = Column(String, nullable=False)
    product_en = Column(String, nullable=False)
    cooperative = Column(String, nullable=False)
    cooperative_en = Column(String, nullable=False)
    region = Column(String, nullable=False)
    harvest_date = Column(String, nullable=False)  # YYYY-MM-DD
    packing_date = Column(String, nullable=False)  # YYYY-MM-DD
    soil_metrics = Column(JSON, nullable=False)  # Contiene ph, organic_matter, etc.
    water_metrics = Column(JSON, nullable=False)  # Contiene source, purity_level, etc.
    destination_port = Column(String, nullable=False)
    destination_port_en = Column(String, nullable=False)
    shipment_date = Column(String, nullable=False)  # YYYY-MM-DD
    status = Column(String, nullable=False)
    status_en = Column(String, nullable=False)

# 5. Formulario de Contacto General
class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    company = Column(String, nullable=True)
    country = Column(String, nullable=False)
    product_interest = Column(String, nullable=False)
    volume_tons = Column(Float, nullable=True)
    message = Column(String, nullable=False)
    date_received = Column(String, nullable=False)  # ISO Datetime string

# 6. Puertos Logística
class PortLogistics(Base):
    __tablename__ = "ports_logistics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    port = Column(String, nullable=False)
    port_en = Column(String, nullable=False)
    transit_days = Column(Integer, nullable=False)
    temperature_c = Column(Float, nullable=False)
    humidity_pct = Column(Integer, nullable=False)
    ventilation_cbm = Column(Integer, nullable=False)

# 7. Cosechas y Entregas (Flujo Productor / Administrador)
class HarvestDelivery(Base):
    __tablename__ = "harvest_deliveries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(String, nullable=False)  # YYYY-MM-DD
    product = Column(String, nullable=False)
    weight_kg = Column(Float, nullable=False)
    proposed_price_pen_kg = Column(Float, nullable=True)
    location = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Registrado")  # Registrado, En Negociación, Precio Acordado, Completado
    price_paid_pen = Column(Float, default=0.0)
    producer_name = Column(String, nullable=False)
    producer_email = Column(String, nullable=False)

# 8. Precios calculados cada mañana (Precios Diarios)
class PrecioDiario(Base):
    __tablename__ = "precios_diarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    producto = Column(String, nullable=False)  # cafe_pergamino, cacao_conv, cacao_fino
    cotizacion_intl = Column(Float, nullable=False)      # ¢/lb café | US$/t cacao
    tipo_cambio = Column(Float, nullable=False)
    paridad_skg = Column(Float, nullable=False)          # valor teórico S//kg
    compra_max_skg = Column(Float, nullable=False)       # según fórmula (costos 1.15 café / 0.95 cacao)
    compra_publicada_skg = Column(Float, nullable=True)  # ajuste manual
    venta_ref_skg = Column(Float, nullable=True)         # mejor cotización exportador
    fuente = Column(String, default="n8n")

    __table_args__ = (
        CheckConstraint(producto.in_(['cafe_pergamino', 'cacao_conv', 'cacao_fino']), name='chk_producto_valido'),
    )

# 9. Lotes Comprados para Dashboard
class LoteDashboard(Base):
    __tablename__ = "lotes_dashboard"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ciclo_id = Column(Integer, ForeignKey("ciclos.id"), nullable=True)
    producto = Column(String, nullable=False)
    fecha_compra = Column(Date, nullable=False)
    kg = Column(Float, nullable=False)
    precio_compra_skg = Column(Float, nullable=False)
    humedad_pct = Column(Float, nullable=True)
    comprador = Column(String, nullable=True)                        # exportador comprometido
    precio_venta_pactado_skg = Column(Float, nullable=True)          # NULL = alerta sin calzar
    fecha_entrega = Column(Date, nullable=True)
    fecha_cobro = Column(Date, nullable=True)
    precio_venta_real_skg = Column(Float, nullable=True)
    merma_pct = Column(Float, default=0.0)
    costos_skg = Column(Float, default=1.15)                         # flete+estiba+retención
    estado = Column(String, default="comprado")                      # comprado, consolidado, entregado, cobrado, cancelado
    comentario = Column(String, nullable=True)                       # comentario o motivo de cancelación/edición

    ciclo = relationship("Ciclo", back_populates="lotes")

    __table_args__ = (
        CheckConstraint(estado.in_(['comprado', 'consolidado', 'entregado', 'cobrado', 'cancelado']), name='chk_estado_valido'),
    )

# 10. Agrupador quincenal de rotación (Ciclos)
class Ciclo(Base):
    __tablename__ = "ciclos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)                           # ej. '2026-08-C1'
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    capital_desplegado = Column(Float, nullable=True)
    estado = Column(String, default="activo")                         # activo, cerrado

    lotes = relationship("LoteDashboard", back_populates="ciclo")

# 11. Proyección del escenario base
class ProyeccionMensual(Base):
    __tablename__ = "proyeccion_mensual"

    mes = Column(Date, primary_key=True)  # Primer día del mes
    margen_plan = Column(Float, nullable=False)
    cuota_plan = Column(Float, nullable=False)
    gastos_plan = Column(Float, nullable=False)
    caja_plan = Column(Float, nullable=False)

# 12. Registro de eventos de mercado
class EventoMercado(Base):
    __tablename__ = "eventos_mercado"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    titulo = Column(String, nullable=False)
    detalle = Column(String, nullable=False)
    impacto = Column(String, nullable=False)  # alcista, bajista, neutro
    producto = Column(String, nullable=True)

    __table_args__ = (
        CheckConstraint(impacto.in_(['alcista', 'bajista', 'neutro']), name='chk_impacto_valido'),
    )

# 13. Pagos de cuotas, préstamos y gastos de caja
class MovimientoCaja(Base):
    __tablename__ = "movimientos_caja"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    tipo = Column(String, nullable=False)  # cuota, gasto_fijo, margen_cobrado, otro
    monto = Column(Float, nullable=False)
    nota = Column(String, nullable=True)

    __table_args__ = (
        CheckConstraint(tipo.in_(['cuota', 'gasto_fijo', 'margen_cobrado', 'otro']), name='chk_tipo_caja_valido'),
    )
