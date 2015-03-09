from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from forms import NewZWaveControllerForm
from models import ZWaveController
from datetime import datetime
from hotqueue import HotQueue
import redis
import json


detectStatus = redis.Redis("localhost")


def zwave_controller_new(request):
  print "zwave_controller_new start"

  if request.method == 'POST':
    form = NewZWaveControllerForm(request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      zwave = ZWaveController(name=cd['name'], location=cd['location'], ipaddress=cd['ipaddress'])
      zwave.save()

      return HttpResponseRedirect('/zwave/' + str(zwave.id))
  else:
    form = NewZWaveControllerForm()

  return render(request, 'zwavecontroller_new.html', {'form': form})


def zwave_controller_delete(request, zwave_id):
  print "zwave_controller_delete start"
  try:
    id = int(zwave_id)
  except ValueError:
    raise Http404()

  zwave = ZWaveController.objects.get(id=id)
  zwave.delete()

  return HttpResponseRedirect('/zwave_control/')


