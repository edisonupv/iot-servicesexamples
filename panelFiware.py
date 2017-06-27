# Copyright 2014 Telefonica Investigacion y Desarrollo, S.A.U
# 
# This file is part of FIGWAY software (a set of tools for FIWARE Orion ContextBroker and IDAS2.6).
#
# FIGWAY is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as 
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# FIGWAY is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with FIGWARE. 
# If not, see http://www.gnu.org/licenses/
#
# For those usages not covered by the GNU Affero General Public License please contact with: Carlos Ralli Ucendo [ralli@tid.es] 
# Developed by Carlos Ralli Ucendo (@carlosralli), Nov 2014.
# New Features added/developped by Easy Global Market, Nov 2015 abbas.ahmad@eglobalmark.com 

import requests, json
import ConfigParser
import io
import sys
import random

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

ENTITY_ID= "panelsolarupv"                                           #The ID of the object
ENTITY_TYPE="panelsolar"                                                #The Type of the Object

ENTITY_ATTR="voltajeSTC"                                                #Attribute of the entity (properties of the object)
ENTITY_ATTR_TYPE="float"
ENTITY_ATTR_VALUE=str(voltajeSTC)

ENTITY_ATTR1="voltajeNOCT"
ENTITY_ATTR_TYPE1="float"
ENTITY_ATTR_VALUE1=str(voltajeNOCT)

ENTITY_ATTR2="intensidadSTC"
ENTITY_ATTR_TYPE2="float"
ENTITY_ATTR_VALUE2=str(intensidadSTC)

ENTITY_ATTR3="intensidadNOCT"
ENTITY_ATTR_TYPE3="float"
ENTITY_ATTR_VALUE3=str(intensidadNOCT)

ENTITY_ATTR4="temperaturapanel"
ENTITY_ATTR_TYPE4="float"
ENTITY_ATTR_VALUE4=str(temperaturapanel)

CONFIG_FILE = "/home/pi/fiware-figway/python-IDAS4/config.ini"          #The route of your config.ini 

# Load the configuration file
with open(CONFIG_FILE,'r+') as f:
    sample_config = f.read()
config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(io.BytesIO(sample_config))

CB_HOST=config.get('contextbroker', 'host')
CB_PORT=config.get('contextbroker', 'port')
CB_FIWARE_SERVICE=config.get('contextbroker', 'fiware_service')
CB_FIWARE_SERVICEPATH=config.get('contextbroker', 'fiware-service-path')
CB_AAA=config.get('contextbroker', 'OAuth')
if CB_AAA == "yes":
    TOKEN=config.get('user', 'token')
    TOKEN_SHOW=TOKEN[1:5]+"**********************************************************************"+TOKEN[-5:]
else:
    TOKEN="NULL"
    TOKEN_SHOW="NULL"

CB_URL = "http://"+CB_HOST+":"+CB_PORT
HEADERS = {'content-type': 'application/json','accept': 'application/json', 'Fiware-Service': CB_FIWARE_SERVICE ,'Fiware-ServicePath': CB_FIWARE_SERVICEPATH,'X-Auth-Token' : TOKEN}
HEADERS_SHOW = {'content-type': 'application/json', 'accept': 'application/json' , 'Fiware-Service': CB_FIWARE_SERVICE ,'Fiware-ServicePath': CB_FIWARE_SERVICEPATH , 'X-Auth-Token' : TOKEN_SHOW}

PAYLOAD = '{ \
    "contextElements": [ \
        { \
            "type": "'+ENTITY_TYPE+'", \
            "isPattern": "false",  \
            "id": "'+ENTITY_ID+'", \
            "attributes": [ \
            { \
                "name": "'+ENTITY_ATTR+'",  \
                "type": "'+ENTITY_ATTR_TYPE+'", \
                "value": "'+ENTITY_ATTR_VALUE+'" \
            }, \
            { \
                "name": "'+ENTITY_ATTR1+'",  \
                "type": "'+ENTITY_ATTR_TYPE1+'", \
                "value": "'+ENTITY_ATTR_VALUE1+'" \
            }, \
            { \
                "name": "'+ENTITY_ATTR2+'",  \
                "type": "'+ENTITY_ATTR_TYPE2+'", \
                "value": "'+ENTITY_ATTR_VALUE2+'" \
            }, \
            { \
                "name": "'+ENTITY_ATTR3+'",  \
                "type": "'+ENTITY_ATTR_TYPE3+'", \
                "value": "'+ENTITY_ATTR_VALUE3+'" \
            }, \
            { \
                "name": "'+ENTITY_ATTR4+'",  \
                "type": "'+ENTITY_ATTR_TYPE4+'", \
                "value": "'+ENTITY_ATTR_VALUE4+'" \
            } \
            ] \
        } \
    ], \
    "updateAction": "APPEND" \
}'

URL = CB_URL + '/v1/updateContext'

print "* Asking to "+URL
print "* Headers: "+str(HEADERS_SHOW)
print "* Sending PAYLOAD: "
print json.dumps(json.loads(PAYLOAD), indent=4)
print
print "..."
r = requests.post(URL, data=PAYLOAD, headers=HEADERS)
print
print "* Status Code: "+str(r.status_code)
print "* Response: "
print r.text
print
