import logging

import azure.functions as func

import datetime
from dateutil import tz
import json
import numpy as np


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    to_zone = tz.gettz("America/New_York")
    now = datetime.datetime.now()
    now = now.astimezone(to_zone)
    weekday = now.weekday()
    month = now.month
    hour = now.hour
    row_idx = weekday * 24 + hour

    logging.info('Using data for month %d.' % month)
    total_fare = np.load("data/%02d-total-fare.npy" % month)
    cnt = np.load("data/%02d-cnt.npy" % month)
    fare = np.divide(total_fare, cnt, out=np.zeros_like(total_fare), where=(cnt != 0))
    curr_fare = fare[row_idx]

    idx = np.argsort(-curr_fare)[:3]
    top3_result = [(idx + 1).tolist(), (curr_fare[idx]).tolist()]
    all_result = curr_fare.tolist()
    res = {
        "top3_results": top3_result,
        "all_results": all_result
    }
    return json.dumps(res)
