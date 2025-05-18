from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from models import Folder, Flashcard
from database.database import get_db
from auth.dependencies import get_current_user
from api.schemas import FolderCreate, FolderResponse, FlashcardResponse
from api.flashcards import to_flashcard_response
import uuid

router = APIRouter()

@router.post("/folders", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_data: FolderCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    existing = await db.execute(select(Folder).where(Folder.user_id == user_id, Folder.name == folder_data.name))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Folder with this name already exists")

    new_folder = Folder(
        id=str(uuid.uuid4()),
        name=folder_data.name,
        user_id=user_id
    )
    db.add(new_folder)
    await db.commit()
    await db.refresh(new_folder)
    return new_folder

@router.get("/folders", response_model=list[FolderResponse])
async def list_folders(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    result = await db.execute(select(Folder).where(Folder.user_id == user_id))
    return result.scalars().all()

@router.delete("/folder/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    result = await db.execute(select(Folder).where(
        Folder.id == folder_id, Folder.user_id == user_id
    ))
    folder = result.scalars().first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    await db.delete(folder)
    await db.commit()

@router.put("/folder/{folder_id}", response_model=FolderResponse)
async def update_folder_name(folder_id: str, folder_data: FolderCreate, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)):
    result = await db.execute(select(Folder).where(Folder.id == folder_id, Folder.user_id == user_id))
    folder = result.scalars().first()

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    folder.name = folder_data.name

    await db.commit()
    await db.refresh(folder)
    return folder

@router.get("/folder/{folder_id}", response_model=FolderResponse)
async def get_folder_detail(
    folder_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    result = await db.execute(
        select(Folder).where(Folder.id == folder_id, Folder.user_id == user_id)
    )
    folder = result.scalars().first()

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    return folder

@router.get("/folder/{folder_id}/flashcards", response_model=list[FlashcardResponse])
async def get_flashcards_by_folder(
    folder_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    result = await db.execute(
        select(Flashcard).where(
            and_(
                Flashcard.folder_id == folder_id,
                Flashcard.user_id == user_id
            )
        )
    )
    flashcards = result.scalars().all()

    return [to_flashcard_response(f) for f in flashcards]