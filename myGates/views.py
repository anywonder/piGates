from django.core.context_processors import csrf
from django.shortcuts import render_to_response, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from hotqueue import HotQueue
from camsettings.forms import CameraSettingsForm
from camsettings.models import Camera
from zwave.models import ZWaveController, ZWaveAlarm
import redis
import os
import time
import urllib2
import json
import math
# import cameramodule

queue = HotQueue("myqueue", host="localhost", port=6379, db=0)
statusServer = redis.Redis("localhost")

needsRefresh = False

def loginview(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('login.html', c)

def auth_and_login(request, onsuccess='/', onfail='/login/'):
    user = authenticate(username=request.POST['email'], password=request.POST['password'])
    if user is not None:
        login(request, user)
        return redirect(onsuccess)
    else:
        return redirect(onfail)  

def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    user.save()
    return user

def user_exists(username):
    user_count = User.objects.filter(username=username).count()
    if user_count == 0:
        return False
    return True

def sign_up_in(request):
    post = request.POST
    if not user_exists(post['email']): 
        user = create_user(username=post['email'], email=post['email'], password=post['password'])
    	return auth_and_login(request)
    else:
    	return redirect("/login/")

@login_required(login_url='/login/')
def home_view(request):
    request.session.set_expiry(300)
    return render_to_response('home.html', RequestContext(request))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def loggedout(request):
    return render_to_response("loggedout.html")

@login_required(login_url='/login/')
def gates_control(request):
    request.session.set_expiry(300)
    currentStatus = statusServer.get("status")
    if currentStatus == 'open':
        status = "OPEN"
    else: 
        status = "CLOSED"
    return render_to_response('gates.html', RequestContext(request, {'gates_status': status}))

def open_gates(request):
    if(request.user.is_authenticated()):
      queue.put("open")
      return HttpResponseRedirect('/gates_control/')
    else:
      return HttpResponseRedirect('/login/')

def close_gates(request):
    if(request.user.is_authenticated()):
      queue.put("close")
      return HttpResponseRedirect('/gates_control')
    else:
      return HttpResponseRedirect('/login/')

@login_required(login_url='/login/')
def camera_control(request):
    request.session.set_expiry(300)
    cam_list = Camera.objects.all()
    return render(request, 'camera_list.html', {'cameras': cam_list})


@login_required(login_url='/login/')
def camera(request, cam_id):
    global needsRefresh

    try:
      id = int(cam_id)
    except ValueError:
      raise Http404()

    request.session.set_expiry(300)
    camera = Camera.objects.get(id=id)

    if ping_device(camera.ipaddress) == 0:
        cameraStatus = "Active"
        statusCamera = redis.Redis(camera.ipaddress)
        motionStatus = statusCamera.get("motionstatus")
    else:
        cameraStatus = "Not available"

    if motionStatus == 'monitoring':
      motion_text = "Monitoring"
    elif motionStatus == 'streaming':
      motion_text = "Streaming"
    elif motionStatus == 'recording':
      motion_text = "Recording"
    else:
      motion_text = "Stopped"

    refresh = needsRefresh
    needsRefresh = False

    status = {'PiStatus': cameraStatus, 'MotionStatus': motion_text, 'Camera': camera, 'Refresh': refresh}
    return render(request, 'camera.html', {'camera_status': status})


def camera_start(request, cam_id):
    try:
      id = int(cam_id)
    except ValueError:
      raise Http404()

    camera = Camera.objects.get(id=id)

    if(request.user.is_authenticated()):
      try:
        motionqueue = HotQueue("mymotionqueue", host=camera.ipaddress, port=6379, db=0)
        motionqueue.put('monitor')
      except:
        print "motionqueue error"
      return HttpResponseRedirect('/camera/%s' % cam_id)
    else:
      print "not authenticated"
      return HttpResponseRedirect("/login/")

def camera_stop(request, cam_id):
    global needsRefresh

    try:
      id = int(cam_id)
    except ValueError:
      raise Http404()

    camera = Camera.objects.get(id=id)
    needsRefresh = True

    if(request.user.is_authenticated()):
      try:
        motionqueue = HotQueue("mymotionqueue", host=camera.ipaddress, port=6379, db=0)
        motionqueue.put('stop')
      except:
        print "motionqueue error"
      return HttpResponseRedirect('/camera/%s' % cam_id)
    else:
      print "not authenticated"
      return HttpResponseRedirect("/login/")

def camera_snap(request, cam_id):
    try:
      id = int(cam_id)
    except ValueError:
      raise Http404()

    camera = Camera.objects.get(id=id)

    if(request.user.is_authenticated()):
      try:
        motionqueue = HotQueue("mymotionqueue", host=camera.ipaddress, port=6379, db=0)
        motionqueue.put('force_snap')
      except:
        print "motionqueue error"
      return HttpResponseRedirect('/camera/%s' % cam_id)
    else:
      print "not authenticated"
      return HttpResponseRedirect("/login/")

def camera_thumb(request, cam_id):
    try:
      id = int(cam_id)
    except ValueError:
      raise Http404()

    camera = Camera.objects.get(id=id)

    if(request.user.is_authenticated()):
      try:
        motionqueue = HotQueue("mymotionqueue", host=camera.ipaddress, port=6379, db=0)
        motionqueue.put('thumbnail')
      except:
        print "motionqueue error"
      return HttpResponseRedirect('/camera/%s' % cam_id)
    else:
      print "not authenticated"
      return HttpResponseRedirect("/login/")
      
def video_stream(request, cam_id):
    try:
      id = int(cam_id)
    except ValueError:
      raise Http404()

    camera = Camera.objects.get(id=id)

    if(request.user.is_authenticated()):
      try:
        motionqueue = HotQueue("mymotionqueue", host=camera.ipaddress, port=6379, db=0)
        motionqueue.put('video_stream')
      except:
        print "motionqueue error"
      return HttpResponseRedirect('/camera/%s' % cam_id)
    else:
      print "not authenticated"
      return HttpResponseRedirect("/login/")

def video_record(request, cam_id):
    try:
      id = int(cam_id)
    except ValueError:
      raise Http404()

    camera = Camera.objects.get(id=id)

    if(request.user.is_authenticated()):
      try:
        motionqueue = HotQueue("mymotionqueue", host=camera.ipaddress, port=6379, db=0)
        motionqueue.put('video_record')
      except:
        print "motionqueue error"
      return HttpResponseRedirect('/camera/%s' % cam_id)
    else:
      print "not authenticated"
      return HttpResponseRedirect("/login/")


def ping_device(host):
  # hostname = CAMERA_HOSTNAME  #example
  print host
  hostname = host  #example
  response = os.system("ping -c 1 " + hostname)

  return response


def run_zwave_cmd(ipaddr, port, cmd):

  url = 'http://' + ipaddr + ':' + str(port) + '/ZWaveAPI/Run/'
  url += cmd

  data = {}
  device_list = []

  try:
    serialized_data = urllib2.urlopen(url).read()
    data = json.loads(serialized_data)
  except:
    print 'failed to read zwave data'


def get_zwave_data(ipaddr, port):

  url = 'http://' + ipaddr + ':' + str(port) + '/ZWaveAPI/Data/0'

  data = {}
  device_list = []
  

  try:
    serialized_data = urllib2.urlopen(url).read()
    data = json.loads(serialized_data)
  except:
    print 'failed to read zwave data'

  if 'devices' in data:

    for device in sorted(data['devices']):
      #print data['devices'][device]
      if device != '1':
        for inst in data['devices'][device]['instances']:

            if inst == '0':
                if len(data['devices'][device]['instances']) > 1:
                    if '96' in data['devices'][device]['instances'][inst]['commandClasses']:
                        print "Found multichannel"
                        if data['devices'][device]['instances'][inst]['commandClasses']['96']['data']['supported']['value']:
                            print "Multichannel supported"
                            continue

            # print "Device: " + device + " Instance: " + inst
            devType_list = []

            for cc in sorted(data['devices'][device]['instances'][inst]['commandClasses']):

              nodeId = device
              ccData = data['devices'][device]['instances'][inst]['commandClasses'][cc]['data']
              #print data['devices'][device]['instances'][inst]['commandClasses'][cc]

              if cc == '37':
                devtype = 'Switch Binary'
                if 1 == ccData['level']['value']:
                   value = 'On'
                else:
                   value = 'Off'

                devType_list.append({'type': devtype, 'value': value})

              elif cc == '156':
                devtype = 'Alarm Sensor'

                # read the battery level
                if '128' in data['devices'][device]['instances'][inst]['commandClasses']:
                  value = "Battery level: " + str(data['devices'][device]['instances'][inst]['commandClasses']['128']['data']['last']['value']) + "%"

                devType_list.append({'type': devtype, 'value': value})

              elif cc == '48':
                devtype = 'Sensor Binary'
                for sense in ccData:
                    if sense.isdigit():
                        value = ccData[sense]['level']['value']
                        devType_list.append({'type': devtype, 'value': value})
          
              elif cc == '49':
                devtype = 'Sensor Multilevel'
                for sense in ccData:
                    if sense.isdigit():
                        value = ccData[sense]['sensorTypeString']['value'] + ": " + str(ccData[sense]['val']['value']) + " " + ccData[sense]['scaleString']['value']
                        devType_list.append({'type': devtype, 'value': value})

            if len(devType_list):
              device_list.append({'nodeId': nodeId, 'instance': inst, 'devtypes': devType_list})
              #device_list.append({'nodeId': nodeId, 'instance': inst, 'type': devtype, 'value': value})

  return device_list
          


@login_required(login_url='/login/')
def zwave_control(request):
    request.session.set_expiry(300)

    # Get controller list
    zwave_list = ZWaveController.objects.all()

    # Get device list from these controllers
    zwave_devices = []

    # Get Alarm list
    zwave_alarms = ZWaveAlarm.objects.all()
    
    for dev in zwave_list:
        #print 'Got ZWave device in list'
        nodes = get_zwave_data(dev.ipaddress, 8083)
        for n in nodes:
            #print 'Got node'
            n['controllerName'] = dev.name
            zwave_devices.append(n)

    return render(request, 'zwavecontroller_list.html', {'zwavecontrollers': zwave_list, 'zwavedevices': zwave_devices,
                    'zwavealarms': zwave_alarms})



@login_required(login_url='/login/')
def zwavecontroller(request, zwave_id):
    try:
      id = int(zwave_id)
    except ValueError:
      raise Http404()

    request.session.set_expiry(300)

    #print "Id is %d\n" % id
    zwave = ZWaveController.objects.get(id=id)

    if ping_device(zwave.ipaddress) == 0:
        zwavestatus = "Active"
    else: 
        zwavestatus = "Not available"

    status = {'PiStatus': zwavestatus, 'ZWaveController': zwave}
    return render(request, 'zwavecontroller.html', {'zwave_status': status})



@login_required(login_url='/login/')
def zwave_switch_off(request, cntr, dev, inst):
   request.session.set_expiry(300)

   #print "zwave_switch_off"
   zwave = ZWaveController.objects.get(name=cntr)
   #print zwave.ipaddress
   cmd = 'devices[' + dev + '].instances[' + inst + '].SwitchBinary.Set(0)'
   run_zwave_cmd(zwave.ipaddress, 8083, cmd)

   return HttpResponseRedirect("/zwave_control/")


@login_required(login_url='/login/')
def zwave_switch_on(request, cntr, dev, inst):
   request.session.set_expiry(300)

   #print "zwave_switch_on"
   zwave = ZWaveController.objects.get(name=cntr)
   #print zwave.ipaddress
   cmd = 'devices[' + dev + '].instances[' + inst + '].SwitchBinary.Set(255)'
   run_zwave_cmd(zwave.ipaddress, 8083, cmd)

   return HttpResponseRedirect("/zwave_control/")


@login_required(login_url='/login/')
def zwave_clear_alarms(request):
   request.session.set_expiry(300)

   #print "zwave_clear_alarms"
   zwave_alarms = ZWaveAlarm.objects.all()
   zwave_alarms.delete()

   return HttpResponseRedirect("/zwave_control/")

