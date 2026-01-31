from fastapi import APIRouter, UploadFile

from src.services.images import ImagesService

router = APIRouter(prefix="/images", tags=["Изображения отелей"])


@router.post(
    "",
    summary="Загрузка изображения",
    description="<h1>Загрузите ваше изображение</h1>"
)
def upload_image(file: UploadFile):
    ImagesService().upload_image(file)

    # from fastapi import APIRouter, UploadFile, BackgroundTasks
    # def upload_image(file: UploadFile, background_tasks: BackgroundTasks)
    # background_tasks.add_task(resize_image, image_path)
    # return {"message": "Изображение загружено"}
