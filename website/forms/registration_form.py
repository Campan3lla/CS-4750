import django.forms as forms

from website.models.core_models import *


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = '__all__'

