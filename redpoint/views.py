#encoding=utf-8
import math
import time
import operator
import datetime
import base64
from io import BytesIO

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template.context import (Context, RequestContext)
from django.template.loader import Template
from django.core.paginator import Paginator
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings 

from redpoint.models import Oldman
from redpoint.forms import CheckInForm

BASE_DIR = settings.BASE_DIR

def home(request):
    template = 'redpoint/home.html'
    whos = Oldman.objects.all()
    page = render(request, template, {"whos": whos})
    return HttpResponse(page)


def checkin_page(request):
    template = "redpoint/checkin.html"
    form = CheckInForm()
    page = render(request, template, {"form": form})
    return HttpResponse(page)

import time
def do_checkin(request):
    avatar = request.POST.get("avatar", "")
    form = CheckInForm(request.POST)
    if form.is_valid():
        image_file = save_to_local(avatar)
        Oldman.objects.create(name=form.cleaned_data['name'], avatar="/media/"+image_file)
        return HttpResponseRedirect('/checkin')
    else:
        form = CheckInForm()
    return render(request, 'redpoint/checkin.html', {'form': form})


def save_to_local(data):
    image = base64.b64decode(data[22:])
    image_file = '/avatars/'+str(time.time())+".jpg"
    with open(BASE_DIR+image_file, "wb+") as photo:
        photo.write(image)
    return image_file


