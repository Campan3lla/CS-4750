# https://simpleisbetterthancomplex.com/tutorial/2018/01/18/how-to-implement-multiple-user-types-with-django.html
from django.contrib.auth.models import AbstractUser
from django.db import models


class UniversityMember(AbstractUser):
    is_student = models.BooleanField(default=True)
    is_instructor = models.BooleanField(default=False)

    def save(self, **kwargs):
        self.full_clean()
        return super().save(**kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Student(models.Model):
    student_user = models.OneToOneField(
        UniversityMember,
        related_name='user_student',
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def save(self, **kwargs):
        self.full_clean()
        return super().save(**kwargs)

    def __str__(self):
        return f'{self.student_user.first_name} {self.student_user.last_name}'


class InstructorType(models.TextChoices):
    TEACHING_ASSISTANT = 'TA', 'Teaching Assistant'
    PROFESSOR = 'PROF', 'Professor'


class Instructor(models.Model):
    instructor_user = models.OneToOneField(
        UniversityMember,
        related_name='user_instructor',
        on_delete=models.CASCADE,
        primary_key=True,
    )
    instructor_type = models.CharField(choices=InstructorType.choices, max_length=4)

    def save(self, **kwargs):
        self.full_clean()
        return super().save(**kwargs)

    def __str__(self):
        return f'{self.instructor_user.first_name} {self.instructor_user.last_name}'


class TeachingAssistant(models.Model):
    ta_instructor = models.OneToOneField(
        Instructor,
        related_name='instructor_ta',
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def save(self, **kwargs):
        self.full_clean()
        return super().save(**kwargs)


class Professor(models.Model):
    prof_instructor = models.OneToOneField(
        Instructor,
        related_name='instructor_professor',
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def save(self, **kwargs):
        self.full_clean()
        return super().save(**kwargs)


def _get_univ_mem_(user):
    if type(user) == Student:
        user = user.student_user
    elif type(user) == Instructor:
        user = user.instructor_user
    elif type(user) == Professor:
        user = user.prof_instructor.instructor_user
    elif type(user) == TeachingAssistant:
        user = user.ta_instructor.instructor_user
    else:
        user = user
    return user


def get_or_none(model, **kwargs):
    try:
        instance = model.objects.get(**kwargs)
    except model.DoesNotExist:
        instance = None
    return instance


def get_instructor_or_none(user):
    return get_or_none(Instructor, instructor_user=_get_univ_mem_(user))


def get_student_or_none(user):
    return get_or_none(Student, student_user=_get_univ_mem_(user))
