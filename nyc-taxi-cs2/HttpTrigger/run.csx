#r "Newtonsoft.Json"

using System.Net;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Primitives;
using Newtonsoft.Json;

public static IActionResult Run(HttpRequest req, out object tripRecordDocument, ILogger log)
{
    log.LogInformation("C# HTTP trigger function processed a request.");

    string record = "{\"VendorID\":\"1\",\"tpep_pickup_datetime\":\"2018-12-01 00:28:22\",\"tpep_dropoff_datetime\":\"2018-12-01 00:44:07\",\"passenger_count\":\"2\",\"trip_distance\":\"2.50\",\"RatecodeID\":\"1\",\"store_and_fwd_flag\":\"N\",\"PULocationID\":\"148\",\"DOLocationID\":\"234\",\"payment_type\":\"1\",\"fare_amount\":\"12\",\"extra\":\"0.5\",\"mta_tax\":\"0.5\",\"tip_amount\":\"3.95\",\"tolls_amount\":\"0\",\"improvement_surcharge\":\"0.3\",\"total_amount\":\"17.25\"}";
    dynamic tripRecord = JsonConvert.DeserializeObject(record);
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
        return (ActionResult)new OkResult();
    }
    else
    {
        tripRecordDocument = null;
        log.LogInformation("Bad request");
        return (ActionResult)new BadRequestResult();
    }
}
