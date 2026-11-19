from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone


# --- Validators -------------------------------------------------------------

phone_validator = RegexValidator(
    regex=r'^\d{8}$',
    message="Le numéro de téléphone doit contenir exactement 8 chiffres.",
)

national_id_validator = RegexValidator(
    regex=r'^\d{8}$',
    message="Le numéro de CIN doit contenir exactement 8 chiffres.",
)


def validate_past_date(value):
    """birth_date doit être strictement antérieure à la date du jour."""
    if value >= timezone.localdate():
        raise ValidationError(
            "La date de naissance doit être antérieure à la date du jour."
        )


# --- Modèle utilisateur personnalisé ---------------------------------------

class User(AbstractUser):
    """Hérite de AbstractUser sans rien ajouter : point d'extension du projet."""
    pass


# --- Specialty --------------------------------------------------------------

class Specialty(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Spécialité"
        verbose_name_plural = "Spécialités"

    def __str__(self):
        return self.name


# --- Doctor (héritage multi-tables de User) --------------------------------

class Doctor(User):
    # id hérité (lien user_ptr) conservé comme clé primaire
    license_number = models.CharField(
        max_length=6,
        unique=True,
        validators=[MinLengthValidator(6)],
    )
    phone = models.CharField(max_length=8, validators=[phone_validator])
    specialties = models.ManyToManyField(Specialty, related_name='doctors')

    class Meta:
        verbose_name = "Médecin"
        verbose_name_plural = "Médecins"

    def __str__(self):
        return f"Dr {self.first_name} {self.last_name}"


# --- Patient (héritage multi-tables de User) -------------------------------

class Patient(User):
    # id hérité (lien user_ptr) conservé : patient.pk == request.user.pk
    national_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[national_id_validator],
    )
    phone = models.CharField(max_length=8, validators=[phone_validator])
    birth_date = models.DateField(validators=[validate_past_date])

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.national_id})"
