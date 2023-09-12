import re
import datetime

from django.http import *
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from website.authentication_decorators import professor_or_superuser_required
from website.models import *


@professor_or_superuser_required()
def course_create(request):
    if request.method == 'POST':
        post = request.POST
        course = __create_course__(post)
        __create_course_topics__(course, post['course_topics'])
        return HttpResponseRedirect(
            reverse('website:professor-class-create', kwargs={'course_id': course.id})
        )
    else:
        return render(request, 'website/instructor/professor/course-create.html')


def __create_course__(post) -> Course:
    """ Creates or finds a `Course` based on the kwargs in post
    :param post: contains the kwargs of the `Course` object to be queried/made
    :returns: a Course
    """
    return Course.objects.get_or_create(
        course_subject=post['course_subject'],
        course_catalog_number=post['course_catalog_number']
    )[0]


def __create_course_topics__(course: Course, raw_course_topics: str) -> list[CourseTopic]:
    """ Returns a list of found or created `CourseTopics`
    :param course: the `Course` to link the topics to
    :param raw_course_topics: a string of comma-separated `CourseTopic` names
    :returns: a list of `CourseTopics`
    """
    course_topic_names = __get_course_topic_names__(raw_course_topics)
    course_topics = []
    for name in course_topic_names:
        course_topics += [CourseTopic.objects.get_or_create(course_topic_name=name, course_topic_course=course)[0]]
    return course_topics


def __get_course_topic_names__(raw_course_topics: str) -> [str]:
    """ Returns a list of `CourseTopic` names based on a comma separated string
    :param raw_course_topics: a comma separated string of `CourseTopic` names
    :returns: a list of `CourseTopic` names
    """
    return [i for item in re.sub(r'\s', ' ', raw_course_topics).split(',') if (i := item.strip())]


@professor_or_superuser_required()
def class_create(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course_topics = CourseTopic.objects.filter(course_topic_course=course)
    if request.method == 'POST':
        post = request.POST
        semester = __create_semester__(post['semester'])
        course_class = __create_class__(course, semester)
        __create_prof_registration__(request.user, course_class)
        __create_assignments__(course_class, post)
        return HttpResponseRedirect(reverse('website:home'))
    else:
        return render(
            request, 'website/instructor/professor/class-create.html',
            {'course_id': course_id, 'course_topics': course_topics}
        )


def __create_prof_registration__(user: UniversityMember, course_class: Class) -> Registration:
    """ Finds or creates a professor `Registration` entry for the UniversityMember
    :param user: the `UniversityMember` to associate the registration entry with
    :returns: a Registration object"""
    return Registration.objects.get_or_create(
        reg_user=user, reg_class=course_class, reg_type=RegistrationType.PROFESSOR
    )[0]


def __create_semester__(date_string: str) -> Semester:
    """ Finds or creates a `Semester` object based of the date_string supplied.
     :param date_string: a string containing a date in the format: '%Y-%m'
     :returns: a `Semester` object
     """
    date = datetime.datetime.strptime(date_string, '%Y-%m').date()
    semester_month = date.month
    if 1 <= semester_month <= 4:
        semester_name = SemesterChoices.SPRING
    elif 5 <= semester_month <= 8:
        semester_name = SemesterChoices.SUMMER
    else:
        semester_name = SemesterChoices.FALL
    return Semester.objects.get_or_create(semester_year=date.year, semester_name=semester_name)[0]


def __create_class__(course: Course, semester: Semester) -> Class:
    """ Finds or creates a `Class` based upon the `Course` and `Semester` supplied
    :param course: the `Course` to link the `Class` to
    :param semester: the `Semester` to link the `Class` to
    :returns: a `Class`
    """
    return Class.objects.get_or_create(class_course=course, class_semester=semester)[0]


def __create_assignments__(course_class: Class, post: [QueryDict, dict]) -> list[Assignment]:
    """ Finds or creates a list of assignments tied to a `Class`.
    The assignments will be populated with `AssignmentTopics` contained in the post object.
    :param course_class: the `Class` to link the `Assignments` to
    :param post: the post object filled with the number of assignments,
                 the assignment names, and the `AssignmentTopics` ids to be linked.
    :return: a list of `Assignments`
    """
    assignments = []
    for assignment_index in range(1, int(post['assignments'])+1):
        assignment_name = post[f'assignment{assignment_index}']
        assignment, _ = Assignment.objects.get_or_create(
            assignment_class=course_class,
            assignment_name=assignment_name
        )
        assignment_topic_ids = post.getlist(f'assignment{assignment_index}_topics')
        __link_assignment_topics__(assignment, assignment_topic_ids)
        assignments.append(assignment)
    return assignments


def __link_assignment_topics__(assignment: Assignment, assignment_topic_ids: list[str]) -> None:
    """ Helper method to associate a list of `AssignmentTopic` ids with a specific `Assignment`
    :param assignment: the `Assignment` object to link the topics with
    :param assignment_topic_ids: a list of `AssignmentTopic` ids represented as strings
    :return: None
    """
    for topic_id in assignment_topic_ids:
        topic = get_object_or_404(CourseTopic, id=int(topic_id))
        assignment.assignment_topics.add(topic)
