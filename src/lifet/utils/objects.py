import json

from lifet.utils.error import LifetError
def object_to_json(objectTarget: object) -> tuple[str | None, LifetError | None]:
    try:
        dict_data_object = objectTarget.__dict__
        return json.dumps(dict_data_object), None
    except:
        return None, LifetError('Error')
