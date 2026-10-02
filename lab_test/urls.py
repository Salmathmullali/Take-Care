from django.urls import path
from . import views

app_name = 'lab_test'

urlpatterns = [
    path('know-your-disease/', views.symptom_input, name='symptom_input'),
    path('analyze-symptoms/', views.analyze_symptoms, name='analyze_symptoms'),
    path('results/', views.results, name='results'),
    path('doctors/<int:disease_id>/', views.doctor_list, name='doctor_list'),
    path('appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('appointment-success/<int:appointment_id>/', views.appointment_success, name='appointment_success'),
]
