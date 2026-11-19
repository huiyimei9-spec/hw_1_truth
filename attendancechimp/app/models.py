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
from django.utils import timezone

import logging
import string
import random

from zoneinfo import ZoneInfo
from datetime import datetime

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

    course = models.CharField(max_length = 50, unique = True, null = True, blank =True)
    start_time = models.TimeField(null = True, blank = True)
    end_time = models.TimeField(null = True, blank = True)
    day_mon = models.BooleanField(default = False)
    day_tue = models.BooleanField(default = False)
    day_wed = models.BooleanField(default = False)
    day_thu = models.BooleanField(default = False)
    day_fri = models.BooleanField(default = False)
    def meets_on_day(self, weekday):
        """weekday: 0 = Monday ... 4 = Friday (same as datetime.weekday())."""
        days = [self.day_mon, self.day_tue, self.day_wed, self.day_thu, self.day_fri]
        return weekday < 5 and days[weekday]


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
class QRCodeUpload(models.Model):
    UploadID = models.IntegerField(primary_key = True)
    student = models.ForeignKey(StudentProfile, on_delete = models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete = models.SET_NULL, null = True, blank = True)
    time = models.DateTimeField(default = timezone.now)
    image = models.ImageField(upload_to = "uploads/")
def getUploadsForCourse(course):
    """Return a list of QRCodeUpload objects that are valid for the course number."""
    course_obj = Course.objects.filter(course=course).first()
    if course_obj is None:
        return[]

    chicago = ZoneInfo("America/Chicago")
    valid = []
    uploads = QRCodeUpload.objects.filter(lecture__course=course_obj)
    for u in uploads:
        t = u.time
        if timezone.is_naive(t):
            t = t.replace(tzinfo=ZoneInfo("UTC"))
        t = t.astimezone(chicago)
        if not course_obj.meets_on_day(t.weekday()):
            continue
        
        tod = t.time()
        if tod <  course_obj.start_time or tod > course_obj.end_time:
            continue
        valid.append(u)
    return valid

# ---------------------------------------------------------------------------
# Helper / API functions
# ---------------------------------------------------------------------------



