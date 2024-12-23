import os
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from core.middleware import LogRoute


router = APIRouter(prefix="/video")

VIDEO_PATH = "video"


@router.post("/")
async def video_api():
    """
    通过stream推流视频
    """
    video_path = os.path.join(VIDEO_PATH, "test.mp4")

    def iter_file():
        with open(video_path, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iter_file(), media_type="video/mp4")
