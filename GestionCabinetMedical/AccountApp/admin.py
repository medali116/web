from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Doctor, Patient, Specialty, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('license_number', 'last_name', 'first_name', 'email', 'phone')
    search_fields = ('license_number', 'last_name', 'first_name')
    filter_horizontal = ('specialties',)

    def get_readonly_fields(self, request, obj=None):
        # license_number est un identifiant métier : non modifiable après création
        if obj is not None:
            return ('license_number',)
        return ()


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('national_id', 'last_name', 'first_name', 'birth_date', 'phone')
    search_fields = ('national_id', 'last_name', 'first_name')

    def get_readonly_fields(self, request, obj=None):
        # national_id est un identifiant métier : non modifiable après création
        if obj is not None:
            return ('national_id',)
        return ()
