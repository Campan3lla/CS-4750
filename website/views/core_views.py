from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from website.authentication_decorators import superuser_required
from website.forms import RegistrationForm


def home(request):
    return render(request, template_name='website/home.html')


@superuser_required()
def register_view(request):
    form = RegistrationForm(request.POST or None)
    form.initial = {'reg_user': request.user}
    if request.method == 'POST' and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('website:home'))
    else:
        return render(request, 'website/register.html', {'form': form})
