from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('predict/', views.predict, name='predict'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # API endpoints for dynamic dropdowns
    path('api/education_data/', views.education_data_api, name='education_data_api'),
    path('api/cities/', views.cities_api, name='cities_api'),
    path('api/universities/', views.universities_api, name='universities_api'),
    path('api/university_data/', views.university_data_api, name='university_data_api'),
    path('api/programs/', views.programs_api, name='programs_api'),
    path('api/program_details/', views.program_details_api, name='program_details_api'),
] 