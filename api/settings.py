from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.database import get_db
from auth.dependencies import get_current_user
from models.settings import UserSettings
from api.schemas import UserSettingsResponse, UserSettingsUpdate

router = APIRouter()

# Get current user's settings
@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    settings = result.scalars().first()

    # If no settings exist, create default
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return settings


# Update user settings
@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    payload: UserSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    settings = result.scalars().first()

    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)
    return settings