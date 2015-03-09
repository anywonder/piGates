var http = require('http');
var util = require('util');
var sqlite3 = require('sqlite3').verbose();

var ZWaveAPIData = { updateTime: 0 };
var ZWaveAlarm = {};
var controllerName = '';

var options = {
   host: '',
   port: 8083,
   path: '/ZWaveAPI/Data/',
   method: 'POST',
};

var dbPath = '/home/pi/Projects/Django/myGates/mygatesdb'


function dumpZWayData() {

   for(var nodeId in ZWaveAPIData.devices) {
      //console.log("Found nodeId: " + nodeId);

      var controllerNodeId = ZWaveAPIData.controller.data.nodeId.value;
      if (nodeId == 255 || nodeId == controllerNodeId) {
         // We skip broadcase and self
         continue;
      }

      var device = ZWaveAPIData.devices[nodeId];

      var basicType = device.data.basicType.value;
      var genericType = device.data.genericType.value;
      var specificType = device.data.specificType.value;


      for(var instance in device.instances) {

         if(instance == 0 && Object.keys(device.instances).length > 1) {
            //console.log("Skip instance: " + instance + " length: " + Object.keys(device.instances).length);

            // Look for Multichannel cc and whether supported or not.  If supported then skip this instance
            // otherwise this instance contains the data
            //
            if('96' in device.instances[instance].commandClasses) {
               //console.log("Found Multichannel");
               if(device.instances[instance].commandClasses[96].data.supported.value == true) {
                  //console.log("Multichannel supported");
                  continue;
               }
            }
         }

         for(var cc in device.instances[instance].commandClasses) {
            //console.log("CC: " + cc);

            if(0x25 == cc) {
               //console.log("Switch Binary");
               //console.log("Switch Binary dev: " + nodeId + " inst: " + instance);
            }

            if(0x9c == cc) {
               //console.log("Alarm sensor");
            }

            if(0x30 == cc) {

               for(var sense in device.instances[instance].commandClasses[cc].data) {

                  // 1 = General Purpose
                  // 2 = 2 = Smoke
                  // 3 = Carbon monoxide
                  // 4 = Carbon dioxide
                  // 5 = Heat
                  // 6 = Water
                  // 7 = Freeze
                  // 8 = Tamper
                  // 9 = Aux
                  // 10 = Door Window
                  // 11 = Tilt
                  // 12 = Motion
                  // 13 = Glass break

                  if(false == isNaN(sense)) {
                     //console.log("Sensor Binary: " + device.instances[instance].commandClasses[cc].data[sense].sensorTypeString.value + " Level: " + device.instances[instance].commandClasses[cc].data[sense].level.value);
                  }
               }
            }

            if(0x31 == cc) {

               for(var sense in device.instances[instance].commandClasses[cc].data) {
                  if(false == isNaN(sense)) {
                     //console.log("Sensor Multilevel: " + device.instances[instance].commandClasses[cc].data[sense].sensorTypeString.value + ": " + device.instances[instance].commandClasses[cc].data[sense].val.value + " " + device.instances[instance].commandClasses[cc].data[sense].scaleString.value);
                  }
               }
            }
         }

      }
   }

   var cur = ZWaveAPIData.devices[2].instances[0].commandClasses[37].data.level.value;
   //console.log('Switch: ' + cur); 
}


// Run ZWaveAPI command via HTTP POST
function runCmd(cmd, success_cbk) {

   options.path = '/ZWaveAPI/Run/' + cmd;
   console.log("runCmd: " + options.path);

   var req = http.request(options, function(res) {

      res.setEncoding('utf-8');

      var responseString = '';

      res.on('data', function(data) {
         responseString += data;
      });

      res.on('end', function() {
         var resultObject = JSON.parse(responseString);
      });

   });

   req.end();
};


function initDeviceEventHandlers() {

   for(var nodeId in ZWaveAPIData.devices) {

      var controllerNodeId = ZWaveAPIData.controller.data.nodeId.value;
      if (nodeId == 255 || nodeId == controllerNodeId) {
         // We skip broadcase and self
         continue;
      }

      var device = ZWaveAPIData.devices[nodeId];

      for(var instance in device.instances) {

         for(var cc in device.instances[instance].commandClasses) {

            if(0x25 == cc) {
               console.log("Switch Binary Handler");
               device.updateEvent = function(x) { 
                  runCmd('devices[' + x + '].SwitchBinary.Get()');
               };
                  
            }

            if(0x9c == cc) {
               console.log("Alarm sensor Handler");

               // Need to loop through each sensor type ( 5 == water ) and add event handler for each
               //
               for(var sense in device.instances[instance].commandClasses[cc].data) {

                  //var alarmpath = 'devices.' + nodeId + '.instances.' + instance + '.commandClasses.' + cc + '.data.' + sense + '.sensorState';
                  var alarmpath = 'devices.' + nodeId + '.instances.' + instance + '.commandClasses.' + cc + '.data.' + sense;

                  if(0x5 == sense) {
                     // Flood sensor
                     //
                     //console.log("Alarm path: " + alarmpath);
                     ZWaveAlarm[alarmpath] = function(x, y) { 
                        // x is nodeId
                        // y is path

                        var eventType = "Flood sensor event"
                        var eventData = null;
                        var device = ZWaveAPIData.devices[x];

                        console.log("Sensor state: " + device.instances[0].commandClasses[0x9c].data[5].sensorState.value);
                        if(255 == device.instances[0].commandClasses[0x9c].data[5].sensorState.value) {
                           eventData = "sensorState = 255 (Water detected!)"
                           console.log("Flood sensor detecting water!!");
                        } else {
                           eventData = "sensorState = 0 (Dry!)"
                           console.log("Flood sensor is dry");
                        }
                        //console.log(ZWaveAPIData[y]);

                        var db = new sqlite3.Database(dbPath);
                        //console.log(controllerName)
                        //console.log(x)
                        var now = new Date().toISOString();
                        db.run("INSERT INTO zwave_zwavealarm VALUES(?, ?, ?, ?, ?, ?)", null, controllerName, x, now, eventType, eventData);
                        db.close();
                     };
                  }

               }
            }

            if(0x30 == cc) {
               console.log("Sensor Binary Handler");

               // Need to loop through each sensor type ( 1 == general purpose ) and add event handler for each
               //
               for(var sense in device.instances[instance].commandClasses[cc].data) {

                  //var alarmpath = 'devices.' + nodeId + '.instances.' + instance + '.commandClasses.' + cc + '.data.' + sense + '.sensorState';
                  var alarmpath = 'devices.' + nodeId + '.instances.' + instance + '.commandClasses.' + cc + '.data.' + sense;

                  if(0x1 == sense) {
                     // General Purpose sensor
                     //
                     //console.log("Alarm path: " + alarmpath);
                     ZWaveAlarm[alarmpath] = function(x, y) { 
                        // x is nodeId
                        // y is path

                        var eventType = "General Purpose sensor event"
                        var eventData = null;
                        var device = ZWaveAPIData.devices[x];

                        console.log("Sensor state: " + device.instances[0].commandClasses[0x30].data[1].sensorState.value);
                        if(255 == device.instances[0].commandClasses[0x30].data[1].sensorState.value) {
                           eventData = "sensorState = 255 (Motion detected!)"
                           console.log("Motion sensor detecting motion!!");
                        } else {
                           eventData = "sensorState = 0 (No Activity!)"
                           console.log("Motion sensor is quiet");
                        }
                        //console.log(ZWaveAPIData[y]);

                        var db = new sqlite3.Database(dbPath);
                        //console.log(controllerName)
                        //console.log(x)
                        var now = new Date().toISOString();
                        db.run("INSERT INTO zwave_zwavealarm VALUES(?, ?, ?, ?, ?, ?)", null, controllerName, x, now, eventType, eventData);
                        db.close();
                     };
                  }

               }
            }
         }

      }
   }

}


function readZWay() {
   options.path = '/ZWaveAPI/Data/' + ZWaveAPIData.updateTime;

   var req = http.request(options, function(res) {

      res.setEncoding('utf-8');

      var responseString = '';

      res.on('data', function(data) {
         responseString += data;
         });

      res.on('end', function() {
         var resultObject = JSON.parse(responseString);

         var previousUpdateTime = ZWaveAPIData.updateTime;

         var pobj = ZWaveAPIData;
         for (var prop in resultObject) {

            var pobj = ZWaveAPIData;
            var pe_arr = prop.split('.');
            for (var pe in pe_arr.slice(0, -1)) {
               pobj = pobj[pe_arr[pe]];
            }
            pobj[pe_arr.slice(-1)] = resultObject[prop];
         }

         if(previousUpdateTime == 0) {
            // Set up callbacks
            //
            initDeviceEventHandlers();
            
         } else {
            // Look for event updates
            //
            for (var prop in resultObject) {

               var pe_arr = prop.split('.');

               if(pe_arr.slice(-1) == "nodeInfoFrame") {

                  for(var index in resultObject[prop].value) {
                     if(0x25 == resultObject[prop].value[index]) {
                        // pe_arr[1] is the nodeId
                        var device = ZWaveAPIData.devices[pe_arr[1]];
                        device.updateEvent(pe_arr[1]);
                     }
                  }

               } else {

                  if(ZWaveAlarm[prop]) {
                     ZWaveAlarm[prop](pe_arr[1], prop);
                  }

               }
            }

            if( Object.keys(resultObject).length > 1) {
                // Don't print the updateTime updates
                console.log(resultObject);
            }
         }

         dumpZWayData();

      });

   });

   req.end();
}

// Main application starts here
//
var db = new sqlite3.Database(dbPath);

db.serialize(function() {
  query = "SELECT * FROM zwave_zwavecontroller where id=" + process.argv[2];
  console.log("DB Query: " + query);
  db.get(query, function(err, row) {
     if(row) {
        console.log("ControllerName: " + row.name);
        options.host = row.ipaddress;
        controllerName = row.name;
     } else {
        console.log("Could not retrieve zwaveController from db");
        process.exit(1);
     }
  });

});

db.close();

process.on('uncaughtException', function (err) {
    console.log(err);
}); 

setInterval(readZWay, 5000);

