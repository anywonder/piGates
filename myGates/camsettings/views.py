from django.shortcuts import render_to_response, redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from forms import CameraSettingsForm, NewCameraForm
from models import Camera
from datetime import datetime
from hotqueue import HotQueue
import redis
import json

detectStatus = redis.Redis("localhost")


def camera_new(request):
  print "camera_new start"

  if request.method == 'POST':
    form = NewCameraForm(request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      camera = Camera(name=cd['name'], location=cd['location'], ipaddress=cd['ipaddress'], triggerlevel=7, detectionlevel=2, triggerlimit=2000, sensitivity=75)
      camera.save()

      return HttpResponseRedirect('/camera/' + str(camera.id))
  else:
    form = NewCameraForm()

  return render(request, 'camera_new.html', {'form': form})


def camera_delete(request, cam_id):
  print "camera_delete start"
  try:
    id = int(cam_id)
  except ValueError:
    raise Http404()

  camera = Camera.objects.get(id=id)
  camera.delete()

  return HttpResponseRedirect('/camera_control/')



def camera_settings(request, cam_id):
  print "camera_settings start"
  try:
    id = int(cam_id)
  except ValueError:
    raise Http404()

  camera = Camera.objects.get(id=id)

  if request.method == 'POST':
    form = CameraSettingsForm(request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      camera.triggerlimit = cd['triggerdetectionlimit']
      camera.detectionlevel = cd['detectionlevel']
      camera.triggerlevel = cd['triggerdetectionlevel']
      camera.sensitivity = cd['sensitivity']
      camera.save()

      return HttpResponseRedirect('/camera_control/settings/thanks/' + cam_id)
  else:
    form = CameraSettingsForm(
            initial={
            'triggerdetectionlimit': camera.triggerlimit,
            'detectionlevel': camera.detectionlevel,
            'triggerdetectionlevel': camera.triggerlevel,
            'sensitivity': camera.sensitivity}
            )
  return render(request, 'camera_settings.html', {'form': form})


def camera_settings_thanks(request, cam_id):
  try:
    id = int(cam_id)
  except ValueError:
    raise Http404()

  return render(request, 'camera_settings_thanks.html', {'CamId': id})

