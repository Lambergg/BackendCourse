from datetime import date

from fastapi import HTTPException


class NabronirovalException(Exception):
    """
    Базовый класс для всех кастомных исключений приложения.

    Наследуется от стандартного `Exception`.
    Содержит общее поведение и атрибут `detail` по умолчанию.

    Атрибуты:
    - detail (str): Сообщение об ошибке, используемое по умолчанию.
    """
    detail = "Неожиданая ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(NabronirovalException):
    detail = "Объект не найден"


class RoomNotFoundException(NabronirovalException):
    detail = "Номер не найден"


class HotelNotFoundException(NabronirovalException):
    detail = "Отель не найден"


class ObjectAlreadyExistsException(NabronirovalException):
    detail = "Похожий объект уже существует"


class AllRoomsAreBookedException(NabronirovalException):
    detail = "Не осталось свободных комнат"


# === Валидационные функции ===
def check_date_to_after_date_from(date_from: date, date_to: date) -> None:
    """
    Проверяет, что дата выезда позже даты заезда.

    Параметры:
    - date_from (date): Дата заезда.
    - date_to (date): Дата выезда.

    Исключения:
    - HTTPException(422): если date_to <= date_from.

    Используется в сервисах для валидации входных данных.
    """
    if date_to <= date_from:
        raise HTTPException(status_code=422, detail="Дата заезда не может быть позже даты выезда")


# === HTTP-исключения (для ответа клиенту) ===
class NabronirovalHTTPException(HTTPException):
    """
    Базовый класс для всех HTTP-ошибок приложения.

    Наследуется от `HTTPException` FastAPI.
    Позволяет определить статус-код и детали ошибки.

    Атрибуты:
    - status_code (int): Код HTTP-ответа.
    - detail (str): Текст ошибки.
    """
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class HotelNotFoundHTTPException(NabronirovalHTTPException):
    status_code = 404
    detail = "Отель не найден"


class HotelIndexWrongHTTPException(NabronirovalHTTPException):
    status_code = 422
    detail = "Индекс не может быть меньше или равным нулю"


class HotelAlreadyExistsHTTPException(NabronirovalHTTPException):
    status_code = 422
    detail = "Такой отель уже существует"


class RoomNotFoundHTTPException(NabronirovalHTTPException):
    status_code = 404
    detail = "Номер не найден"


class RoomAlreadyExistsHTTPException(NabronirovalHTTPException):
    status_code = 422
    detail = "Номер с таким названием уже существует в этом отеле"


class RoomIndexWrongHTTPException(NabronirovalHTTPException):
    status_code = 422
    detail = "Индекс не может быть меньше или равным нулю"


class FacilitiesNotFoundHTTPException(NabronirovalHTTPException):
    status_code = 404
    detail = "Удобства не найдены"


class UserAllReadyExistsHTTPException(NabronirovalHTTPException):
    status_code = 409
    detail = "Пользователь с таким email уже зарегистрирован"


class UserPasswordToShortHTTPException(NabronirovalHTTPException):
    status_code = 422
    detail = "Пароль должен содержать минимум 8 символов"


class UserDeleteTokenHTTPException(NabronirovalHTTPException):
    status_code = 401
    detail = "Вы уже вышли из аккаунта"


class UserNotRegisterHTTPException(NabronirovalHTTPException):
    status_code = 401
    detail = "Пользователь с таким email не зарегистрирован"


class WrongPasswordHTTPException(NabronirovalHTTPException):
    status_code = 401
    detail = "Неверный пароль"


class AllRoomsAreBookedHTTPException(NabronirovalHTTPException):
    status_code = 409
    detail = "Не осталось свободных комнат"