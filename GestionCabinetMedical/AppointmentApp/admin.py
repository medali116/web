from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_date', 'doctor', 'patient', 'duration_minutes', 'status')
    list_filter = ('status', 'doctor')
    search_fields = ('patient__last_name', 'doctor__last_name', 'reason')
