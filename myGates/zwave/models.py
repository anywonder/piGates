from django.db import models


class ZWaveController(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    ipaddress = models.IPAddressField()

    def __unicode__(self):
      return self.name

class ZWaveAlarm(models.Model):
    controllerName = models.CharField(max_length=100)
    nodeId = models.IntegerField()
    eventTime = models.DateTimeField()
    eventType = models.CharField(max_length=100)
    data = models.CharField(max_length=100)

    def __unicode__(self):
      return self.name
