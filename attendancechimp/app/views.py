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
import random
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from .models import InstructorProfile, StudentProfile, Course, Lecture, QR_Code_Upload

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

def _next_id(model, field):
    return (model.objects.aggregate(m=Max(field))["m"] or 0) + 1


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
        StudentProfile.objects.create(
            StudentID=_next_id(StudentProfile, "StudentID"), user=user, email=email)
    else:
        InstructorProfile.objects.create(
            InstructorID=_next_id(InstructorProfile, "InstructorID"), user=user, email=email)
    login(request, user)
    return HttpResponse("User created")
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
def _next_id(model, field):
    return (model.objects.aggregate(m=Max(field))["m"] or 0) + 1

def _is_instructor(user):
    return user.is_authenticated and InstructorProfile.objects.filter(user=user).exists()

def _is_student(user):
    return user.is_authenticated and StudentProfile.objects.filter(user=user).exists()


@login_required
@require_GET
def new_course(request):
    return render(request, 'app/new_course.html')


@login_required
@require_GET
def new_lecture(request):
    return render(request, 'app/new_lecture.html', {"courses": Course.objects.all()})


@login_required
@require_GET
def new_qr_upload(request):
    return render(request, 'app/new_qr_upload.html')


@csrf_exempt
@require_POST
def createCourse(request):
    if not _is_instructor(request.user):
        return HttpResponse("Unauthorized", status=401)

    name = request.POST.get("course-name")
    start = request.POST.get("start-time")
    end = request.POST.get("end-time")
    day_labels = {"mon": "Mon", "tue": "Tue", "wed": "Wed", "thu": "Thu", "fri": "Fri"}
    days = [label for key, label in day_labels.items() if f"day-{key}" in request.POST]

    if not (name and start and end and days):
        return HttpResponseBadRequest("Missing field")

    Course.objects.create(
        CourseID=_next_id(Course, "CourseID"),
        coursename=name,
        Instructor=InstructorProfile.objects.get(user=request.user),
        meetingschedule=f"{','.join(days)} {start}-{end}",
    )
    return HttpResponse("Course created")


@csrf_exempt
@require_POST
def createLecture(request):
    if not _is_instructor(request.user):
        return HttpResponse("Unauthorized", status=401)

    course = Course.objects.filter(coursename=request.POST.get("choice")).first()
    if course is None:
        return HttpResponseBadRequest("Unknown course")

    Lecture.objects.create(
        lectureID=_next_id(Lecture, "lectureID"),
        course=course,
        date=datetime.now(CDT).date(),
        QRID=random.randint(100000, 999999),
    )
    return HttpResponse("Lecture created")


@csrf_exempt
@require_POST
def createQRCodeUpload(request):
    if not _is_student(request.user):
        return HttpResponse("Unauthorized", status=401)

    image = request.FILES.get("imageUpload")
    if image is None:
        return HttpResponseBadRequest("Missing file")

    QR_Code_Upload.objects.create(
        UploadID=_next_id(QR_Code_Upload, "UploadID"),
        student=StudentProfile.objects.get(user=request.user),
        image=image,
    )
    return HttpResponse("Upload created")


@require_GET
def dumpUploads(request):
    if not _is_instructor(request.user):
        return HttpResponse("Unauthorized", status=401)

    data = [
        {"username": u.student.user.username,
         "upload_time": u.time.astimezone(CDT).strftime("%Y-%m-%d %H:%M:%S")}
        for u in QR_Code_Upload.objects.all()
    ]
    return JsonResponse(data, safe=False)


   
        
       
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



