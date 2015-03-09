from django.db import models


class Camera(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    ipaddress = models.IPAddressField()
    triggerlevel = models.IntegerField()
    detectionlevel = models.IntegerField()
    triggerlimit = models.IntegerField()
    sensitivity = models.IntegerField()

    def __unicode__(self):
      return self.name
