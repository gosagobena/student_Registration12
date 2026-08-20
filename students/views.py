# render: renders a template with context data
# redirect: sends the browser to another URL
# get_object_or_404: fetches an object or raises a 404 error if not found
from django.shortcuts import render, redirect, get_object_or_404

# messages: framework for showing one-time success/error messages to the user
from django.contrib import messages

# user_passes_test: decorator that restricts a view to users who pass a test
from django.contrib.auth.decorators import user_passes_test

# login: logs an authenticated user into the session
from django.contrib.auth import login as auth_login

# logout: logs the current user out of the session
from django.contrib.auth import logout as auth_logout

# AuthenticationForm: Django's built-in form for username + password login
from django.contrib.auth.forms import AuthenticationForm

# Q: object used to build complex OR/AND queries on the database
from django.db.models import Q

# datetime: provides the strptime function used to parse date strings
from datetime import datetime

# Import the Student model and the phone_validator from the models file
from .models import Student, phone_validator

# Create a decorator that only allows staff users (admins) into a view
# If a non-staff user tries to access the view, they are redirected to 'students:login'
admin_required = user_passes_test(lambda u: u.is_staff, login_url='students:login')

# Helper function that validates and converts a date string into a date object
def parse_date_field(value, label):
    # Remove leading/trailing spaces; if nothing is provided, use an empty string
    value = (value or '').strip()
    # If the value is empty, raise an error saying the field is required
    if not value:
        raise ValueError(f"{label} is required.")
    try:
        # Try to convert the text into a date using the YYYY-MM-DD format (e.g. 2026-08-19)
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        # If parsing fails, raise a friendly error telling the user the expected format
        raise ValueError(f"{label} must be in YYYY-MM-DD format.")

# Login view: lets an admin/staff user sign in
def login_view(request):
    # Only handle the form data if the request method is POST (form submitted)
    if request.method == 'POST':
        # Create the authentication form filled with the submitted username/password
        form = AuthenticationForm(request, data=request.POST)
        # If the credentials are correct...
        if form.is_valid():
            # Get the authenticated user object from the form
            user = form.get_user()
            # Start a login session for this user
            auth_login(request, user)
            # Staff go to the student list; regular users go home
            if user.is_staff:
                return redirect('students:student_list')
            return redirect('students:home')
    else:
        # For a GET request, create an empty authentication form
        form = AuthenticationForm(request)

    # Render the login page, passing the form to the template
    return render(request, 'login.html', {'form': form})

# Logout view: signs the current user out
def logout_view(request):
    # End the current user's session
    auth_logout(request)
    # Send the user back to the home page
    return redirect('students:home')

# Home page view: shows statistics about the students
def home(request):
    # Count the total number of student records in the database
    total_students = Student.objects.count()
    # Count only the students who are marked as active
    active_students = Student.objects.filter(is_active=True).count()
    # Count students whose grade is 9 or higher (grade__gte=9 means grade >= 9)
    high_school = Student.objects.filter(grade__gte=9).count()

    # Build a dictionary of data to pass to the template
    context = {
        'total_students': total_students,                          # total count
        'active_students': active_students,                        # active count
        'high_school': high_school,                                # high school count
        'recent_students': Student.objects.all()[:5],              # first 5 students
    }
    # Render the home template with the context data
    return render(request, 'home.html', context)

# Student list view: shows all students (admin only)
@admin_required  # Only staff users can access this page
def student_list(request):
    # Fetch every student record from the database
    students = Student.objects.all()
    # Put the queryset into the context
    context = {'students': students}
    # Render the student list template
    return render(request, 'student_list.html', context)

# Register student view: lets anyone create a new student record
def register_student(request):
    # Only process the data if the form was submitted (POST request)
    if request.method == 'POST':
        try:  # Wrap everything in try/except so errors show a friendly message
            # Get the phone numbers from the form (empty string if not provided)
            phone = request.POST.get('phone', '')
            parent_phone = request.POST.get('parent_phone', '')
            # Loop over both phone fields to validate them
            for value, field in [(phone, 'Phone'), (parent_phone, 'Parent phone')]:
                # If the value is not empty and does not match the 10-digit pattern...
                if value and not phone_validator.regex.match(value):
                    # ...raise an error message naming the field
                    raise ValueError(f"{field} number must be exactly 10 digits.")

            # Create a new Student object from the submitted form data
            student = Student(
                first_name=request.POST['first_name'],                        # first name from form
                last_name=request.POST['last_name'],                          # last name from form
                email=request.POST['email'],                                  # email from form
                grade=request.POST['grade'],                                  # grade from form
                date_of_birth=parse_date_field(request.POST.get('date_of_birth'), 'Date of birth'),  # validated date
                address=request.POST.get('address', ''),                      # address (optional)
                phone=phone,                                                  # validated phone
                parent_name=request.POST.get('parent_name', ''),              # guardian name (optional)
                parent_phone=parent_phone,                                    # validated guardian phone
                parent_email=request.POST.get('parent_email', ''),            # guardian email (optional)
            )
            # Save the new student record to the database
            student.save()
            # Show a success message including the student's full name
            messages.success(request, f"Student {student.full_name()} registered successfully!")
            # If the current user is a staff member, go to the student list
            if request.user.is_staff:
                return redirect('students:student_list')
            # Otherwise (a regular visitor), go back to the home page
            return redirect('students:home')
        except Exception as e:  # Catch any error that happened above
            # Show the error message to the user on the page
            messages.error(request, f"Error: {e}")

    # For a GET request (or after a failed save), show the registration form
    return render(request, 'register.html')

# Student detail view: shows one student's full information (admin only)
@admin_required  # Only staff users can access this page
def student_detail(request, student_id):
    # Fetch the student by its ID; raise 404 if it does not exist
    student = get_object_or_404(Student, id=student_id)
    # Put the student into the context
    context = {'student': student}
    # Render the student detail template
    return render(request, 'student_detail.html', context)

# Edit student view: updates an existing student (admin only)
@admin_required  # Only staff users can access this page
def edit_student(request, student_id):
    # Fetch the student to edit; raise 404 if it does not exist
    student = get_object_or_404(Student, id=student_id)

    # Only process the data if the form was submitted (POST request)
    if request.method == 'POST':
        try:  # Wrap everything in try/except so errors show a friendly message
            # Update each field of the student from the submitted form data
            student.first_name = request.POST['first_name']                                     # new first name
            student.last_name = request.POST['last_name']                                       # new last name
            student.email = request.POST['email']                                               # new email
            student.grade = request.POST['grade']                                               # new grade
            student.date_of_birth = parse_date_field(request.POST.get('date_of_birth'), 'Date of birth')  # new validated date
            student.address = request.POST.get('address', '')                                   # new address (optional)
            phone = request.POST.get('phone', '')                                               # new phone
            parent_phone = request.POST.get('parent_phone', '')                                 # new guardian phone
            # Loop over both phone fields to validate them
            for value, field in [(phone, 'Phone'), (parent_phone, 'Parent phone')]:
                # If the value is not empty and does not match the 10-digit pattern...
                if value and not phone_validator.regex.match(value):
                    # ...raise an error message naming the field
                    raise ValueError(f"{field} number must be exactly 10 digits.")
            # Assign the validated phone numbers back to the student
            student.phone = phone
            student.parent_name = request.POST.get('parent_name', '')                           # new guardian name
            student.parent_phone = parent_phone                                                 # validated guardian phone
            student.parent_email = request.POST.get('parent_email', '')                         # new guardian email
            # Save the updated student record to the database
            student.save()
            # Show a success message
            messages.success(request, f"Student {student.full_name()} updated successfully!")
            # Go back to the detail page of the edited student
            return redirect('students:student_detail', student_id=student.id)
        except Exception as e:  # Catch any error that happened above
            # Show the error message to the user on the page
            messages.error(request, f"Error: {e}")

    # Put the student into the context for the edit form
    context = {'student': student}
    # Render the edit template (pre-filled with the student's current data)
    return render(request, 'edit_student.html', context)

# Delete student view: removes a student (admin only)
@admin_required  # Only staff users can access this page
def delete_student(request, student_id):
    # Fetch the student to delete; raise 404 if it does not exist
    student = get_object_or_404(Student, id=student_id)

    # Only delete if the request is a POST (form confirmation submitted)
    if request.method == 'POST':
        # Remove the student record from the database
        student.delete()
        # Show a success message
        messages.success(request, f"Student {student.full_name()} deleted successfully!")
        # Go back to the student list page
        return redirect('students:student_list')

    # Put the student into the context for the confirmation page
    context = {'student': student}
    # Render the delete confirmation template
    return render(request, 'delete_student.html', context)

# Search students view: finds students matching a query (admin only)
@admin_required  # Only staff users can access this page
def search_students(request):
    # Get the search text from the URL query string 'q' (empty string if absent)
    query = request.GET.get('q', '')
    # Start with an empty queryset (no results)
    results = Student.objects.none()

    # Only search if the user actually typed something
    if query:
        # Filter students whose first name, last name, email, or parent name contains the query
        results = Student.objects.filter(
            Q(first_name__icontains=query) |   # first name contains query (case-insensitive)
            Q(last_name__icontains=query) |    # OR last name contains query
            Q(email__icontains=query) |        # OR email contains query
            Q(parent_name__icontains=query)    # OR parent name contains query
        )

    # Build the context with the query text, results, and a result count
    context = {
        'query': query,          # the search text, to show it back in the box
        'results': results,      # the matching student records
        'count': results.count(),  # how many matches were found
    }
    # Render the search results template
    return render(request, 'search_results.html', context)

# Students by grade view: shows all students in a specific grade (admin only)
@admin_required  # Only staff users can access this page
def students_by_grade(request, grade):
    # Fetch all students whose grade equals the grade in the URL
    students = Student.objects.filter(grade=grade)
    # Build the context with the students, the grade, and the total count
    context = {
        'students': students,          # the student records for this grade
        'grade': grade,                # the grade number from the URL
        'total': students.count(),     # how many students are in this grade
    }
    # Render the students-by-grade template
    return render(request, 'students_by_grade.html', context)