from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase, override_settings
from django.utils import timezone

from AccountApp.models import Doctor, Patient

from .models import Appointment


@override_settings(MEDIA_ROOT='/tmp/test_media')
class AppointmentTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.doctor = Doctor.objects.create(username='dr1', license_number='123456', phone='22334455')
        cls.patient = Patient.objects.create(username='p1', national_id='12345678',
                                             phone='98765432', birth_date=date(2000, 1, 1))

    def future(self, days=2):
        return timezone.now() + timedelta(days=days)

    def make(self, **kw):
        data = dict(doctor=self.doctor, patient=self.patient,
                    appointment_date=self.future(), reason='Contrôle')
        data.update(kw)
        return Appointment(**data)

    def test_defaults(self):
        a = self.make()
        a.full_clean()
        a.save()
        self.assertEqual(a.status, Appointment.Status.PENDING)
        self.assertEqual(a.duration_minutes, 30)
        self.assertIsNotNone(a.created_at)
        self.assertIsNotNone(a.updated_at)

    def test_status_choices(self):
        self.assertEqual(set(Appointment.Status.values), {'PENDING', 'CONFIRMED', 'CANCELLED'})

    def test_date_in_past_rejected_on_create(self):
        with self.assertRaises(ValidationError):
            self.make(appointment_date=timezone.now() - timedelta(hours=1)).full_clean()

    def test_past_appointment_still_editable(self):
        a = self.make()
        a.save()
        Appointment.objects.filter(pk=a.pk).update(appointment_date=timezone.now() - timedelta(days=1))
        a.refresh_from_db()
        a.status = Appointment.Status.CONFIRMED
        a.prescription = SimpleUploadedFile('ordonnance.pdf', b'%PDF-1.4')
        a.full_clean()  # ne doit pas lever d'erreur

    def test_changing_date_to_past_rejected(self):
        a = self.make()
        a.save()
        a.appointment_date = timezone.now() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            a.full_clean()

    def test_prescription_only_pdf(self):
        a = self.make(prescription=SimpleUploadedFile('ordonnance.docx', b'x'))
        with self.assertRaises(ValidationError):
            a.full_clean()

    def test_prescription_optional(self):
        self.make().full_clean()

    def test_unique_doctor_date(self):
        when = self.future()
        self.make(appointment_date=when).save()
        with self.assertRaises(ValidationError):
            self.make(appointment_date=when).full_clean()
        with self.assertRaises(IntegrityError):
            self.make(appointment_date=when).save()

    def test_same_couple_several_appointments(self):
        self.make(appointment_date=self.future(1)).save()
        self.make(appointment_date=self.future(3)).save()
        self.assertEqual(self.patient.appointments.filter(doctor=self.doctor).count(), 2)

    def test_ordering(self):
        late = self.make(appointment_date=self.future(5))
        late.save()
        early = self.make(appointment_date=self.future(1))
        early.save()
        self.assertEqual(list(Appointment.objects.all()), [early, late])
