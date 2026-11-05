"""Avisos por correo de las consultas del formulario web (vía API de Resend).

Se usa HTTPS porque Railway bloquea SMTP saliente en los planes Free/Trial/Hobby.
Un fallo aquí nunca debe afectar al visitante: la consulta ya está guardada en la
BD antes de intentar el envío, así que los errores solo se registran en el log.
"""
import json
import logging
import urllib.error
import urllib.request

from app.database import settings

logger = logging.getLogger("uvicorn.error")

RESEND_URL = "https://api.resend.com/emails"


def _one_line(value: str) -> str:
    return " ".join(value.split())


def build_contact_email(contact) -> dict:
    """Arma el correo interno; `reply_to` permite responderle directo al cliente."""
    rows = [
        ("Nombre", contact.name),
        ("Correo", contact.email),
        ("Empresa", contact.company),
        ("País", contact.country),
        ("Interés", contact.product_interest),
        ("Volumen", f"{contact.volume_tons} TM" if contact.volume_tons is not None else None),
    ]
    summary = "\n".join(f"{label}: {value}" for label, value in rows if value)
    # Sin correo no se envía `reply_to`: el contacto va por teléfono dentro del detalle.
    reply_to = {"reply_to": contact.email} if contact.email else {}
    return {
        "from": settings.CONTACT_EMAIL_FROM,
        "to": settings.contact_email_to_list,
        **reply_to,
        "subject": _one_line(f"Nueva consulta web: {contact.name} - {contact.product_interest}")[:150],
        "text": f"{summary}\n\nDetalle:\n{contact.message}\n",
    }


def send_contact_notification(contact) -> None:
    if not settings.contact_email_enabled:
        logger.warning("Aviso de contacto omitido: faltan variables de correo.")
        return

    request = urllib.request.Request(
        RESEND_URL,
        data=json.dumps(build_contact_email(contact)).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
            # El User-Agent por defecto de urllib puede ser rechazado por el WAF.
            "User-Agent": "wari-trading-backend/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10):
            pass
    except urllib.error.HTTPError as exc:
        detail = exc.read(300).decode("utf-8", "replace")
        logger.error("Resend rechazó el aviso de contacto (%s): %s", exc.code, detail)
    except Exception as exc:
        logger.error("No se pudo enviar el aviso de contacto: %s", exc)
