from .logger_conf import init_logger
import os
from .settings import settings

try:
    if not os.path.exists(settings.DATA_PATH):
        os.makedirs(settings.DATA_PATH)
        print("Созданна дериктория данных")
    else:
        print("Дериктория данных существует")
except Exception as e:
    print(f"Ошибка создания директории")
    raise e

try:
    if not os.path.exists(settings.TEMP_DIR_PATH):
        os.makedirs(settings.TEMP_DIR_PATH)
        print("Созданна временная дериктория")
    else:
        print("Временная дериктория существует")
except Exception as e:
    print(f"Ошибка создания временной директории")
    raise e


logger = init_logger()