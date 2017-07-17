// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

#include "iothubtransportmqtt.h"
#include "schemalib.h"
#include "iothub_client.h"
#include "serializer_devicetwin.h"
#include "schemaserializer.h"
#include "azure_c_shared_utility/threadapi.h"
#include "azure_c_shared_utility/platform.h"

#include <stdio.h>
#include <stdlib.h>

static const char* deviceId = "**********************";    //Your device ID
static const char* connectionString = "**************";    //Connection String of your device ID

static const char* deviceInfo = "{ \"ObjectType\": \"DeviceInfo\","
"\"IsSimulatedDevice\": 1,"
"\"Version\" : '1.0',"
"\"DeviceProperties\" :"
"{\"DeviceID\": \"%s\", \"TelemetryInterval\" : 1, \"HubEnabledState\" : true},"
"\"Telemetry\" : ["
"{\"Name\": \"Temperature\", \"DisplayName\" : \"Temperature\", \"Type\" : \"double\"},"
"{ \"Name\": \"Humidity\", \"DisplayName\" : \"Humidity\", \"Type\" : \"double\" }] }";

static const char* telemetryData = "{"
"\"DeviceID\": \"%s\","

"\"voltajeSTC01\" : %.2f,"
"\"voltajeNOCT01\" : %.2f,"
"\"intensidadSTC01\" : %.2f,"
"\"intensidadNOCT01\" : %.2f,"
"\"temppanel01\" : %.2f } ";

static IOTHUB_CLIENT_HANDLE g_iotHubClientHandle = NULL;

/*json of supported methods*/
static char* supportedMethod = "{ \"LightBlink\": \"light blink\", \"ChangeLightStatus--LightStatusValue-int\""
": \"Change light status, on and off\" }";

// Define the Model
BEGIN_NAMESPACE(Contoso);

/* Reported properties */
DECLARE_STRUCT(SystemProperties,
ascii_char_ptr, FirmwareVersion
);

DECLARE_MODEL(ConfigProperties,
WITH_REPORTED_PROPERTY(uint8_t, TelemetryInterval)
);

DECLARE_DEVICETWIN_MODEL(Thermostat,
/* Device twin properties */
WITH_REPORTED_PROPERTY(ConfigProperties, Config),
WITH_REPORTED_PROPERTY(SystemProperties, System),

WITH_DESIRED_PROPERTY(uint8_t, TelemetryInterval, onDesiredTelemetryInterval),

/* Direct methods implemented by the device */
WITH_METHOD(LightBlink),
WITH_METHOD(ChangeLightStatus, int, LightStatusValue),

/* Register direct methods with solution portal */
WITH_REPORTED_PROPERTY(ascii_char_ptr_no_quotes, SupportedMethods)
);

END_NAMESPACE(Contoso);

/* Callback after sending reported properties */
void deviceTwinCallback(int status_code, void* userContextCallback)
{
	(void)(userContextCallback);
	printf("IoTHub: reported properties delivered with status_code = %u\n", status_code);
}

void onDesiredTelemetryInterval(void* argument)
{
	/* By convention 'argument' is of the type of the MODEL */
	Thermostat* thermostat = argument;
	printf("Received a new desired_TelemetryInterval = %d\r\n", thermostat->TelemetryInterval);
	thermostat->Config.TelemetryInterval = thermostat->TelemetryInterval;
	if (IoTHubDeviceTwin_SendReportedStateThermostat(thermostat, deviceTwinCallback, NULL) != IOTHUB_CLIENT_OK)
	{
		printf("Report Config.TelemetryInterval property failed");
	}
	else
	{
		printf("Report new value of Config.TelemetryInterval property: %d\r\n", thermostat->Config.TelemetryInterval);
	}
}

/*change light status on Raspberry Pi to received value*/
METHODRETURN_HANDLE ChangeLightStatus(Thermostat* thermostat, int lightstatus)
{
	printf("Raspberry Pi simulated light status change\n");
	return MethodReturn_Create(201, "\"simulated light status changed\"");
}

METHODRETURN_HANDLE LightBlink(Thermostat* thermostat)
{
	printf("Raspberry Pi simulated light blink\n");
	return MethodReturn_Create(201, "\"simulated light blink success\"");
}

/* Send data to IoT Hub */
static void sendMessage(IOTHUB_CLIENT_HANDLE iotHubClientHandle, const unsigned char* buffer, size_t size)
{
	IOTHUB_MESSAGE_HANDLE messageHandle = IoTHubMessage_CreateFromByteArray(buffer, size);
	if (messageHandle == NULL)
	{
		printf("unable to create a new IoTHubMessage\r\n");
	}
	else
	{
		if (IoTHubClient_SendEventAsync(iotHubClientHandle, messageHandle, NULL, NULL) != IOTHUB_CLIENT_OK)
		{
			printf("failed to hand over the message to IoTHubClient");
		}
		else
		{
			printf("IoTHubClient accepted the message for delivery\r\n");
		}

		IoTHubMessage_Destroy(messageHandle);
	}
	free((void*)buffer);
}

void SendDeviceInfo(IOTHUB_CLIENT_HANDLE iotHubClientHandle)
{
	char* buffer = malloc(sizeof(char) * 512);
	sprintf(buffer, deviceInfo, deviceId);
	printf("send device info: %s %d\r\n", buffer, strlen(buffer));
	sendMessage(iotHubClientHandle, buffer, strlen(buffer));
}

void SendTelemetryData(IOTHUB_CLIENT_HANDLE iotHubClientHandle)
{
	float voltajeSTC001 = (float)rand() / (float)(RAND_MAX / 5) + 25;
	float voltajeNOCT001 = (float)rand() / (float)(RAND_MAX / 5) + 15;
    float intensidadSTC001 = (float)rand() / (float)(RAND_MAX / 5) + 25;
    float intensidadNOCT001 = (float)rand() / (float)(RAND_MAX / 5) + 15;
    float temperaturapanel001 = (float)rand() / (float)(RAND_MAX / 5) + 25;

	char* buffer = malloc(sizeof(char) * 4096);
	sprintf(buffer, telemetryData, deviceId, voltajeSTC001, voltajeNOCT001, intensidadSTC001, intensidadNOCT001, temperaturapanel001
                                                   );

	printf("Sending sensor value: %s %d\r\n", buffer, strlen(buffer));
	sendMessage(iotHubClientHandle, buffer, strlen(buffer));
}

void remote_monitoring_run(void)
{
	if (platform_init() != 0)
	{
		printf("Failed to initialize the platform.\n");
	}
	else
	{
		if (SERIALIZER_REGISTER_NAMESPACE(Contoso) == NULL)
		{
			printf("Unable to SERIALIZER_REGISTER_NAMESPACE\n");
		}
		else
		{
			IOTHUB_CLIENT_HANDLE iotHubClientHandle = IoTHubClient_CreateFromConnectionString(connectionString, MQTT_Protocol);
			g_iotHubClientHandle = iotHubClientHandle;
			if (iotHubClientHandle == NULL)
			{
				printf("Failure in IoTHubClient_CreateFromConnectionString\n");
			}
			else
			{
#ifdef MBED_BUILD_TIMESTAMP
				// For mbed add the certificate information
				if (IoTHubClient_SetOption(iotHubClientHandle, "TrustedCerts", certificates) != IOTHUB_CLIENT_OK)
				{
					printf("Failed to set option \"TrustedCerts\"\n");
				}
#endif // MBED_BUILD_TIMESTAMP
				Thermostat* thermostat = IoTHubDeviceTwin_CreateThermostat(iotHubClientHandle);
				if (thermostat == NULL)
				{
					printf("Failure in IoTHubDeviceTwin_CreateThermostat\n");
				}
				else
				{
					/* Set values for reported properties */
					thermostat->Config.TelemetryInterval = 3;
					thermostat->System.FirmwareVersion = "1.0";
					/* Specify the signatures of the supported direct methods */
					thermostat->SupportedMethods = supportedMethod;

					/* Send reported properties to IoT Hub */
					if (IoTHubDeviceTwin_SendReportedStateThermostat(thermostat, deviceTwinCallback, NULL) != IOTHUB_CLIENT_OK)
					{
						printf("Failed sending serialized reported state\n");
					}
					else
					{
						thermostat->TelemetryInterval = 3;
						{
							SendTelemetryData(iotHubClientHandle);

							ThreadAPI_Sleep(thermostat->TelemetryInterval * 1000);
						}

						IoTHubDeviceTwin_DestroyThermostat(thermostat);
					}
				}
				IoTHubClient_Destroy(iotHubClientHandle);
			}
			serializer_deinit();
		}
	}
	platform_deinit();
}

int main(void)
{
	remote_monitoring_run();

	return 0;
}
