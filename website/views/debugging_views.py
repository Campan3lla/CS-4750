import json

from django.db import transaction, Error
from django.http import HttpResponse
from datetime import datetime
from website.models import *


def populate_table_view(request):
    with open('data.json') as file:
        json_data = json.loads(file.read())
    try:
        with transaction.atomic():
            admin = __create_admin__()
            __create_university_members__(json_data['members'])
            __create_courses__(json_data['courses'])
            __register_admin_in_classes__(admin)
        return HttpResponse(str(json_data))
    except Error as e:
        return HttpResponse(e)


def __register_admin_in_classes__(admin: UniversityMember):
    for class_obj in Class.objects.all():
        Registration.objects.create(reg_class=class_obj, reg_user=admin, reg_type=RegistrationType.PROFESSOR)
        Registration.objects.create(reg_class=class_obj, reg_user=admin, reg_type=RegistrationType.STUDENT)


def __create_admin__() -> UniversityMember:
    admin = UniversityMember.objects.create_superuser(
        username='admin', is_student=True, is_instructor=True,
        first_name='Addy', last_name='Adder'
    )
    admin.set_password('123')
    admin.save()
    Student.objects.create(student_user=admin)
    admin_instructor = Instructor.objects.create(instructor_user=admin, instructor_type=InstructorType.PROFESSOR)
    Professor.objects.create(prof_instructor=admin_instructor)
    return admin


def __create_courses__(all_crs_data: json):
    for crs_data in all_crs_data:
        course, _ = Course.objects.get_or_create(**crs_data['course'])
        __create_course_topics__(course, crs_data)
        __create_classes__(course, crs_data)


def __create_classes__(course: Course, crs_data: json):
    for class_data in crs_data['classes']:
        semester, _ = Semester.objects.get_or_create(**class_data['semester'])
        class_obj = Class.objects.create(class_course=course, class_semester=semester)
        __create_registration__(class_data, class_obj)
        __create_assignments__(class_data, class_obj, course)
        __create_office_hours__(class_data, class_obj)


def __create_office_hours__(class_data, class_obj):
    for ohs_data in class_data['office_hours']:
        __create_ohs__(class_obj, ohs_data)


def __create_ohs__(class_obj, ohs_data):
    ohs, _ = OfficeHourSession.objects.get_or_create(
        ohs_class=class_obj,
        ohs_start_time=datetime.fromisoformat(ohs_data['ohs_start_time']),
        ohs_end_time=datetime.fromisoformat(ohs_data['ohs_end_time']),
        ohs_instructor=__get_instructor_by_compid__(ohs_data['ohs_instructor_computing_id']),
        ohs_status=ohs_data['ohs_status'],
        ohs_location=Location.objects.get_or_create(location_name=ohs_data['location_name'])[0]
    )
    for question_data in ohs_data['questions']:
        __create_ohqs__(class_obj, ohs, question_data)


def __create_ohqs__(class_obj, ohs, question_data):
    ohq, _ = OfficeHourQuestion.objects.get_or_create(
        ohq_ohs=ohs,
        ohq_student=__get_student_by_compid__(question_data['ohq_student_computing_id']),
        ohq_assignment=__get_assignment_or_none__(class_obj, question_data['ohq_assignment']),
        ohq_student_comment=question_data['ohq_student_comment'],
        ohq_instructor_comment=question_data['ohq_instructor_comment'],
        ohq_opened_at=datetime.fromisoformat(question_data['ohq_opened_at']),
        ohq_closed_at=datetime.fromisoformat(question_data['ohq_closed_at']),
        ohq_status=question_data['ohs_status']
    )
    for topic_name in question_data['ohq_topics']:
        ohq.ohq_topics.add(__get_course_topic_by_name__(class_obj.class_course, topic_name))


def __get_assignment_or_none__(class_obj, assignment_name: str):
    if assignment_name:
        return Assignment.objects.get(assignment_class=class_obj, assignment_name=assignment_name)
    else:
        return None


def __create_registration__(class_data: json, class_obj: Class):
    for reg_data in class_data['registration']:
        registration, _ = Registration.objects.get_or_create(
            reg_class=class_obj,
            reg_user=UniversityMember.objects.get(username=reg_data['computing_id']),
            reg_type=reg_data['reg_type']
        )


def __create_assignments__(class_data: json, class_obj: Class, course: Course):
    for assignment_data in class_data['assignments']:
        assignment, _ = Assignment.objects.get_or_create(
            assignment_name=assignment_data['assignment_name'],
            assignment_class=class_obj
        )
        __associate_assignment_topics__(assignment, assignment_data, course)


def __associate_assignment_topics__(assignment: Assignment, assignment_data: json, course: Course):
    for assignment_topic in assignment_data['assignment_topics']:
        assignment.assignment_topics.add(
            CourseTopic.objects.get(
                course_topic_course=course,
                course_topic_name=assignment_topic)
        )


def __create_course_topics__(course: Course, crs_data: json):
    for crs_topic_data in crs_data['course_topics']:
        course_topic, _ = CourseTopic.objects.get_or_create(
            course_topic_course=course,
            course_topic_name=crs_topic_data
        )


def __create_university_members__(um_data: json):
    for um in um_data:
        instructor_type = um['instructor_type']
        del um['instructor_type']
        univ_mem = UniversityMember.objects.create_user(**um)
        univ_mem.set_password(um['password'])
        univ_mem.save()
        if um['is_instructor']:
            __create_instructor__(instructor_type, univ_mem)
        if um['is_student']:
            __create_student__(univ_mem)


def __create_student__(univ_mem: UniversityMember):
    Student.objects.get_or_create(student_user=univ_mem)


def __create_instructor__(instructor_type: InstructorType, univ_mem: UniversityMember):
    instructor, _ = Instructor.objects.get_or_create(
        instructor_user=univ_mem,
        instructor_type=instructor_type
    )
    if instructor.instructor_type == InstructorType.TEACHING_ASSISTANT:
        TeachingAssistant.objects.get_or_create(ta_instructor=instructor)
    elif instructor.instructor_type == InstructorType.PROFESSOR:
        Professor.objects.get_or_create(prof_instructor=instructor)


def __get_instructor_by_compid__(computing_id: str):
    return Instructor.objects.get(instructor_user__username=computing_id)


def __get_univmem_by_compid__(computing_id: str):
    return UniversityMember.objects.get(username=computing_id)


def __get_student_by_compid__(computing_id: str):
    return Student.objects.get(student_user__username=computing_id)


def __get_course_topic_by_name__(course: Course, name: str):
    return CourseTopic.objects.get(course_topic_course=course, course_topic_name=name)
