from django.contrib.auth.decorators import user_passes_test
from website.models import Instructor, Student, TeachingAssistant, Professor, UniversityMember


# https://simpleisbetterthancomplex.com/tutorial/2018/01/18/how-to-implement-multiple-user-types-with-django.html
def student_or_superuser_required(function=None, redirect_field_name='redirect_from', redirect_url='website:home'):
    """
    Decorator for views that checks that the logged-in user is a student,
    redirects to the home page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: (u.is_active and u.is_student) or u.is_superuser,
        login_url=redirect_url,
        redirect_field_name=redirect_field_name
    )
    return actual_decorator(function) if function else actual_decorator


def instructor_or_superuser_required(function=None, redirect_field_name='redirect_from', redirect_url='website:home'):
    """
    Decorator for views that checks that the logged-in user is a student,
    redirects to the home page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: (u.is_active and u.is_instructor) or u.is_superuser,
        login_url=redirect_url,
        redirect_field_name=redirect_field_name
    )
    return actual_decorator(function) if function else actual_decorator


def professor_or_superuser_required(function=None, redirect_field_name='redirect_from', redirect_url='website:home'):
    """
    Decorator for views that checks that the logged-in user is a student,
    redirects to the home page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: (u.is_active and u.is_instructor and u.user_instructor.instructor_type == 'PROF') or u.is_superuser,
        login_url=redirect_url,
        redirect_field_name=redirect_field_name
    )
    return actual_decorator(function) if function else actual_decorator


def superuser_required(function=None, redirect_field_name='redirect_from', redirect_url='website:home'):
    """
    Decorator for views that checks that the logged-in user is a student,
    redirects to the home page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=redirect_url,
        redirect_field_name=redirect_field_name
    )
    return actual_decorator(function) if function else actual_decorator
