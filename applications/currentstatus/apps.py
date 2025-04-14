import os
from django.apps import AppConfig



class CurrentstatusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.currentstatus'
    
    def ready(self):
        from .scheduler import start_scheduler
        if os.environ.get('RUN_MAIN') == 'true':
            start_scheduler()
