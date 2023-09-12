import datetime
import functools

from django.shortcuts import render, get_object_or_404
from django.views.defaults import permission_denied

from website.authentication_decorators import instructor_or_superuser_required
from website.models import *


def enrollment_required(view):
    """Prevents a user from accessing a Class's information unless they are the enrolled within it.
    :param view: the view to be wrapped (needs to have class_id as a view parameter)
    :return: the view or an HTTP 403 Forbidden page
    """
    @functools.wraps(view)
    def test_request(request, class_id):
        class_obj = get_object_or_404(Class, id=class_id)
        if Registration.objects.filter(reg_class=class_obj, reg_user=request.user).exists():
            return view(request, class_id)
        else:
            return permission_denied(request, 'You do not have permission to access this class.')

    return test_request


@instructor_or_superuser_required()
def inf_home(request):
    """This view provides a tab-bar interface to other information views using HTMX.
    When registering a new information view, append a new entry in the context object."""
    get_context_view = lambda name, url: {'display_name': name, 'url': url}
    classes = Registration.get_instructor_classes(request.user)
    context = {
        'information_views': [
            get_context_view('Questions Answered', 'website:inf-questions-answered'),
            get_context_view('Questions Asked', 'website:inf-questions-asked'),
            get_context_view('Questions per Assignment', 'website:inf-questions-per-assignment'),
            get_context_view('Hours Held', 'website:inf-ohs-hours'),
            get_context_view('Registration Summary', 'website:inf-registration-summary'),
            get_context_view('Questions per Month', 'website:inf-questions-per-month'),
        ],
        'classes': classes
    }
    return render(request, 'website/instructor/information/inf-home.html', context)


def __assemble_graph_context__(labels, data, chart_name, unique_identifier, graph_type='bar', y_max=None):
    return {
        'labels': labels,
        'data': data,
        'graph_type': graph_type,
        'chart_name': chart_name,
        'max': y_max if y_max else max(data) + 2,
        'canvas_id': f'{unique_identifier}_canvas_id',
        'data_id': f'{unique_identifier}_data_id',
        'label_id': f'{unique_identifier}_label_id'
    }


def __make_strings__(objects):
    return [str(obj) for obj in objects]


@instructor_or_superuser_required()
@enrollment_required
def inf_questions_answered(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    instructors = class_obj.get_instructors()
    questions_answered_list = [
        OfficeHourQuestion.objects.filter(
            ohq_ohs__ohs_instructor=instructor,
            ohq_ohs__ohs_class=class_obj,
            ohq_status=OHQStatus.ANSWERED
        ).count() for instructor in instructors]
    return render(
        request,
        'website/instructor/information/inf-generic-graph.html',
        __assemble_graph_context__(
            labels=__make_strings__(instructors),
            data=questions_answered_list,
            chart_name='Questions Answered',
            unique_identifier=f'questionsAnswered{class_obj.id}'
        )
    )


@instructor_or_superuser_required()
@enrollment_required
def inf_questions_asked(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    students = class_obj.get_students()
    questions_asked_list = [
        OfficeHourQuestion.objects.filter(
            ohq_student=student,
            ohq_ohs__ohs_class=class_obj
        ).count() for student in students]
    return render(
        request,
        'website/instructor/information/inf-generic-graph.html',
        __assemble_graph_context__(
            labels=__make_strings__(students),
            data=questions_asked_list,
            chart_name='Questions Asked',
            unique_identifier=f'questionsAsked{class_obj.id}'
        )
    )


@instructor_or_superuser_required()
@enrollment_required
def inf_questions_per_assignment(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    assignments = Assignment.objects.filter(
        assignment_class=class_obj
    )
    questions_asked_list = [
        OfficeHourQuestion.objects.filter(
            ohq_assignment=assignment
        ).count() for assignment in assignments]
    return render(
        request,
        'website/instructor/information/inf-generic-graph.html',
        __assemble_graph_context__(
            labels=__make_strings__(assignments),
            data=questions_asked_list,
            chart_name='Questions per Assignment',
            unique_identifier=f'questionsPerAssignment{class_obj.id}'
        )
    )


@instructor_or_superuser_required()
@enrollment_required
def inf_ohs_hours(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    instructors = class_obj.get_instructors()
    office_hours_held_list = []
    for instructor in instructors:
        total_time = sum(
            [ohs.duration() for ohs in OfficeHourSession.objects.filter(
                ohs_instructor=instructor,
                ohs_class=class_obj
            )],
            datetime.timedelta(0)
        )
        office_hours_held_list.append(total_time.total_seconds() / 3600)
    return render(
        request,
        'website/instructor/information/inf-generic-graph.html',
        __assemble_graph_context__(
            labels=__make_strings__(instructors),
            data=office_hours_held_list,
            chart_name='Office Hours Held',
            unique_identifier=f'ohsHours{class_obj.id}'
        )
    )


@instructor_or_superuser_required()
@enrollment_required
def inf_registration_summary(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    members = [0, 0, 0]  # Student, Teaching Assistant, Professor
    for registration in Registration.objects.filter(reg_class=class_obj):
        if registration.reg_type == RegistrationType.STUDENT:
            members[0] += 1
        elif registration.reg_type == RegistrationType.TEACHING_ASSISTANT:
            members[1] += 1
        elif registration.reg_type == RegistrationType.PROFESSOR:
            members[2] += 1
    return render(
        request,
        'website/instructor/information/inf-generic-graph.html',
        __assemble_graph_context__(
            labels=['Students', 'Teaching Assistants', 'Professors'],
            data=members,
            chart_name='Registration Summary',
            unique_identifier=f'registrationSummary{class_obj.id}'
        )
    )


@instructor_or_superuser_required()
@enrollment_required
def inf_questions_per_month(request, class_id):
    sem_months = []
    question_count = [0, 0, 0, 0]  # represents different months
    class_obj = get_object_or_404(Class, id=class_id)
    class_sem = class_obj.class_semester.semester_name
    if class_sem == SemesterChoices.SPRING:
        sem_months = ['January', 'February', 'March', 'April']
        for i in range(4):
            question_count[i] = OfficeHourQuestion.objects.filter(
                ohq_opened_at__month=i + 1
            ).count()
    elif class_sem == SemesterChoices.SUMMER:
        for i in range(4):
            sem_months = ['May', 'June', 'July', 'August']
            question_count[i] = OfficeHourQuestion.objects.filter(
                ohq_opened_at__month=i + 5
            ).count()
    else:
        for i in range(4):
            sem_months = ['September', 'October', 'November', 'December']
            question_count[i] = OfficeHourQuestion.objects.filter(
                ohq_opened_at__month=i + 9
            ).count()
    return render(
        request,
        'website/instructor/information/inf-generic-graph.html',
        __assemble_graph_context__(
            labels=sem_months,
            data=question_count,
            graph_type='line',
            chart_name='Questions per Month',
            unique_identifier=f'questionsPerMonth{class_obj.id}'
        )
    )
