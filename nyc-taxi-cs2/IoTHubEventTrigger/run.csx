#r "Newtonsoft.Json"

using System;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Primitives;
using Newtonsoft.Json;

public static void Run(string myIoTHubMessage, out object tripRecordDocument, ILogger log)
{
    // log.LogInformation($"C# IoT Hub trigger function processed a message: {myIoTHubMessage}");
    dynamic tripRecord = JsonConvert.DeserializeObject(myIoTHubMessage);
    char[] charSeparators = new char[] {'-', ' ', ':'};
    string[] tpep_pickup_datetime = Convert.ToString(tripRecord.tpep_pickup_datetime).Split(charSeparators);
    int year = Int32.Parse(tpep_pickup_datetime[0]);
    int month = Int32.Parse(tpep_pickup_datetime[1]);
    int day = Int32.Parse(tpep_pickup_datetime[2]);
    DateTime dt = new DateTime(year, month, day);
    int day_of_week = ((int)(dt.DayOfWeek) + 6) % 7;
    int hour = Int32.Parse(tpep_pickup_datetime[3]);
    int PULocationID = Convert.ToInt32(tripRecord.PULocationID);
    double total_fare = Convert.ToDouble(tripRecord.total_amount);

    // We need both name and task parameters.
    if (tripRecord != null)
    {
        tripRecordDocument = new{year, month, day, day_of_week, hour, PULocationID, total_fare};
        log.LogInformation($"Month: {month}, Day of week: {day_of_week}, Hour: {hour}, PULocationID: {PULocationID}, Total fare: {total_fare}");
        // return (ActionResult)new OkResult();
    }
    else
    {
        tripRecordDocument = null;
        log.LogInformation("Bad request");
        // return (ActionResult)new BadRequestResult();
    }
}
