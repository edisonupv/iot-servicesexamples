# *****************************************************************************
# Copyright (c) 2014 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html 
#
# Contributors:
#   David Parker - Initial Contribution
# *****************************************************************************

import time
import sys
import pprint
import uuid
import random

try:
	import ibmiotf.application
	import ibmiotf.device
except ImportError:
	# This part is only required to run the sample from within the samples
	# directory when the module itself is not installed.
	#
	# If you have the module installed, just use "import ibmiotf.application" & "import ibmiotf.device"
	import os
	import inspect
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../src")))
	if cmd_subfolder not in sys.path:
		sys.path.insert(0, cmd_subfolder)
	import ibmiotf.application
	import ibmiotf.device

organization = "cg6c6c"
deviceType = "panelsolarupv"
deviceId = "panelsolarupv002"
authMethod = "token"
authToken = "2&2hys+wyVFrwb31L)"

voltajeSTC1 = random.uniform(30,35)
voltajeSTC = round(voltajeSTC1,2)
voltajeNOCT1 = random.uniform(27,32)
voltajeNOCT = round(voltajeNOCT1,2)
intensidadSTC1 = random.uniform(8,12)
intensidadSTC = round(intensidadSTC1,2)
intensidadNOCT1 = random.uniform(6,10)
intensidadNOCT = round(intensidadNOCT1,2)
temperaturapanel1 = random.uniform(43,48)
temperaturapanel = round(temperaturapanel1,2)

# Initialize the device client.
try:
	deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
	deviceCli = ibmiotf.device.Client(deviceOptions)
except Exception as e:
	print("Caught exception connecting device: %s" % str(e))
	sys.exit()

# Connect and send a datapoint into the cloud as an event of type "status"
deviceCli.connect()
myData = {'voltajeSTC': voltajeSTC, 'voltajeNOCT': voltajeNOCT, 'intensidadSTC': intensidadSTC, 'intensidadNOCT': intensidadNOCT, 'temperaturapanel': temperaturapanel}
def myOnPublishCallback():
	print("Confirmed event %s received by IoTF\n")
success = deviceCli.publishEvent("status", "json", myData, qos=0, on_publish=myOnPublishCallback)
if not success:
	print("Not connected to IoTF")
time.sleep(1)

# Disconnect the device and application from the cloud
deviceCli.disconnect()
