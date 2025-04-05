from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from .models import DeviceStat, User

from statistics import median
from datetime import datetime
from typing import Optional


async def save_device_stat(db: AsyncSession, device_stat):
    db_stat = DeviceStat(**device_stat.dict())
    db.add(db_stat)
    await db.commit()
    await db.refresh(db_stat)
    return db_stat


async def get_device_stats(
        db: AsyncSession,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
):
    query = select(DeviceStat).where(DeviceStat.device_id == device_id)
    if start_time:
        query = query.where(DeviceStat.timestamp >= start_time)
    if end_time:
        query = query.where(DeviceStat.timestamp <= end_time)

    result = await db.execute(query)
    return result.scalars().all()


async def analyze_device_stats(
        db: AsyncSession,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
):
    stats = await get_device_stats(db, device_id, start_time, end_time)

    if not stats:
        return None

    values = [s.x for s in stats] + [s.y for s in stats] + [s.z for s in stats]

    return {
        "min_value": min(values),
        "max_value": max(values),
        "sum_value": sum(values),
        "count": len(values),
        "median": median(values)
    }


async def get_user_device_stats(
    db: AsyncSession,
    user_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    query = select(DeviceStat).where(DeviceStat.user_id == user_id)

    if start_time:
        query = query.where(DeviceStat.timestamp >= start_time)
    if end_time:
        query = query.where(DeviceStat.timestamp <= end_time)

    result = await db.execute(query)
    return result.scalars().all()


async def analyze_user_stats(
        db: AsyncSession,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
):
    stats = await get_user_device_stats(db, user_id, start_time, end_time)

    if not stats:
        return None

    values = [s.x for s in stats] + [s.y for s in stats] + [s.z for s in stats]

    return {
        "min_value": min(values),
        "max_value": max(values),
        "sum_value": sum(values),
        "count": len(values),
        "median": median(values),
    }


async def analyze_device_stats_by_user(
        db: AsyncSession, user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
):
    stats = await get_user_device_stats(db, user_id, start_time, end_time)

    if not stats:
        return None

    result = {}
    for device in set(s.device_id for s in stats):
        device_stats = [s for s in stats if s.device_id == device]
        values = [s.x for s in device_stats] + [s.y for s in device_stats] + [s.z for s in device_stats]

        result[device] = {
            "min_value": min(values),
            "max_value": max(values),
            "sum_value": sum(values),
            "count": len(values),
            "median": median(values),
        }

    return result


async def link_user_to_device(db: AsyncSession, user_id: str, device_id: str):
    user_query = select(User).where(User.user_id == user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalars().first()

    if not user:
        new_user = User(user_id=user_id)
        db.add(new_user)
        await db.commit()

    update_query = (
        update(DeviceStat)
        .where(DeviceStat.device_id == device_id)
        .values(user_id=user_id)
    )
    await db.execute(update_query)
    await db.commit()
