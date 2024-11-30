from pydantic import BaseModel, Field


class RoadInfo(BaseModel):
    id: int = Field(description="ID of road")
