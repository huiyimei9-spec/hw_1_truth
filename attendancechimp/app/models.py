"""
models.py — Data model for AttendanceChimp.

AttendanceChimp is an electronic class attendance tool.  Instructors create
courses and lectures; each lecture is assigned a random QR code.  Students
photograph the QR code and upload the image.  The system decodes the QR code,
matches it to a lecture, and records the attendance.

Entities
--------
- CourseProfile   : extends Django User → instructor-specific data
- StudentProfile  : extends Django User → student-specific data
- Course          : a course taught by one instructor
- Enrollment      : junction table linking students to courses
- Lecture         : a single class meeting (has a QR-code identifier)
- QRCodeUpload    : a student's uploaded QR-code photograph
"""

from django.db import models
from django.contrib.auth.models import User

import logging
import string
import random

logger = logging.getLogger(__name__) # set up tracking, auditing, and debugging
                                                               # allows using logger.warning(), logger.error(), 
                                                               # logger.info(), etc. Better than print() for debuggin... 


# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------
class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    InstructorID = models.IntegerField(primary_key = True)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.CharField(max_length = 50)
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    StudentID = models.IntegerField(primary_key = True)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.CharField(max_length = 50)
	



# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------
class Course(models.Model):
    CourseID = models.IntegerField(primary_key = True)
    coursename = models.CharField(max_length = 50)
    Instructor = models.ForeignKey(InstructorProfile, on_delete = models.CASCADE)
    meetingschedule = models.CharField(max_length = 50)



# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------
class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete = models.CASCADE)
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    class Meta:
        unique_together = ("student", "course")



# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------
class Lecture(models.Model):
    lectureID = models.IntegerField(primary_key = True)
    course = models.ForeignKey(Course, on_delete = models.CASCADE)
    date = models.DateField()
    QRID = models.IntegerField()



# ---------------------------------------------------------------------------
# QR Code Upload
# ---------------------------------------------------------------------------
class QR_Code_Upload(models.Model):
    UploadID = models.IntegerField(primary_key = True)
    student = models.ForeignKey(StudentProfile, on_delete = models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete = models.SET_NULL, null = True, blank = True)
    time = models.DateTimeField(auto_now_add = True)



# ---------------------------------------------------------------------------
# Helper / API functions
# ---------------------------------------------------------------------------



