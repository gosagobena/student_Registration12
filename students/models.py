# Import the RegexValidator from Django's validators
# RegexValidator checks that a value matches a regular expression pattern
from django.core.validators import RegexValidator

# Import the models module from Django
# This module contains the base class Model and all field types (CharField, EmailField, etc.)
from django.db import models

# Define the list of grade choices available for students
# Each item is a tuple: (value stored in database, human-readable label)
GRADE_CHOICES = [
    ('9', 'Grade 9'),    # value '9' is stored, displayed as "Grade 9"
    ('10', 'Grade 10'),  # value '10' is stored, displayed as "Grade 10"
    ('11', 'Grade 11'),  # value '11' is stored, displayed as "Grade 11"
    ('12', 'Grade 12'),  # value '12' is stored, displayed as "Grade 12"
]

# Create a reusable validator for phone numbers
phone_validator = RegexValidator(
    regex=r'^\d{10}$',          # The pattern: start (^), exactly 10 digits (\d{10}), end ($)
    message='Phone number must be exactly 10 digits.',  # Error message shown when validation fails
)

# Define the Student model, which creates a "students_student" table in the database
class Student(models.Model):
    # --- Personal Information ---
    # first_name: a short text field holding up to 15 characters (the student's first name)
    first_name = models.CharField(max_length=15)
    # last_name: a short text field holding up to 15 characters (the student's last name)
    last_name = models.CharField(max_length=15)
    # email: an email address field; unique=True ensures no two students share the same email
    email = models.EmailField(unique=True)
    # address: a text field holding up to 100 characters (the student's home address)
    address = models.CharField(max_length=100)
    # phone: a text field of exactly 10 digits; the phone_validator enforces the format
    phone = models.CharField(max_length=10, validators=[phone_validator])

    # --- Academic Information ---
    # grade: stores one of the GRADE_CHOICES values ('9', '10', '11', '12')
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    # date_of_birth: stores the student's birth date as a calendar date
    date_of_birth = models.DateField()
    # is_active: boolean flag (True/False); defaults to True (student is active)
    is_active = models.BooleanField(default=True)

    # --- Parent/Guardian Information ---
    # parent_name: text field of up to 30 characters (guardian's full name)
    parent_name = models.CharField(max_length=30)
    # parent_email: email field; unique=True means each guardian email is distinct
    parent_email = models.EmailField(unique=True)
    # parent_phone: guardian's phone; also validated to be exactly 10 digits
    parent_phone = models.CharField(max_length=10, validators=[phone_validator])

    # Override the save() method to run custom logic before the record is written
    def save(self, *args, **kwargs):
        # Lowercase and remove surrounding spaces from the student's email
        # e.g. "John@Example.com " becomes "john@example.com"
        self.email = self.email.lower().strip()
        # Lowercase and remove surrounding spaces from the guardian's email
        self.parent_email = self.parent_email.lower().strip()
        # Call the parent class save() to actually write the record to the database
        super().save(*args, **kwargs)

    # String representation of a Student object (shown in admin and shell)
    def __str__(self):
        # Return the student's full name, e.g. "John Smith"
        return f"{self.first_name} {self.last_name}"

    # Helper method that returns the student's full name
    def full_name(self):
        # Concatenate first and last name with a space in between
        return f"{self.first_name} {self.last_name}"

    # Helper method to check whether the student is in high school
    def is_high_school_student(self):
        # Return True if the grade is 9, 10, 11, or 12
        return self.grade in ['9', '10', '11', '12']

    # Meta class: extra configuration for the model
    class Meta:
        # Default ordering of records: by last_name, then first_name (alphabetically)
        ordering = ['last_name', 'first_name']
        # Singular display name used in the Django admin
        verbose_name = 'Student'
        # Plural display name used in the Django admin
        verbose_name_plural = 'Students'