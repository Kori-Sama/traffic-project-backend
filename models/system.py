from pydantic import BaseModel, Field


class Usage(BaseModel):
    cpu: str = Field(..., description="CPU usage percentage")
    memory: str = Field(..., description="Memory usage percentage")
    disk: str = Field(..., description="Disk usage percentage")


class Performance(BaseModel):
    rps: str = Field(..., description="Requests per second")
    time: str = Field(..., description="Time taken")
    user: str = Field(..., description="User count")


class SystemInfo(BaseModel):
    usage: Usage
    performance: Performance
