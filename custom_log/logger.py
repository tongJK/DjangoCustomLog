
import json
import logging
from django.utils import timezone

from custom_log import local


def get_system_log_message():
    system_log_message = json.dumps({
        "@timestamp": '%(asctime)s',
        "service": '%(service)s',
        "container_id": '%(container_id)s',
        "version": '%(version)s',
        "severity": "%(levelname)s",
        "type": "system",
        "message": "%(message)s, exec_info: %(traceback)s",
        "request_id": "%(request_id)s",
        "context": "%(_context)s",
        "payload": "%(payload)s",
        "api": {
            "method": "%(method)s",
            "api": "%(api)s",
            "status_code": "%(status_code)s",
            "processing_time": "%(processing_time)d",

        }
    })

    system_log_message = system_log_message.replace('"%(payload)s"', '%(payload)s')
    system_log_message = system_log_message.replace('"%(processing_time)d"', '%(processing_time)d')

    return system_log_message


def get_application_log_message():
    app_log_message = '{' \
                      '"@timestamp": "$asctime", ' \
                      f'"service": "$service", ' \
                      f'"version": "$version", ' \
                      f'"container_id": "$container_id", ' \
                      '"severity": "$levelname", ' \
                      '"type": "application", ' \
                      '"message": "$log_message", ' \
                      '"request_id": "$request_id", ' \
                      '"context": "$context", ' \
                      '"operation": $operation, ' \
                      '"payload": $payload' \
                      '}'

    return app_log_message


class ApplicationLogger:
    def __init__(self, message, **kwargs):
        self.time_stamp = timezone.localtime().strftime('%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger('application')
        self.type = 'application'
        self.extra = kwargs

        self.context = ""
        self.payload = {}
        self.operation = {}
        self._status_code = ""
        self.extra.update({'log_message': message})

    def get_log_message(self, severity):
        self.extra.update({
            "context": self.context,
            "payload": self.payload,
            "operation": self.operation,
            "_status_code": self._status_code,
        })

        local.payload = self.payload

        return ''

    def push_info(self):
        log_message = self.get_log_message('INFO')
        self.logger.info(log_message, extra=self.extra)

    def push_warning(self):
        log_message = self.get_log_message('WARNING')
        self.logger.warning(log_message, extra=self.extra)

    def push_error(self):
        log_message = self.get_log_message('ERROR')
        self.logger.error(log_message, extra=self.extra)

    def push_critical(self):
        log_message = self.get_log_message('CRITICAL')
        self.logger.critical(log_message, extra=self.extra)
