import psutil
from schemas.common import Response
from schemas.system import Performance, SystemInfo, Usage


class SystemService:
    def __init__(self):
        pass

    async def get_system_info(self) -> Response[SystemInfo]:
        return Response(
            data=SystemInfo(
                usage=await self.get_usage(),
                performance=await self.get_performance()
            )
        )

    async def get_usage(self) -> Usage:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')

        return Usage(
            cpu=f"{cpu_usage}%",
            memory=f"{memory_info.percent}%",
            disk=f"{disk_usage.percent}%"
        )

    async def get_performance(self) -> Performance:
        # Placeholder values for performance metrics
        # Replace these with actual performance metrics as needed
        return Performance(
            rps="1000",
            time="200ms",
            user="50"
        )
