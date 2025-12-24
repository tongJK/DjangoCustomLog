
from django.conf import settings

from custom_log import local
from .utils.request_id_generator import generate_request_id

try:
    from django.utils.deprecation import MiddlewareMixin

except ImportError:
    MiddlewareMixin = object


class CustomRequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request):

        request_id = self._get_request_id(request)
        local.request_id = request_id   # Request ID from DSO (if None, generate it.)
        local.method = request.method   # HTTP Method [GET, POST, PATCH, ...]
        local.api = request.path    # API Path [eg.: /api/get_by_key]
        local.service = getattr(settings, 'PROJECT_NAME', '')    # Set this variable name in project settings.py
        local.version = getattr(settings, 'PROJECT_VERSION', '')    # Set this variable name in project settings.py

        request.id = request_id

    @staticmethod
    def process_response(request, response):
        local.status_code = response.status_code

        return response

    @staticmethod
    def _get_request_id(request):
        request_id_header = settings.REQUEST_ID_HEADER
        if not (request_id := request.META.get(request_id_header, None)):
            return generate_request_id()

        return request_id
