from django.contrib import admin
from .models import AlertEvent, EmergencyContact

admin.site.register(EmergencyContact)
admin.site.register(AlertEvent)
