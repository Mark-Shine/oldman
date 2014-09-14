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
from redpoint.models import Bed
from redpoint.models import Room
from redpoint.forms import CheckInForm

BASE_DIR = settings.BASE_DIR

def home(request):
    template = 'redpoint/home.html'
    whos = Oldman.objects.all()
    page = render(request, template, {"whos": whos})
    return HttpResponse(page)


def checkin_page(request):
    template = "redpoint/checkin.html"
    bed = request.GET.get("bed")
    room = request.GET.get("room")
    form = CheckInForm()
    form.fields['bed'].initial = bed
    form.fields['room'].initial = room
    page = render(request, template, {"form": form})
    return HttpResponse(page)

import time
def do_checkin(request):
    avatar = request.POST.get("avatar", "")
    form = CheckInForm(request.POST)
    if form.is_valid():
        image_file = save_to_local(avatar)
        bed = form.cleaned_data['bed']
        room = form.cleaned_data['room']
        room_q = Room.objects.get(room_number=room)
        bed_q = Bed.objects.get(number=bed, room=room_q)
        new_man = Oldman.objects.create(name=form.cleaned_data['name'], avatar="/media/"+image_file)
        bed_q.who = new_man
        bed_q.save()
        return HttpResponseRedirect('/rooms/')
    else:
        form = CheckInForm()
    return render(request, 'redpoint/checkin.html', {'form': form})


def save_to_local(data):
    image = base64.b64decode(data[22:])
    image_file = '/avatars/'+str(time.time())+".jpg"
    with open(BASE_DIR+image_file, "wb+") as photo:
        photo.write(image)
    return image_file


def rooms_page(request):
    """房间管理页面"""
    template = "redpoint/rooms.html"
    beds = Bed.objects.all()
    context = {}
    context['objects'] = beds
    page = render(request, template, context)
    return HttpResponse(page)


def home_client_page(request):
    template = "redpoint/home_client.html"
    room = Room.objects.all()
    context = {}
    context['objects'] = room
    page = render(request, template, context)
    return HttpResponse(page)

from django.utils.datastructures import OrderedDict

def room_client_page(request):
    room_number = request.GET.get("number")
    template = "redpoint/room_client.html"
    beds = Room.objects.get(room_number=room_number).bed_set.all()
    beds_dict = {o.number:o for o in beds}
    od = OrderedDict(sorted(beds_dict.items(), key=lambda t: t[0]))
    page = render(request, template, {"objects": od})
    return HttpResponse(page)
