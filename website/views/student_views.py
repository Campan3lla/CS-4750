import functools

from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.db.models import Case, When
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.defaults import permission_denied

from website.authentication_decorators import student_or_superuser_required
from website.models import *


def __get_user_student_or_none__(user, check_class: Class):
    reg = check_class.registration_set.filter(
        reg_user=user,
        reg_type=RegistrationType.STUDENT
    ).last()
    return reg.reg_user.user_student if reg else None


@student_or_superuser_required()
def student_ohs_list(request):
    registration = Registration.objects.filter(reg_user=request.user, reg_type=RegistrationType.STUDENT)
    classes = [reg.reg_class for reg in registration]
    return render(request, 'website/student/ohs-list.html', {'classes': classes})


@student_or_superuser_required()
def student_ohq_list(request):
    if request.method == 'POST':
        post = request.POST
        ohq_id = post.get('ohq_id')
        ohq = get_object_or_404(OfficeHourQuestion, id=ohq_id)
        if ohq.ohq_status == OHQStatus.PENDING:
            ohq.delete()
    ohqs = OfficeHourQuestion.objects.filter(
        ohq_student=Student.objects.get(student_user=request.user)
    ).order_by(
        Case(
            When(ohq_status=OHQStatus.PENDING, then=0),
            When(ohq_status=OHQStatus.ANSWERED, then=1),
            When(ohq_status=OHQStatus.UNANSWERED, then=2),
            default=3,
        ),
        '-ohq_opened_at'
    )
    return render(request, 'website/student/ohq-list.html', {'ohqs': ohqs})


def ohq_class_enrollment_required(view):
    """Prevents a user from creating a question for an OfficeHourSession unless they are enrolled in the class
    to which the OHQ belongs to.
    :param view: the view to be wrapped (needs to have ohs_id as a view parameter)
    :return: the view or an HTTP 403 Forbidden page
    """
    @functools.wraps(view)
    def test_request(request, ohs_id):
        ohs = get_object_or_404(OfficeHourSession, id=ohs_id)
        if Registration.objects.filter(
                reg_class=ohs.ohs_class,
                reg_user=request.user,
                reg_type=RegistrationType.STUDENT
        ).exists():
            print(f'user passes test for class {ohs.ohs_class}')
            return view(request, ohs_id)
        else:
            print(f'user failed test for class {ohs.ohs_class}')
            return permission_denied(request, 'You do not have permission to access this office hour session.')

    return test_request


@student_or_superuser_required()
@ohq_class_enrollment_required
def student_ohq_create(request, ohs_id):
    ohs = get_object_or_404(OfficeHourSession, id=ohs_id)
    errors = {}
    if request.method == 'POST':
        post = request.POST
        try:
            with transaction.atomic():
                ohq = OfficeHourQuestion.objects.create(
                    ohq_ohs=ohs,
                    ohq_assignment=Assignment.objects.filter(
                        id=assignment if (assignment := post['ohq_assignment']) else None
                    ).first(),
                    ohq_student=__get_user_student_or_none__(request.user, ohs.ohs_class),
                    ohq_student_comment=post['ohq_student_comment'],
                    ohq_instructor_comment='',
                    ohq_status=OHQStatus.PENDING,
                    ohq_opened_at=timezone.now(),
                    ohq_closed_at=None,
                )
                ohq.ohq_topics.add(*post.getlist('ohq_topics'))
                if not (ohq.ohq_topics.all() or ohq.ohq_assignment):
                    raise ValidationError({'ohq_assignment': 'You must input an assignment or select course topics.'})
                return HttpResponseRedirect(reverse('website:student-ohq-list'))
        except ValidationError as e:
            errors = errors | e.message_dict
        except IntegrityError as e:
            errors = errors | {'integrity_error': e.args}
    return render(request, 'website/student/ohq-create.html', {'ohs': ohs, 'errors': errors})
