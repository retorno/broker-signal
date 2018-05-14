# -*- coding: utf-8 -*-
import os
from celery import Celery
# from django.conf import settings


class WorkerConnect(object):

    @classmethod
    def __init__(self, broker_url=None, backend_url=None):

        if broker_url is None:
            broker_url = os.environ.get('WORKER_BROKER_URL')

        if backend_url is None:
            backend_url = os.environ.get('WORKER_BACKEND_URL')

        if hasattr(self, 'celery') is False:
            self.celery = Celery(
                'worker',
                broker=broker_url,
                backend=backend_url)
        else:
            pass

    def execute(self, task_name, option='delay', countdown=0, args=None):

        # route_dict = getattr(settings, 'CELERY_ROUTES', None)
        # default_queue = getattr(settings, 'CELERY_DEFAULT_QUEUE', 'celery')
        route_dict = os.environ.get('CELERY_ROUTES', None)
        default_queue = os.environ.get('CELERY_DEFAULT_QUEUE', 'celery')

        if not route_dict:
            queue = default_queue
        else:
            queue = route_dict.get(task_name, {}).get('queue', default_queue)

        if args is not None:
            data = args
        else:
            data = None

        if not data:
            return {
                'status': 'erro',
                'code': 500,
                'msg': 'no args'
            }

        if option == 'get':
            celery_response = self.celery.signature(
                task_name,
                kwargs=data,
                countdown=countdown,
                options={
                    'queue': queue
                }
            ).delay().get(timeout=60)

            return {
                'status': 'success',
                'code': 200,
                'data': celery_response
            }
        else:
            celery_response = self.celery.signature(
                task_name,
                kwargs=data,
                countdown=countdown,
                options={
                    'queue': queue
                }
            ).delay()

            if celery_response.status in ['SUCCESS', 'PENDING']:
                return {
                    'status': 'success',
                    'code': 200
                }
            else:
                return {
                    'status': 'success',
                    'code': 500
                }
