//............................................ Connection to Artik Cloud...........................................
var webSocketUrl = "wss://api.artik.cloud/v1.1/websocket?ack=true";
var device_id = "***********************************";       //Your DEVIDE ID
var device_token = "***********************************";    //Your DEVICE TOKEN
var isWebSocketReady = false;
var ws = null;
var WebSocket = require('ws');
//.....................................................................................................................


//........................Values from solar panel to send.......................................
var voltajeSTC= round(Math.random() * (40 - 30 + 1) + 30, 2); 
var voltajeNOCT= round(Math.random() * (45 - 35 + 1) + 35, 2);
var intensidadSTC= round(Math.random() * (12 - 8 + 1) + 8, 2);
var intensidadNOCT= round(Math.random() * (14 - 10 + 1) + 10, 2);
var temperaturapanel= round(Math.random() * (30 - 20 + 1) + 20, 2);

//...............................Fuction Random..................
function round(value, exp) {
	  if (typeof exp === 'undefined' || +exp === 0)
	    return Math.round(value);

	  value = +value;
	  exp  = +exp;

	  if (isNaN(value) || !(typeof exp === 'number' && exp % 1 === 0))
	    return NaN;

	  // Shift
	  value = value.toString().split('e');
	  value = Math.round(+(value[0] + 'e' + (value[1] ? (+value[1] + exp) : exp)));

	  // Shift back
	  value = value.toString().split('e');
	  return +(value[0] + 'e' + (value[1] ? (+value[1] - exp) : -exp));
	}

//..........................Get time ...............
function getTimeMillis(){
    return parseInt(Date.now().toString());
	}

//.......................Create channel from Raspberry Pi to send at Artik Cloud.........................
function start() {
    isWebSocketReady = false;
    ws = new WebSocket(webSocketUrl);
    ws.on('open', function() {
        console.log("Websocket connection is open ....");
        register();
    });
    ws.on('message', function(data, flags) {
        console.log("Received message: " + data + '\n');
    });
    ws.on('close', function() {
        console.log("Websocket connection is closed ....");
    });
}

//..................Sends a register message to the websocket and starts the message flooder........................
function register(){
    console.log("Registering device on the websocket connection");
    try{
        var registerMessage = '{"type":"register", "sdid":"'+device_id+'", "Authorization":"bearer '+device_token+'", "cid":"'+getTimeMillis()+'"}';
        console.log('Sending register message ' + registerMessage + '\n');
        ws.send(registerMessage, {mask: true});
        isWebSocketReady = true;
    	sendData(voltajeSTC, voltajeNOCT, intensidadSTC, intensidadNOCT, temperaturapanel);
	    }
    catch (e) {
        console.error('Failed to register messages. Error in registering message: ' + e.toString());
    }   
}

//........................Send one message to ARTIK Cloud..............................................
function sendData(voltajeSTC, voltajeNOCT, intensidadSTC, intensidadNOCT, temperaturapanel){
    try{
        ts = ', "ts": '+getTimeMillis();
        var data = {
            "voltajeSTC": voltajeSTC,
	    "voltajeNOCT": voltajeNOCT,
            "intensidadSTC": intensidadSTC,
            "intensidadNOCT": intensidadNOCT,
            "temperaturapanel": temperaturapanel
        };
        var payload = '{"sdid":"'+device_id+'"'+ts+', "data": '+JSON.stringify(data)+', "cid":"'+getTimeMillis()+'"}';
        console.log('Sending payload ' + payload);
        ws.send(payload, {mask: true});
    } catch (e) {
        console.error('Error in sending a message: ' + e.toString());
    }   
}

//................Start Script.................................
start();
