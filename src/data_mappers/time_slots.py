from src.data_mappers.base import BaseDataMapper
from src.models.time_slots import TimeSlots
from src.schemas.time_slots import TimeSlotsResponse


class TimeSlotsDataMapper(BaseDataMapper):
    db_model = TimeSlots
    schema = TimeSlotsResponse
