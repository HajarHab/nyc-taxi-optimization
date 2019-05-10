'use strict';

var clientFromConnectionString = require('azure-iot-device-mqtt').clientFromConnectionString;
var Message = require('azure-iot-device').Message;

const fs = require('fs');

let rawdata = fs.readFileSync('0507-10_test/201805920.json');  
let trips_data = JSON.parse(rawdata);  

var count = 0
function azcall()
{
	var connectionString = 'HostName=nyc-taxi-hub.azure-devices.net;DeviceId=Summer_taxi;SharedAccessKey=466Zh7EynYp2unQkMVl1qpNkZTMCV2ZJt/qyT3BIa5w='; 

	var client = clientFromConnectionString(connectionString);
	function printResultFor(op) 
	{
		return function printResult(err, res) 
		{
			if (err) console.log(op + ' error: ' + err.toString());
			if (res) console.log(op + ' status: ' + res.constructor.name);
		};
	}

	var connectCallback = function (err) 
	{
		if (err) 
		{
			console.log('Could not connect: ' + err);
		} 
		else 
		{
			console.log('Client connected');
			pubData();
			function pubData()
			{  
				var data;
				
				if(trips_data[count]["PULocationID"]>263 || trips_data[count]["DOLocationID"]>263){
					count += 1
					return;
				}
				data = JSON.stringify(trips_data[count]);
				var message = new Message(data);
				console.log("Sending message: " + message.getData());
				count += 1;
				console.log(count)
				if(count >= trips_data.length){
					throw new Error("ALL DATA SENT TO HUB!");
				}
				client.sendEvent(message, printResultFor('send'));
			}
		}
	};
	client.open(connectCallback);
}

setInterval(azcall, 100);
