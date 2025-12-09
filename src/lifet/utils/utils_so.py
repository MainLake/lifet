import platform

from lifet.utils.objects import object_to_json

def get_info_so_json() -> (str | None):
    data_so = platform.uname()
    data_json, error = object_to_json(data_so)
    if error:
        return None
    return data_json
