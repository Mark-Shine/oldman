#encoding=utf-8
from django.db import models

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.db.models import Manager


class BedManager(Manager):

    def occupyied(self, ):
        return self.exclude(who=None)

    def avalible(self, ):
        return self.filter(who=None)

class Bed(models.Model):
    room = models.ForeignKey("Room", null=True, blank=True) 
    who = models.ForeignKey("Oldman", null=True, blank=True)
    number = models.IntegerField(null=True, blank=True,)
    objects = BedManager()
    def __str__(self, ):
        return u"%s-%s" % (self.room, self.number)

    class Meta:
        ordering = ('id', )

    def is_occupyied(self,):
        return self.who is not None


# Create your models here.
class Room(models.Model):
    floor = models.IntegerField(null=True, blank=True,)
    room_number = models.IntegerField(null=True, blank=True,)
    beds_count = models.IntegerField(null=True, blank=True,)

    def __str__(self, ):
      return u"%s-%s" % (self.floor, self.room_number)

    def add_beds(self, ):
        Beds = [Bed(number=num, room=self) for num in range(1, self.beds_count+1)]
        Bed.objects.bulk_create(Beds)

    def save(self, *args, **kwargs):
        super(Room, self).save(*args, **kwargs)
        self.add_beds()


class Client(models.Model):
    img_class = models.IntegerField(null=True, blank=True,)
    bed_class = models.IntegerField(null=True, blank=True,)


class Oldman(models.Model):
    name = models.CharField(max_length=16, null=True, blank=True, verbose_name=u"姓名")
    time = models.DateTimeField(blank=True, null=True)
    
    avatar = models.ImageField(upload_to='avatars', verbose_name=u"照片")
    avatar_thumbnail = ImageSpecField(source='avatar',
                                      processors=[ResizeToFill(200, 200)],
                                      format='JPEG',
                                      options={'quality': 60}, )

    def __str__(self, ):
        return u"%s" % self.name
