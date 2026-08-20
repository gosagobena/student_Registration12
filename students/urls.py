# Import the path function, which defines a URL pattern (route) in Django
from django.urls import path

# Import the views module so the URL patterns can reference the view functions
from . import views

# app_name gives this URL configuration a namespace ('students')
# This lets templates refer to URLs like 'students:home' instead of just 'home'
app_name = 'students'

# urlpatterns: the list of all URL routes for this app
urlpatterns = [
    # --- Home ---
    # Route the root URL '' to the register view (register-only landing page)
    path('', views.register_student),
    # Route '/home/' to the home view, named 'home'
    # Visiting /home/ renders the statistics/dashboard page
    path('home/', views.home, name='home'),

    # --- Authentication ---
    # Route '/login/' to the login view, named 'login'
    path('login/', views.login_view, name='login'),
    # Route '/logout/' to the logout view, named 'logout'
    path('logout/', views.logout_view, name='logout'),

    # --- Student management ---
    # Route '/students/' to the register view (public registration form)
    path('students/', views.register_student, name='register_student'),
    # Route '/students/list/' to the student_list view (admin-only student list)
    path('students/list/', views.student_list, name='student_list'),
    # Route '/register/' to the register view too (alternative URL for the form)
    path('register/', views.register_student),
    # Route '/students/<id>/' to student_detail; <int:student_id> captures a numeric ID
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    # Route '/students/<id>/edit/' to edit_student; edit page for one student
    path('students/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    # Route '/students/<id>/delete/' to delete_student; delete page for one student
    path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),

    # --- Search and filter ---
    # Route '/search/' to the search view; 'q' comes from the URL query string
    path('search/', views.search_students, name='search_students'),
    # Route '/grade/<grade>/' to students_by_grade; <int:grade> captures the grade number
    path('grade/<int:grade>/', views.students_by_grade, name='students_by_grade'),
]