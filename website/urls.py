"""
URL configuration for OfficeHourManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
import website.views as website_views

app_name = 'website'
urlpatterns = [
    path('', website_views.home, name='home'),

    # STUDENTS:
    path('student/office-hours/list/', website_views.student_ohs_list,
         name='student-ohs-list'),
    path('student/office-hours/<int:ohs_id>/question/create/', website_views.student_ohq_create,
         name='student-ohq-create'),
    path('student/office-hours/questions/list/', website_views.student_ohq_list,
         name='student-ohq-list'),

    # INSTRUCTORS:
    path('instructor/office-hours/location/create/', website_views.ohs_location_create,
         name='instructor-location-create'),
    path('instructor/office-hours/create/', website_views.ohs_create,
         name='instructor-ohs-create'),
    path('instructor/office-hours/list/', website_views.ohs_list,
         name='instructor-ohs-list'),
    path('instructor/office-hours/<int:ohs_id>/detail/', website_views.ohs_detail,
         name='instructor-ohs-detail'),
    path('instructor/office-hours/question/<int:ohq_id>/edit', website_views.ohs_detail_edit_ohq,
         name='instructor-ohs-detail-edit-ohq'),

    # PROFESSORS:
    path('professor/course/create/', website_views.course_create,
         name='professor-course-create'),
    path('professor/course/<int:course_id>/class/create/', website_views.class_create,
         name='professor-class-create'),

    # MISC:
    path('superuser/register/', website_views.register_view, name='register'),

    path('account/', include('django.contrib.auth.urls')),
    path('account/signup/', website_views.signup, name='signup'),

    path('test/populate/', website_views.populate_table_view, name='test-populate-tables'),

    # INFORMATION SUMMARIES
    path('information/home/', website_views.inf_home,
         name='inf-home'),
    path('information/<int:class_id>/questions-answered/', website_views.inf_questions_answered,
         name='inf-questions-answered'),
    path('information/<int:class_id>/questions-asked/', website_views.inf_questions_asked,
         name='inf-questions-asked'),
    path('information/<int:class_id>/questions-per-assignment/', website_views.inf_questions_per_assignment,
         name='inf-questions-per-assignment'),
    path('information/<int:class_id>/ohs-hours/', website_views.inf_ohs_hours,
         name='inf-ohs-hours'),
    path('information/<int:class_id>/registration-summary/', website_views.inf_registration_summary,
         name='inf-registration-summary'),
    path('information/<int:class_id>/questions-per-month/', website_views.inf_questions_per_month,
         name='inf-questions-per-month'),
]
