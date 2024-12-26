# myproject/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_route.settings')

app = Celery('fuel_route')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')
# Define the queues  
app.conf.task_queues = {  
    'default': {  
        'exchange': 'default',  
        'routing_key': 'default'  
    },  
    'get_route_task': {  
        'exchange': 'get_route_task',  
        'routing_key': 'get_route_task'  
    },  
        'generate_route_map_task': {  
        'exchange': 'generate_route_map_task',  
        'routing_key': 'generate_route_map_task'  
    },
        'find_fuel_stops_task': {  
        'exchange': 'find_fuel_stops_task',  
        'routing_key': 'find_fuel_stops_task'  
    }    
}  

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()