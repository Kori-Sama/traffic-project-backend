from core.dao import DAO
from schemas.roads import RoadsSchema
from services.common import Service

dao = DAO(RoadsSchema)


class RoadsService(Service):
    def __init__(self):
        super(RoadsService, self).__init__(dao)
