import json

import requests
from celery import Task
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import status

from logger_conicle import local
from logger_conicle.utils.request_id_generator import generate_request_id
from micro_service.report_management.tracker import tracker_fail
from utils.redis import sadd, sismember, srem

BUFFER_TASKS = settings.BUFFER_TASKS
PROCESSING_KEY = settings.PROCESSING_KEY
QUEUING_KEY = settings.QUEUING_KEY


def get_error_detail(payload_data):
    return {
        'text': f"""
    🥹 *Fail Log Alert* 🥹
    ------------------------------
    🗿 *Tracker ID:*
        {str(payload_data.get('tracker_id', -1))}
    🐣 *Site / Environment:*
        `{payload_data['site']}`
    🐒 *Error info:*
        {payload_data['error']}
        """
    }

class BaseAlertTask(Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if not getattr(local, 'request_id', ''):
            local.request_id = generate_request_id()

        local._status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        local._context = json.dumps(kwargs, cls=DjangoJSONEncoder)

        if tracker_id := kwargs.get('tracker_id'):
            tracker_fail(tracker_id, str(einfo))
        if not settings.IS_LOCALHOST and not settings.TESTING:
            webhook_url = settings.BASE_ALERT_FAIL_WEBHOOK_URL
            if webhook_url:
                try:
                    payload = {
                        'error': str(einfo),
                        'tracker_id': kwargs.get('tracker_id', -1),
                        'site': settings.SITE_URL
                    }
                    error_detail = get_error_detail(payload)
                    response = requests.post(
                        webhook_url,
                        headers={'Content-Type': 'application/json; charset=UTF-8'},
                        data=json.dumps(error_detail)
                    )
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    pass

    def on_success(self, retval, task_id, args, kwargs):
        if not getattr(local, 'request_id', ''):
            local.request_id = generate_request_id()

        local._status_code = status.HTTP_200_OK
        local.payload = json.dumps(kwargs, cls=DjangoJSONEncoder)


    def apply_async(self, args=None, kwargs=None, **options):
        kwargs = kwargs or {}
        if self.name in BUFFER_TASKS:
            track_key = kwargs.get('track_key', None)
            if track_key is not None:
                if sismember(PROCESSING_KEY, track_key):
                    if not sismember(QUEUING_KEY, track_key):
                        sadd(QUEUING_KEY, track_key)
                    return None
                else:
                    sadd(PROCESSING_KEY, track_key)
        return super().apply_async(args, kwargs, **options)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        kwargs = kwargs or {}
        if self.name in BUFFER_TASKS:
            track_key = kwargs.get('track_key', None)
            srem(PROCESSING_KEY, track_key)

            if sismember(QUEUING_KEY, track_key):
                srem(QUEUING_KEY, track_key)
                current_priority = None
                if hasattr(self.request, 'delivery_info') and self.request.delivery_info.get('priority'):
                    current_priority = self.request.delivery_info.get('priority')
                self.apply_async(kwargs=kwargs, priority=current_priority)


class AlertAssignmentTask(BaseAlertTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super().on_failure(exc, task_id, args, kwargs, einfo)
        from assignment.models import Assignment
        tracker_id = kwargs.get('tracker_id')

        assignment = Assignment.objects.filter(tracker_id=tracker_id).first()
        if assignment:
            assignment.tracker_id = None
            assignment.save(update_fields=['tracker_id'])
