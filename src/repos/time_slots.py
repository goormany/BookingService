from src.repos.base import BaseRepository
from src.data_mappers.time_slots import TimeSlotsDataMapper


class TimeSlotRepository(BaseRepository):
    mapper = TimeSlotsDataMapper
