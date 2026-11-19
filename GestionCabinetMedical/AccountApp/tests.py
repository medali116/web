from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Doctor, Patient, Specialty


class AccountModelsTests(TestCase):

    def make_patient(self, **kw):
        data = dict(username='p1', national_id='12345678', phone='98765432',
                    birth_date=date(2000, 1, 1), first_name='Sami', last_name='Trabelsi')
        data.update(kw)
        p = Patient(**data)
        p.set_password('Secret123!')
        return p

    def make_doctor(self, **kw):
        data = dict(username='dr1', license_number='123456', phone='22334455',
                    first_name='Ali', last_name='Ben Salah')
        data.update(kw)
        d = Doctor(**data)
        d.set_password('Secret123!')
        return d

    def test_auth_user_model(self):
        self.assertEqual(get_user_model()._meta.label, 'AccountApp.User')

    def test_doctor_and_patient_are_users(self):
        p = self.make_patient()
        p.full_clean()
        p.save()
        User = get_user_model()
        self.assertEqual(p.pk, User.objects.get(username='p1').pk)  # user_ptr conservé
        self.assertTrue(issubclass(Doctor, User))

    def test_license_number_length_6(self):
        with self.assertRaises(ValidationError):
            self.make_doctor(license_number='12345').full_clean()
        self.make_doctor().full_clean()

    def test_license_number_unique(self):
        self.make_doctor().save()
        with self.assertRaises(ValidationError):
            self.make_doctor(username='dr2').full_clean()

    def test_national_id_8_digits(self):
        for bad in ('1234567', '123456789', '1234567a'):
            with self.assertRaises(ValidationError):
                self.make_patient(national_id=bad).full_clean()

    def test_national_id_unique(self):
        self.make_patient().save()
        with self.assertRaises(ValidationError):
            self.make_patient(username='p2').full_clean()

    def test_phone_8_digits(self):
        with self.assertRaises(ValidationError):
            self.make_patient(phone='abc').full_clean()

    def test_birth_date_must_be_past(self):
        with self.assertRaises(ValidationError):
            self.make_patient(birth_date=timezone.localdate()).full_clean()
        with self.assertRaises(ValidationError):
            self.make_patient(birth_date=timezone.localdate() + timedelta(days=1)).full_clean()

    def test_specialties_many_to_many(self):
        d = self.make_doctor()
        d.save()
        cardio = Specialty.objects.create(name='Cardiologie')
        pedia = Specialty.objects.create(name='Pédiatrie')
        d.specialties.add(cardio, pedia)
        self.assertEqual(d.specialties.count(), 2)
        self.assertIn(d, cardio.doctors.all())
