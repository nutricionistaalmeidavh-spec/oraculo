"""
API Endpoints para Alertas
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()


class AlertCreate(BaseModel):
    symbol: str
    zone_id: str
    condition: str  # "touch", "break", "approach"
    notification_type: List[str]  # ["email", "push", "webhook"]


class AlertResponse(BaseModel):
    id: str
    symbol: str
    zone_id: str
    condition: str
    active: bool
    created_at: datetime


# Mock database
_alerts_db = {}
_alert_counter = 0


@router.post("/", response_model=AlertResponse)
async def create_alert(alert: AlertCreate):
    """Cria um novo alerta de zona"""
    global _alert_counter
    _alert_counter += 1

    alert_id = f"alert_{_alert_counter}"
    _alerts_db[alert_id] = {
        "id": alert_id,
        "symbol": alert.symbol,
        "zone_id": alert.zone_id,
        "condition": alert.condition,
        "notification_type": alert.notification_type,
        "active": True,
        "created_at": datetime.now(),
        "triggered_at": None
    }

    return AlertResponse(**_alerts_db[alert_id])


@router.get("/")
async def list_alerts(symbol: Optional[str] = None):
    """Lista todos os alertas ativos"""
    alerts = list(_alerts_db.values())
    if symbol:
        alerts = [a for a in alerts if a["symbol"] == symbol]
    return {"alerts": alerts, "count": len(alerts)}


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    """Remove um alerta"""
    if alert_id in _alerts_db:
        del _alerts_db[alert_id]
        return {"message": "Alerta removido"}
    return {"error": "Alerta não encontrado"}
