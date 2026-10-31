"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime

from django.views.decorators.http import require_GET, require_POST
from .models import InstructorProfile, StudentProfile

import zoneinfo
import json
import io
def time_view(request):
    central = zoneinfo.ZoneInfo("America/Chicago")
    current = datetime.now(central)
    return HttpResponse(current.strftime("%H:%M"), content_type = "text/plain")
def sum_view(request):
    n1 = float(request.GET.get("n1", 0))
    n2 = float(request.GET.get("n2", 0))
    return HttpResponse(f"<p>{n1 + n2}</p>")    
# from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
#                      Lecture, QRCodeUpload, is_instructor, is_student,
#                      getUploadsForCourse)

CDT = zoneinfo.ZoneInfo("America/Chicago")


# ---------------------------------------------------------------------------
# HW2  — index, time, sum
# ---------------------------------------------------------------------------

def index(request):
    """Render the home page (index.html)."""
    current_time = datetime.now(CDT)
    context = {
    "current_time": current_time.strftime("%H:%M"),
    "user": request.user,
}
    return render(request, 'app/index.html', context)



# ---------------------------------------------------------------------------
# HW4  — user creation

@require_GET
def new(request):
    return render(request, 'app/new.html')
@csrf_exempt
@require_POST
def createUser(request):
    email = request.POST.get("email")
    user_name = request.POST.get("user_name")
    password = request.POST.get("password")
    is_student = request.POST.get("is_student")
    if not (email and user_name and password and is_student is not None):
        return HttpResponseBadRequest("Missing Field")
    if User.objects.filter(email=email).exists():
        return HttpResponseBadRequest("Email already registered")
    user = User.objects.create_user(username=user_name, email=email, password=password)
    if is_student == "1":
        StudentProfile.objects.create(user=user)
    else:
        InstructorProfile.objects.create(user=user)
    login(request, user)
    return HttpResponse("User created")
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



