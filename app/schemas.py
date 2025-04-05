from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional, List


class DeviceStat(BaseModel):
    x: float
    y: float
    z: float


class DeviceStatCreate(DeviceStat):
    device_id: str

    class Config:
        from_attributes = True    


class DeviceStatResponse(DeviceStat):
    id: int
    device_id: str
    timestamp: datetime

    class Config:
        from_attributes = True


class LinkDeviceRequest(BaseModel):
    user_id: str
    device_id: str


class UserStatsRequest(BaseModel):
    user_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class LinkDeviceResponse(BaseModel):
    message: str


class StatsAnalysis(BaseModel):
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    sum_value: float = 0
    count: int = 0
    median: Optional[float] = None


class UserStatsResponse(BaseModel):
    stats: Dict[str, StatsAnalysis]
