from logger_conicle import local
from logger_conicle.log import REQUEST_ID_HEADER
from logger_conicle.utils.request_id_generator import generate_request_id


def get_header():
    if not getattr(local, 'request_id', ''):
        return {REQUEST_ID_HEADER: generate_request_id()}

    return {REQUEST_ID_HEADER: local.request_id}
