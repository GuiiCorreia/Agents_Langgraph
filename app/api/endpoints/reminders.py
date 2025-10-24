"""
Endpoints de Lembretes
Baseado nas chamadas HTTP do N8n: [FLUXO PRINCIPAL] e [INCLUI LEMBRETES]
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import User, Reminder
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse
)

router = APIRouter()


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria novo lembrete

    POST /api/reminders
    Headers: apikey, Accept: application/json
    Body: {
        "titulo": "string",
        "descricao": "string",
        "data_lembrete": "ISO datetime"
    }
    """
    new_reminder = Reminder(
        user_id=current_user.id,
        title=reminder.title,
        description=reminder.description,
        reminder_date=reminder.reminder_date,
        is_active=reminder.is_active,
        metadata=reminder.metadata,
        is_sent=False
    )

    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)

    return new_reminder


@router.get("/", response_model=List[ReminderResponse])
async def get_all_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os lembretes do usuário

    GET /api/reminders
    Headers: apikey
    """
    reminders = db.query(Reminder).filter(
        Reminder.user_id == current_user.id
    ).order_by(Reminder.reminder_date.asc()).all()

    return reminders


@router.get("/active", response_model=List[ReminderResponse])
async def get_active_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista lembretes ativos (não enviados)

    GET /api/reminders/active
    Headers: apikey
    """
    reminders = db.query(Reminder).filter(
        Reminder.user_id == current_user.id,
        Reminder.is_active == True,
        Reminder.is_sent == False
    ).order_by(Reminder.reminder_date.asc()).all()

    return reminders


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca lembrete específico por ID

    GET /api/reminders/{id}
    Headers: apikey
    """
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lembrete não encontrado"
        )
    return reminder


@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: int,
    reminder_update: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza lembrete existente

    PATCH /api/reminders/{id}
    Headers: apikey
    """
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lembrete não encontrado"
        )

    # Atualizar campos fornecidos
    update_data = reminder_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reminder, field, value)

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return reminder


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deleta lembrete

    DELETE /api/reminders/{id}
    Headers: apikey
    """
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lembrete não encontrado"
        )

    db.delete(reminder)
    db.commit()

    return None
