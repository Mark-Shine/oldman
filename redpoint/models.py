#encoding=utf-8
from django.db import models

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

# Create your models here.
class Room(models.Model):
    floor = models.IntegerField(null=True, blank=True,)
    room_number = models.IntegerField(null=True, blank=True,)

    def __str__(self, ):
      return u"%s" % self.room_number


class Bed(models.Model):
    room = models.ForeignKey("Room", null=True, blank=True) 
    who = models.ForeignKey("Oldman", null=True, blank=True)
    number = models.IntegerField(null=True, blank=True,)

    def __str__(self, ):
        return u"%s-%s" % (self.room, self.number)


class Oldman(models.Model):
    name = models.CharField(max_length=16, null=True, blank=True, verbose_name=u"姓名")
    time = models.DateTimeField(blank=True, null=True)
    
    avatar = models.ImageField(upload_to='avatars', verbose_name=u"照片")
    avatar_thumbnail = ImageSpecField(source='avatar',
                                      processors=[ResizeToFill(100, 50)],
                                      format='JPEG',
                                      options={'quality': 60}, )

    def __str__(self, ):
        return u"%s" % self.name