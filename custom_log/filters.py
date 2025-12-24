
import re
import logging

from django.conf import settings

from custom_log import local

def custom_record(record):
    processing_time = 0
    if record_args := getattr(record, 'args', None):
        if 'time_taken' in record_args:
            processing_time = record_args.get('time_taken', 0)

        elif 'runtime' in record_args:
            processing_time = record_args.get('runtime', 0)

    setattr(record, 'processing_time', processing_time)

    if not (status_code := getattr(local, 'status_code', '')):
        status_code = getattr(local, '_status_code', '')

    setattr(record, 'status_code', status_code)

    setattr(record, 'request_id', getattr(local, 'request_id', ''))
    setattr(record, 'method', getattr(local, 'method', ''))
    setattr(record, 'api', getattr(local, 'api', ''))
    setattr(record, '_context', getattr(local, '_context', ""))

    return record


class CustomRequestIDFilter(logging.Filter):

    def filter(self, record):
        if msg := getattr(record, 'msg', ''):
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            msg = ansi_escape.sub('', msg)
            msg = msg.replace('"', '')
            record.msg = msg

        record.log_message = msg

        if not getattr(record, 'context', None):
            record.context = {}

        if not getattr(record, 'operation', None):
            record.operation = {}

        record = custom_record(record)
        record.payload = getattr(local, 'payload', {})
        record.service = getattr(local, 'service', '')
        record.version = getattr(local, 'version', '')

        record.container_id = getattr(settings, 'CONTAINER_ID', '')

        return True


class CustomCeleryRequestIDFilter(logging.Filter):

    def filter(self, record):
        _ = custom_record(record)

        return True


class TracebackInfoFilter(logging.Filter):
    """Clear or restore the exception on log records"""
    def __init__(self, clear=True):
        super().__init__()
        self.clear = clear

    def filter(self, record):
        record.traceback = record.exc_info
        if self.clear:
            record._exc_info_hidden, record.exc_info = record.exc_info, None
            # clear the exception traceback text cache, if created.
            record.exc_text = None
        elif hasattr(record, "_exc_info_hidden"):
            record.exc_info = record._exc_info_hidden
            del record._exc_info_hidden
        return True
