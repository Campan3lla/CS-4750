import functools

from django.db.models import Case, When, QuerySet
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.defaults import permission_denied

from website.authentication_decorators import instructor_or_superuser_required
from website.forms.instructor_forms import *
from website.models import OfficeHourSession
from website.models.account_models import get_instructor_or_none


def ohs_creator_required(view):
    """Prevents a user from accessing an OfficeHourSession unless they are the instructor
    to which the OHQ belongs to.
    :param view: the view to be wrapped (needs to have ohs_id as a view parameter)
    :return: the view or an HTTP 403 Forbidden page
    """
    @functools.wraps(view)
    def test_request(request, ohs_id):
        ohs = get_object_or_404(OfficeHourSession, id=ohs_id)
        instructor = get_instructor_or_none(request.user)
        if ohs.ohs_instructor == instructor:
            return view(request, ohs_id)
        else:
            return permission_denied(request, 'You do not have permission to access this office hour session.')

    return test_request


def ohq_instructor_required(view):
    """Prevents a user from accessing an OfficeHourQuestion unless they are the instructor
    to which the OHQ belongs to.
    :param view: the view to be wrapped (needs to have ohq_id as a view parameter)
    :return: the view or an HTTP 403 Forbidden page
    """
    @functools.wraps(view)
    def test_request(request, ohq_id):
        ohq = get_object_or_404(OfficeHourQuestion, id=ohq_id)
        instructor = get_instructor_or_none(request.user)
        if ohq.ohq_ohs.ohs_instructor == instructor:
            return view(request, ohq_id)
        else:
            return permission_denied(request, 'You do not have permission to access this question')

    return test_request


@instructor_or_superuser_required()
def ohs_create(request):
    form = OHSCreateForm(request.POST or None, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('website:instructor-ohs-detail', kwargs={'ohs_id': form.instance.id}))
    return render(
        request, 'website/instructor/office-hour/ohs-create.html',
        {'classes': Registration.get_instructor_classes(request.user),
         'locations': Location.objects.all(),
         'errors': form.errors}
    )


@instructor_or_superuser_required()
def ohs_location_create(request):
    if request.method == 'POST':
        if location_name := request.POST['location_name']:
            location = Location.objects.create(location_name=location_name)
            return HttpResponse(f'<option value="{location.id}">{location.location_name}</option>')


@instructor_or_superuser_required()
def ohs_list(request):
    classes = Registration.get_instructor_classes(request.user)
    office_hours = {class_obj: class_obj.get_ohs_from_user_or_none(request.user) for class_obj in classes}
    return render(
        request, 'website/instructor/office-hour/ohs-list.html',
        {
            'classes': classes,
            'class_office_hours_dict': office_hours,
        }
    )


@instructor_or_superuser_required()
@ohs_creator_required
def ohs_detail(request, ohs_id):
    ohs = get_object_or_404(OfficeHourSession, id=ohs_id)
    ohqs = get_sorted_ohqs(ohs)
    return render(
        request, 'website/instructor/office-hour/ohs-detail.html',
        {'ohs': ohs, 'ohqs': ohqs}
    )


@instructor_or_superuser_required()
@ohq_instructor_required
def ohs_detail_edit_ohq(request, ohq_id):
    ohq = get_object_or_404(OfficeHourQuestion, id=ohq_id)
    if request.method == 'POST':
        post = request.POST
        ohq.ohq_status = post.get('ohq_status', OHQStatus.PENDING)
        ohq.ohq_instructor_comment = post.get('ohq_instructor_comment')
        ohq.save()
    return render(request, 'website/instructor/office-hour/ohs-ohq-component.html', {'ohq': ohq})


def get_sorted_ohqs(ohs: OfficeHourSession) -> QuerySet:
    """This function sorts office hour questions based in two stages.
    First, it sorts based upon the question status (Pending first, answered second, unanswered, last).
    Second, it sorts by the question time (oldest first).
    :param ohs: the office hour session from which the ohqs will be taken from
    :return: a QuerySet containing the filtered results (if any)
    """
    return OfficeHourQuestion.objects.filter(
        ohq_ohs=ohs
    ).order_by(
        Case(
            When(ohq_status=OHQStatus.PENDING, then=0),
            When(ohq_status=OHQStatus.ANSWERED, then=1),
            When(ohq_status=OHQStatus.UNANSWERED, then=2),
            default=3,
        ),
        'ohq_opened_at'
    )
