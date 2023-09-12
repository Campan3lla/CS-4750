import django.forms as forms
from django.core.exceptions import ValidationError

from website.models.account_models import UniversityMember


class UserSignupForm(forms.ModelForm):
    class Meta:
        model = UniversityMember
        fields = '__all__'


class SignupForm(forms.ModelForm):
    password_confirmation = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = UniversityMember
        fields = ['password',
                  'first_name',
                  'last_name',
                  'username',
                  'is_student',
                  'is_instructor']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')
        if password != password_confirmation:
            self.add_error('password_confirmation', ValidationError('The passwords must match'))

        def is_checked(data, field):
            return bool(data.get(field))
        is_student = is_checked(cleaned_data, 'is_student')
        is_instructor = is_checked(cleaned_data, 'is_instructor')
        if (is_student or is_instructor) is False:
            self.add_error(None, ValidationError('You must select at least one account type.'))
