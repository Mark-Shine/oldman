#encoding=utf-8
import math
import os
import time
import operator
import datetime
import base64
import json
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
BED_CLASS = {"2": "beds2", "4": "beds4", "6": "beds6"}
IMG_CLASS = {"2": "room-heart", "4":"room-rounded", "6": "room-rounded","8":"room-photo"}

def home(request):
    template = 'redpoint/home.html'
    context = {}
    beds = Bed.objects.all()
    whos = [bed.who for bed in beds if bed.who]
    beds_avilable = [bed for bed in beds if not bed.is_occupyied()]
    beds_avilable_counts = len(beds_avilable) 
    context['beds_avilable_counts'] = beds_avilable_counts
    context['beds_occupyied_counts'] = int(beds.count() - beds_avilable_counts)
    context["whos"] = whos
    context['home_active'] = 'active'
    page = render(request, template, context)
    return HttpResponse(page)


def checkin_page(request):
    template = "redpoint/checkin.html"
    bed = request.GET.get("bed")
    room = request.GET.get("room")
    if not (room and bed):
        return rooms_page(request)
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
        room_id = form.cleaned_data['room']
        room_q = get_object_or_404(Room, id=room_id)
        bed_q = get_object_or_404(Bed, number=bed, room=room_q)
        new_man = Oldman.objects.create(name=form.cleaned_data['name'], avatar=image_file)
        bed_q.who = new_man
        bed_q.save()
        return HttpResponseRedirect(reverse("room")+'?id=%s' % room_id)
    else:
        form = CheckInForm()
    return render(request, 'redpoint/checkin.html', {'form': form})


def do_checkout(request):
    bed = request.GET.get('bedid')
    bed_q = Bed.objects.filter(pk=bed)
    if bed_q:
        bed_q[0].who = None
        bed_q[0].save()
    return HttpResponseRedirect("/rooms/")


def save_to_local(data):
    image = base64.b64decode(data[22:])
    image_file = '/media/avatars/'+str(time.time())+".jpg"
    name = BASE_DIR+image_file
    # with os.fdopen(os.open(name, os.O_RDWR, 777), 'wb+') as handle:
    #     handle.write(image)
    with open(name, 'wb+') as photo:
        photo.write(image)
        os.chmod(name, 0o666)
        ##in python3 666 is not allowed, it should begin with '0o', said by PEP 3127 
    return image_file


def rooms_page(request):
    """房间管理页面"""
    template = "redpoint/rooms.html"
    beds = Bed.objects.all()
    context = {}
    context['objects'] = beds
    context['occupyied_beds'] = Bed.objects.occupyied()
    beds_avilable = [bed for bed in beds if not bed.is_occupyied()]
    beds_avilable_counts = len(beds_avilable) 
    context['beds_avilable_counts'] = beds_avilable_counts
    context['beds_all_counts'] = beds.count()
    context['rooms'] = Room.objects.all()
    context['room_active'] = 'active'
    page = render(request, template, context)
    return HttpResponse(page)


def room(request):
    template = "redpoint/room.html"
    room_id = request.GET.get("id")
    room_q = get_object_or_404(Room, id=room_id)
    context = {}
    beds = room_q.bed_set.all()
    beds_dict = {o.number:o for o in beds}
    od = OrderedDict(sorted(beds_dict.items(), key=lambda t: t[0]))
    context['obj'] = od
    context['room'] = room_q
    page  = render(request, template, context)
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
    floor = request.GET.get("f")
    template = "client/room_heart.html"
    room_q = get_object_or_404(Room, room_number=room_number, floor=floor)
    beds = room_q.bed_set.all()
    beds_dict = {o.number:o for o in beds}
    od = OrderedDict(sorted(beds_dict.items(), key=lambda t: t[0]))
    ##有可能取到不合适的数字
    context = {}
    context['beds_class'] = BED_CLASS.get(str(room_q.beds_count))
    context['img_class'] = IMG_CLASS.get("8")
    context['objects'] = od
    context['ajax_url'] = reverse('ajax_photo') + '?number=%s&f=%s' %(room_number, floor)
    page = render(request, template, context)
    return HttpResponse(page)


def ajax_get_photo(request):
    room_number = request.GET.get("number")
    floor = request.GET.get("f")
    template = "client/piece_photo.html"
    room_q = get_object_or_404(Room, room_number=room_number, floor=floor)
    beds = room_q.bed_set.all()
    beds_dict = {o.number:o for o in beds}
    od = OrderedDict(sorted(beds_dict.items(), key=lambda t: t[0]))
    ##有可能取到不合适的数字
    context = {}
    context['objects'] = od
    context['beds_class'] = BED_CLASS.get(str(room_q.beds_count))
    context['img_class'] = IMG_CLASS.get("8")
    page = render(request, template, context)
    return HttpResponse(page)

