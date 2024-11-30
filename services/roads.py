from core.dao import DAO
from models.roads import RoadModel
from services.common import Service

dao = DAO(RoadModel)


class RoadsService(Service):
    def __init__(self):
        super(RoadsService, self).__init__(dao)
