#encoding=utf-8
import math
import os
import time
import operator
import datetime
import base64
import json
from io import BytesIO
from PIL import Image, ImageOps

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
from django.contrib.messages import info, success
from django.conf import settings 


from redpoint.models import Oldman
from redpoint.models import Bed
from redpoint.models import Room
from redpoint.models import Messages
from redpoint.forms import CheckInForm, MessagesForm

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
    do_crop = False
    if form.is_valid():
        room_id = form.cleaned_data['room']
        room_q = get_object_or_404(Room, id=room_id)
        if room_q.beds_count == 4:
            do_crop = True
        image_file = save_to_local(avatar, crop=do_crop)
        bed = form.cleaned_data['bed']
        
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


def save_to_local(data, crop=True):
    _, b64data = data.split(',')
    image = base64.b64decode(b64data)
    now = time.time()
    image_file = '/media/avatars/'+str(now)+".jpg"
    dst_img_name = '/media/avatars/'+str(now)+"__160X250.jpg"
    dst_img = BASE_DIR + dst_img_name
    with open(dst_img, 'wb+') as photo:
        photo.write(image)
        os.chmod(dst_img, 0o666)
        if crop:
            _crop(ori_img=dst_img, dst_img=dst_img, dst_w=160, dst_h=300)
        ##in python3 666 is not allowed, it should begin with '0o', said by PEP 3127 
    return dst_img_name


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
    context['message'] = show_message()
    page = render(request, template, context)
    return HttpResponse(page)


def messages_page(request):
    template = "redpoint/messages.html"
    form = MessagesForm()
    page = render(request, template, {"form": form,})
    return HttpResponse(page)


def add_message(request):
    ms_form = MessagesForm(request.POST)
    if ms_form.is_valid():
        data = ms_form.cleaned_data
        Messages.objects.create(**data)
        success(request, u"操作成功！")
        return HttpResponseRedirect(reverse("messages"))
    else:
        info(request, u"发生错误，请检查后重新提交")
        return HttpResponseRedirect(reverse("messages"))

def show_message():
    worktime = 1200
    ms_object = Messages.objects.last()
    now = timezone.now()
    end_time = ms_object.create + datetime.timedelta(seconds=worktime)
    msg = ms_object.payload
    if now > end_time:
        msg = ''
    return msg 


def _crop(**args):
    args_key = {'ori_img':'','dst_img':'','dst_w':'','dst_h':'','save_q':75}
    arg = {}
    for key in args_key:
        if key in args:
            arg[key] = args[key]
        
    im = Image.open(arg['ori_img'])
    # ori_w,ori_h = im.size
    imagefit = ImageOps.fit(im, (arg['dst_w'], arg['dst_h']), Image.ANTIALIAS, centering=(0.5,0))
    imagefit.save(arg['dst_img'], 'JPEG', quality=75)
    # return dst_img


def clipResizeImg(**args):
    
    args_key = {'ori_img':'','dst_img':'','dst_w':'','dst_h':'','save_q':75}
    arg = {}
    for key in args_key:
        if key in args:
            arg[key] = args[key]
        
    im = Image.open(arg['ori_img'])
    ori_w,ori_h = im.size
 
    dst_scale = float(arg['dst_h']) / arg['dst_w'] #目标高宽比
    ori_scale = float(ori_h) / ori_w #原高宽比
 
    if ori_scale >= dst_scale:
        #过高
        width = ori_w
        height = int(width*dst_scale)
 
        x = 0
        y = (ori_h - height) / 3
        
    else:
        #过宽
        height = ori_h
        width = int(height*dst_scale)
 
        x = (ori_w - width) / 2
        y = 0
 
    #裁剪
    box = (x,y,width+x,height+y)
    #这里的参数可以这么认为：从某图的(x,y)坐标开始截，截到(width+x,height+y)坐标
    #所包围的图像，crop方法与php中的Imagecopy方法大为不一样
    newIm = im.crop(box)
    im = None
 
    #压缩
    ratio = float(arg['dst_w']) / width
    newWidth = int(width * ratio)
    newHeight = int(height * ratio)
    newIm.resize((newWidth,newHeight),Image.ANTIALIAS).save(arg['dst_img'],quality=arg['save_q'])


