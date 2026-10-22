import uuid

from django.conf import settings
from django.db import models


class Instructor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructor_profile",
    )
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.get_username()


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    student_number = models.CharField(max_length=30, unique=True)

    def __str__(self):
        name = self.user.get_full_name() or self.user.get_username()
        return f"{name} ({self.student_number})"


class Course(models.Model):
    # Exactly one instructor per course. PROTECT prevents deleting an
    # instructor who still has courses assigned.
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.PROTECT,
        related_name="courses",
    )
    name = models.CharField(max_length=200)

    # Meeting schedule, e.g. meeting_days="MWF", 09:00 - 09:50
    meeting_days = models.CharField(
        max_length=20,
        help_text='Days the class meets, e.g. "MWF" or "TR".',
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    students = models.ManyToManyField(
        Student,
        through="Enrollment",
        related_name="courses",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Lecture(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lectures",
    )
    date = models.DateField()
    # Value encoded into the QR code displayed for this lecture.
    qr_identifier = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "date"], name="unique_lecture_per_course_date"
            ),
        ]

    def __str__(self):
        return f"{self.course} - {self.date}"


class Enrollment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "student"], name="unique_student_per_course"
            ),
        ]

    def __str__(self):
        return f"{self.student} in {self.course}"


class QRCodeUpload(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="qr_uploads",
    )
    # Optional: may be empty if the scanned QR code doesn't match a lecture
    # (or hasn't been matched yet). Keep the upload either way.
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qr_uploads",
    )
    image = models.ImageField(upload_to="qr_uploads/%Y/%m/%d/")
    decoded_value = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Upload by {self.student} at {self.uploaded_at:%Y-%m-%d %H:%M}"
