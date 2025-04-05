from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app.db.database import get_db
from app.schemas import DeviceStatCreate, DeviceStatResponse, StatsAnalysis, DeviceStat
from app.db.crud import save_device_stat, analyze_device_stats

router = APIRouter()


@router.post("/stats/", response_model=DeviceStatResponse)
async def create_stat(
    stat: DeviceStat,
    device_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    stat_with_id = DeviceStatCreate(device_id=device_id, **stat.model_dump())
    return await save_device_stat(db, stat_with_id)


@router.get("/stats/analyze/", response_model=StatsAnalysis)
async def get_analysis(
    device_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    analysis = await analyze_device_stats(db, device_id, start_time, end_time)

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data found for device_id={device_id}"
        )

    return analysis
