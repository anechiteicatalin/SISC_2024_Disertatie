from django.db import models
from datetime import datetime, timedelta, timezone, tzinfo
import time
tz = timezone(timedelta(hours=2))

class PIR(models.Model):
    name = models.CharField(max_length=50, default='Senzor miscare')
    mac = models.CharField(max_length=20)
    value = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=datetime.now(tz))
#    user = models.CharField(max_length=60, default='')
    uid = models.CharField(max_length=16, default=0)
    
class USA(models.Model):
    name = models.CharField(max_length=50, default='Senzor usa/geam')
    mac = models.CharField(max_length=20)
    value = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=datetime.now(tz))
#    user = models.CharField(max_length=60, default='')
    uid = models.CharField(max_length=16, default=0)
    
class DHT(models.Model):
    name = models.CharField(max_length=50, default='Temperatura si umiditate')
    mac = models.CharField(max_length=20)
    humidity = models.FloatField(default=0.0)
    temperature = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(default=datetime.now(tz))
#    user = models.CharField(max_length=60, default='')
    uid = models.CharField(max_length=16, default=0)
    
class CAMERA(models.Model):
    name = models.CharField(max_length=50, default='Camera')
    mac = models.CharField(max_length=20)
#    user = models.CharField(max_length=60, default='')
    uid = models.CharField(max_length=16, default=0)
    socket = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=datetime.now(tz))

class UID(models.Model):
    mac = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    uid = models.CharField(max_length=16, default=0)

class Connections(models.Model):
    uid = models.CharField(max_length=16, default=0)
    user = models.CharField(max_length=60, default='')

class Requests(models.Model):
    uid = models.CharField(max_length=16, default=0)
    user = models.CharField(max_length=60, default='')
    from_user = models.CharField(max_length=60, default='')
    timestamp = models.DateTimeField(default=datetime.now(tz))
    
class ResetPassword(models.Model):
    email = models.CharField(max_length=60, default='')
    key = models.CharField(max_length=65, default='')\
    
def get_image_path(instance, filename):
    return 'image_history/{0}/{1}_{2}'.format(instance.uid, str(time.time()), filename)
  
class ImageHistory(models.Model):
    uid = models.CharField(max_length=16, default=0)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.now(tz))
