import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from core.middleware import LogRoute


router = APIRouter(prefix="/video")

VIDEO_PATH = "videos"

# router.mount(f"/{VIDEO_PATH}", StaticFiles(directory=VIDEO_PATH), name="video")
# @router.get("/")
# async def video_api():
#     """
#     通过stream推流视频
#     """

#     video_path = os.path.join(VIDEO_PATH, "test.mp4")
#     return FileResponse(video_path)


@router.get("/list")
async def list_videos():
    """
    返回视频文件夹中的所有视频 URL
    """
    if not os.path.exists(VIDEO_PATH):
        raise HTTPException(status_code=404, detail="Video folder not found")

    video_files = [f for f in os.listdir(
        VIDEO_PATH) if os.path.isfile(os.path.join(VIDEO_PATH, f))]
    video_urls = [f"/{VIDEO_PATH}/{video}" for video in video_files]
    return {"videos": video_urls}
