from fastapi import APIRouter
from brave.api.config.config import get_settings
setting_controller = APIRouter()

@setting_controller.get("/setting/get-setting")
def get_setting():
    get_setting = get_settings()
    setting_dict = get_setting.__dict__
    return setting_dict