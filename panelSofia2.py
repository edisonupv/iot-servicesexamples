# -*- coding: utf8 -*-
'''
 Python SSAP API
 Version 1.5
 
 © Indra Sistemas, S.A.
 2014  SPAIN
  
 All rights reserved
'''
import time
import random
import unittest
from ssap.core import SSAP_QUERY_TYPE
from ssap.factories import SSAPEndpointFactory
from ssap.tests.utils.callbacks import TestCallback

class TestInserts(unittest.TestCase):
    
    ONTOLOGY = "PanelSolar021UPV"                 #Name of ontology that you were created before
    TOKEN = "*********************************"   #Token of ontology
    INSTANCE = "PanelSolar021UPVKP:Instancia01"   #Instance that you created for the KP that will consume the information 

    voltajeSTC1 = random.uniform(30,35)           #Random data to send to Sofia2
    voltajeSTC = round(voltajeSTC1,2)
    voltajeNOCT1 = random.uniform(27,32)
    voltajeNOCT = round(voltajeNOCT1,2)
    intensidadSTC1 = random.uniform(8,12)
    intensidadSTC = round(intensidadSTC1,2)
    intensidadNOCT1 = random.uniform(6,10)
    intensidadNOCT = round(intensidadNOCT1,2)
    temperaturapanel1 = random.uniform(43,48)
    temperaturapanel = round(temperaturapanel1,2)
   

    hora = time.strftime("%H:%M:%S.000Z")        #Timestamp necessary in Sofia2
    fecha = time.strftime("%Y-%m-%d")
    json = fecha + "T" + hora
   
    print voltajeSTC
    print voltajeNOCT
    print intensidadSTC
    print intensidadNOCT
    print temperaturapanel
    print json
  
    #JSON Message to insert into Sofia2 with the five properties of the ontology (timestamp too!!)
    ONTOLOGY_INSERT_SQLLIKE = "INSERT INTO PanelSolar021UPV(voltajeSTC, voltajeNOCT, intensidadSTC, intensidadNOCT, temperaturapanel, timeadd) values (" + str(voltajeSTC) + "," + str(voltajeNOCT) + "," + str(intensidadSTC) + "," + str(intensidadNOCT) + "," + str(temperaturapanel) + "," + " \"{ '$date': '" + json + "'}\")"
    print ONTOLOGY_INSERT_SQLLIKE

    def setUp(self):
        self.__serverURL = 'ws://sofia2.com/sib/api_websocket'
        self.__callback = TestCallback(True)
        self.__doJoin()
    
    def __doJoin(self):
         self.__endpoint = SSAPEndpointFactory.buildWebsocketBasedSSAPEndpoint(self.__serverURL, self.__callback, True)
         self.__callback.prepareToReceiveSsapResponse()
         self.__endpoint.joinWithToken(TestInserts.TOKEN, TestInserts.INSTANCE)
         self.__callback.waitForSsapResponse()
         self.assertTrue(self.__callback.isSsapResponseOk())
        
    def testSuccessfulSqlLikeInsert(self):
        self.__callback.prepareToReceiveSsapResponse()
        self.__endpoint.insert(TestInserts.ONTOLOGY, TestInserts.ONTOLOGY_INSERT_SQLLIKE, SSAP_QUERY_TYPE.SQLLIKE)
        self.__callback.waitForSsapResponse()
        self.assertTrue(self.__callback.isSsapResponseOk())

if __name__ == "__main__":
    unittest.main()
