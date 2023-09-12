from datetime import timedelta

import django.forms as forms

from website.models.core_models import *


class OHSCreateForm(forms.ModelForm):
    class Meta:
        model = OfficeHourSession
        exclude = ['ohs_status', 'ohs_instructor']

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.instructor = Instructor.objects.get(instructor_user=user)

    def save(self, commit=True):
        self.instance.ohs_instructor = self.instructor
        return super().save(commit)

    def clean(self):
        self.cleaned_data['ohs_instructor'] = self.instructor
        cleaned_data = super().clean()
        self.__clean_times__(cleaned_data)
        self.__clean_registration__(cleaned_data)
        return cleaned_data

    def __clean_registration__(self, cleaned_data):
        class_obj = cleaned_data.get('ohs_class')
        if class_obj and self.instructor not in class_obj.get_instructors():
            self.add_error('ohs_instructor', 'You are not enrolled in this class as an instructor.')

    def __clean_times__(self, cleaned_data):
        start_time = cleaned_data.get('ohs_start_time')
        end_time = cleaned_data.get('ohs_end_time')
        if start_time and end_time:
            if end_time < start_time:
                self.add_error('ohs_end_time', 'The end time cannot be before the start time.')
            if start_time < timezone.now() - timedelta(minutes=15):
                self.add_error('ohs_start_time',
                               'The start time must occur at least 15 minutes before the current time.')
        else:
            if not start_time:
                self.add_error('ohs_start_time', 'The start time must be supplied.')
            if not end_time:
                self.add_error('ohs_end_time', 'The end time must be supplied.')
