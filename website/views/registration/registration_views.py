from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from website.forms import SignupForm
from website.models import *


def associate_accounts(user, post_data):
    if post_data['is_instructor'] is True:
        instructor = Instructor.objects.create(instructor_user=user, instructor_type=post_data['instructor_type'])
        if instructor.instructor_type == InstructorType.TEACHING_ASSISTANT:
            TeachingAssistant.objects.create(ta_instructor=instructor)
        elif instructor.instructor_type == InstructorType.PROFESSOR:
            Professor.objects.create(prof_instructor=instructor)
    if post_data['is_student'] is True:
        Student.objects.create(student_user=user)


def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST':
        post_data = _get_dict_from_post_(request.POST)
        post_data['is_instructor'] = post_data['instructor_type'] != 'None'
        post_data['is_student'] = 'is_student' in post_data
        form = SignupForm(post_data, initial=post_data)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            associate_accounts(request.user, post_data)
            return HttpResponseRedirect(redirect_to='/')
    return render(request=request,
                  template_name='registration/signup.html',
                  context={'form': form})


def _get_dict_from_post_(post):
    post_data = dict(post)
    for key in post_data:
        post_data[key] = post_data[key][0]
    return post_data
