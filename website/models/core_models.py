from django.db import models
from django.utils import timezone

from website.models.account_models import Instructor, Student, _get_univ_mem_, UniversityMember


class AutoValidateMixin:
    def save(self, **kwargs):
        def has_and_callable(obj, name):
            return hasattr(obj, name) and callable(getattr(obj, name))

        if has_and_callable(super(), 'full_clean') and has_and_callable(super(), 'save'):
            full_clean = getattr(super(), 'full_clean')
            save = getattr(super(), 'save')
            full_clean()
            save(**kwargs)
        else:
            raise AttributeError('Error! The object does not have a save() or full_clean() method'
                                 'Please ensure that the mixin is the first item in the inheritance hierarchy.')


class Course(AutoValidateMixin, models.Model):
    course_subject = models.CharField(max_length=8)
    course_catalog_number = models.CharField(max_length=4)

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=['course_subject', 'course_catalog_number'],
                name='unique_course'
            )
        ]

    def __str__(self):
        return f'{self.course_subject} {self.course_catalog_number}'


class CourseTopic(AutoValidateMixin, models.Model):
    course_topic_course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_topic_name = models.CharField(max_length=64)

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=['course_topic_course', 'course_topic_name'],
                name='unique_course_topic'
            )
        ]

    def __str__(self):
        return f'{self.course_topic_name}'


class SemesterChoices(models.TextChoices):
    SPRING = 'SPRING', 'Spring'
    SUMMER = 'SUMMER', 'Summer'
    FALL = 'FALL', 'Fall'


class Semester(AutoValidateMixin, models.Model):
    semester_name = models.CharField(max_length=8, choices=SemesterChoices.choices)
    semester_year = models.IntegerField()

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=['semester_name', 'semester_year'],
                name='unique_semester'
            )
        ]

    def __str__(self):
        return f'{self.semester_name} {self.semester_year}'


class Class(AutoValidateMixin, models.Model):
    class_course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.class_course.course_subject} {self.class_course.course_catalog_number} {self.class_semester}'

    def get_students(self):
        registrations = Registration.objects.filter(
            reg_class=self,
            reg_type=RegistrationType.STUDENT
        )
        return [Student.objects.get(student_user=reg.reg_user) for reg in registrations]

    def get_instructors(self):
        registrations = Registration.objects.filter(
            reg_class=self,
            reg_type__in=[RegistrationType.TEACHING_ASSISTANT, RegistrationType.PROFESSOR]
        )
        return [Instructor.objects.get(instructor_user=reg.reg_user) for reg in registrations]

    def get_active_ohs(self):
        return OfficeHourSession.objects.filter(
            ohs_class=self,
            ohs_status__in=[OHSStatus.OPEN, OHSStatus.AWAY],
            ohs_start_time__lte=timezone.now(),
            ohs_end_time__gt=timezone.now(),
        )

    def get_ohs_from_user_or_none(self, user):
        instructor = Instructor.objects.filter(instructor_user=user).first()
        if instructor:
            return OfficeHourSession.objects.filter(ohs_class=self, ohs_instructor=instructor)
        else:
            return None


class Assignment(AutoValidateMixin, models.Model):
    assignment_name = models.CharField(max_length=64)
    assignment_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    assignment_topics = models.ManyToManyField(CourseTopic)

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=['assignment_name', 'assignment_class'],
                name='unique_assignment'
            )
        ]

    def __str__(self):
        return f'{self.assignment_name}'


class RegistrationType(models.TextChoices):
    STUDENT = 'STUD', 'Student'
    TEACHING_ASSISTANT = 'TA', 'Teaching Assistant'
    PROFESSOR = 'PROF', 'Professor'


class Registration(AutoValidateMixin, models.Model):
    reg_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    reg_user = models.ForeignKey(UniversityMember, on_delete=models.CASCADE)
    reg_type = models.CharField(max_length=4, choices=RegistrationType.choices)

    # class Meta:  # May or may not be added
    #     constraints = [
    #         models.constraints.UniqueConstraint(
    #             fields=['reg_class', 'reg_user'],
    #             name='unique_registration'
    #         )
    #     ]
    @staticmethod
    def user_is_enrolled_as(reg_user, reg_class, reg_types: [RegistrationType]):
        return Registration.objects.filter(
            reg_user=_get_univ_mem_(reg_user),
            reg_class=reg_class,
            reg_type__in=reg_types
        ).exists()

    @staticmethod
    def get_classes_where_enrolled_as(reg_user, reg_types: [RegistrationType]):
        registration = Registration.objects.filter(
            reg_user=_get_univ_mem_(reg_user),
            reg_type__in=reg_types
        )
        return [reg.reg_class for reg in registration]

    @staticmethod
    def get_instructor_classes(reg_user):
        return Registration.get_classes_where_enrolled_as(
            reg_user=reg_user,
            reg_types=[RegistrationType.TEACHING_ASSISTANT, RegistrationType.PROFESSOR]
        )

    @staticmethod
    def get_student_classes(reg_user):
        return Registration.get_classes_where_enrolled_as(
            reg_user=reg_user,
            reg_types=[RegistrationType.STUDENT]
        )

    def __str__(self):
        return f'{self.reg_user} in {self.reg_class} as {self.reg_type}'


class Location(AutoValidateMixin, models.Model):
    location_name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return f'{self.location_name}'


class OHSStatus(models.TextChoices):
    OPEN = 'OPEN', 'open'
    AWAY = 'AWAY', 'away'
    CLOSED = 'CLOSED', 'closed'


class OfficeHourSession(AutoValidateMixin, models.Model):
    ohs_instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    ohs_start_time = models.DateTimeField()
    ohs_end_time = models.DateTimeField()
    ohs_status = models.CharField(choices=OHSStatus.choices, default=OHSStatus.OPEN, max_length=6)
    ohs_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    ohs_location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.ohs_instructor}: {self.ohs_start_time} {self.ohs_end_time} ({self.ohs_location})'

    def duration(self):
        return self.ohs_end_time - self.ohs_start_time

    @staticmethod
    def get_ohs_from_user_or_none(user: UniversityMember):
        instructor = Instructor.objects.filter(instructor_user=user).first()
        if instructor:
            return OfficeHourSession.objects.filter(ohs_instructor=instructor)
        else:
            return None

    def __get_ohq_type__(self, *ohq_status):
        return OfficeHourQuestion.objects.filter(ohq_ohs=self, ohq_status__in=ohq_status)

    def get_unanswered_ohqs(self):
        return self.__get_ohq_type__(OHQStatus.UNANSWERED)

    def get_answered_ohqs(self):
        return self.__get_ohq_type__(OHQStatus.ANSWERED)

    def get_pending_ohqs(self):
        return self.__get_ohq_type__(OHQStatus.PENDING)

    def get_closed_ohqs(self):
        return self.__get_ohq_type__(OHQStatus.ANSWERED, OHQStatus.UNANSWERED)



class OHQStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'  # When a question is first made
    UNANSWERED = 'UNANSWERED', 'Unanswered'  # When a question is closed without being answered
    ANSWERED = 'ANSWERED', 'Answered'  # When a question is closed and is answered


class OfficeHourQuestion(AutoValidateMixin, models.Model):
    ohq_ohs = models.ForeignKey(OfficeHourSession, on_delete=models.CASCADE)
    ohq_assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True, blank=True)
    ohq_student = models.ForeignKey(Student, on_delete=models.CASCADE)
    ohq_topics = models.ManyToManyField(CourseTopic)
    ohq_student_comment = models.CharField(max_length=256, blank=True)
    ohq_instructor_comment = models.CharField(max_length=256, blank=True)
    ohq_status = models.CharField(choices=OHQStatus.choices, max_length=16, default=OHQStatus.PENDING)
    ohq_opened_at = models.DateTimeField()  # When the question was submitted to be answered
    ohq_closed_at = models.DateTimeField(null=True,
                                         blank=True)  # When the question status was set to something other than Pending
