# Import the admin module from Django's admin package
# This provides the ModelAdmin class used to configure the admin interface
from django.contrib import admin

# Import the Student model so it can be registered with the admin site
from .models import Student

# Decorate the class with @admin.register(Student) to register the model
# This tells Django to show a "Students" section in the admin back-end
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # list_display: the columns shown on the student list page in admin
    list_display = ['full_name', 'email', 'grade', 'is_active']

    # list_display_links: which columns act as clickable links to the detail page
    list_display_links = ['full_name', 'email']

    # search_fields: fields searched when the admin uses the search box
    search_fields = ['first_name', 'last_name']

    # list_filter: filters shown in the sidebar to narrow down the list
    list_filter = ['grade', 'is_active']

    # fieldsets: groups the fields into sections on the add/edit page
    fieldsets = (
        # Section 1: personal information fields
        ('Personal Information', {'fields': ('first_name', 'last_name', 'email', 'date_of_birth')}),
        # Section 2: academic information fields
        ('Academic Information', {'fields': ('grade', 'address', 'phone', 'is_active')}),
        # Section 3: parent/guardian information fields
        ('Parent/Guardian', {'fields': ('parent_name', 'parent_email', 'parent_phone')}),
    )

    # list_per_page: how many records to show per page in the admin list
    list_per_page = 25