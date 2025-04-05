from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app.schemas import LinkDeviceRequest, LinkDeviceResponse, UserStatsResponse, StatsAnalysis
from app.db.database import get_db
from app.db.crud import analyze_user_stats, analyze_device_stats_by_user, link_user_to_device

router = APIRouter()


# Привязка устройства к пользователю
@router.post("/user/link_device/", response_model=LinkDeviceResponse)
async def link_device(
    request: LinkDeviceRequest,
    db: AsyncSession = Depends(get_db)
):
    await link_user_to_device(db, request.user_id, request.device_id)
    return {"message": "Device linked successfully"}


# Анализ данных по всем устройствам пользователя (суммарная статистика)
@router.get("/user/{user_id}/stats", response_model=StatsAnalysis)
async def get_user_stats(
    user_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    result = await analyze_user_stats(db, user_id, start_time, end_time)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

    return result

# Анализ данных по каждому устройству пользователя
@router.get("/user/{user_id}/device_stats", response_model=UserStatsResponse)
async def get_device_stats_by_user(
    user_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    stats = await analyze_device_stats_by_user(
        db, user_id, start_time, end_time
    )

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    return UserStatsResponse(stats=stats)
