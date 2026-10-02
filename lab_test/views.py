from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Disease, Doctor, Appointment
import time

def symptom_input(request):
    return render(request, 'lab_test/symptom_input.html')

def analyze_symptoms(request):
    if request.method == 'POST':
        # Simulate background processing
        time.sleep(2) # Fake processing time
        symptoms = request.POST.get('symptoms', '')
        
        # In a real app we would use AI/logic to map symptoms to disease.
        # Here we mock by just picking the first disease or creating a generic one if DB is empty
        disease = Disease.objects.first()
        if not disease:
            # We should probably have a fallback or seed data, but for this demo:
            disease_id = 0
        else:
            disease_id = disease.id
            
        request.session['analyzed_disease_id'] = disease_id
        return JsonResponse({'status': 'success', 'redirect_url': '/lab-test/results/'})
    return JsonResponse({'status': 'error'}, status=400)

def results(request):
    disease_id = request.session.get('analyzed_disease_id')
    disease = Disease.objects.filter(id=disease_id).first()
    
    # Context data for the template
    context = {
        'disease': disease,
        'confidence': '85%', # Mocked
    }
    return render(request, 'lab_test/results.html', context)

def doctor_list(request, disease_id):
    disease = get_object_or_404(Disease, id=disease_id)
    doctors = disease.specialist_doctors.all()
    if not doctors.exists():
        # Fallback to all doctors for demo purposes if no specialist is found
        doctors = Doctor.objects.all()
    
    context = {
        'disease': disease,
        'doctors': doctors,
    }
    return render(request, 'lab_test/doctor_list.html', context)

def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    hospitals = [h.strip() for h in doctor.available_hospitals.split(',') if h.strip()]
    
    if request.method == 'POST':
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        patient_name = request.POST.get('patient_name')
        contact = request.POST.get('contact')
        hospital_selected = request.POST.get('hospital_selected')
        
        appointment = Appointment.objects.create(
            doctor=doctor,
            hospital_selected=hospital_selected,
            date=date,
            time_slot=time_slot,
            patient_name=patient_name,
            contact=contact
        )
        return redirect('lab_test:appointment_success', appointment_id=appointment.id)
        
    context = {
        'doctor': doctor,
        'hospitals': hospitals,
    }
    return render(request, 'lab_test/book_appointment.html', context)

def appointment_success(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'lab_test/appointment_success.html', {'appointment': appointment})
