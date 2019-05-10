import datetime
import logging

import azure.functions as func

import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
from azure.storage.file import FileService
import datetime
from dateutil import tz
import numpy as np
import os

TRIGGER_INTERVAL = 60
YEAR_OFFSET = 1

def SetupConnection() -> tuple:
    config = {
        'ENDPOINT': 'https://nyc-taxi-db.documents.azure.com:443/',
        'PRIMARYKEY': 'KBG7C3paCypMhRD4kquiVkdPzPaWcsyCZcjUadwuYUq9Y7Np3ppxuw7NlorC1spEmpCgt7niznVrsDopmBU61w==',
        'DATABASE': 'TripRecords',
        'CONTAINER': 'YellowCabs2'
    }

    # Initialize the Cosmos client
    client = cosmos_client.CosmosClient(url_connection=config['ENDPOINT'], auth={
                                        'masterKey': config['PRIMARYKEY']})

    # Connect to a database
    database_link = 'dbs/' + config['DATABASE']

    # Connect to a container
    container_link = database_link + '/colls/{0}'.format(config['CONTAINER'])

    return client, container_link


def QueryDocumentsWithCustomQuery(client, collection_link: str, query_with_optional_parameters: dict):
    try:
        results = list(client.QueryItems(collection_link, query_with_optional_parameters))
        logging.info("%d records found." % len(results))
        return results
    except errors.HTTPFailure as e:
        if e.status_code == 404:
            logging.info("Document doesn't exist")
        elif e.status_code == 400:
            # Can occur when we are trying to query on excluded paths
            logging.info("Bad Request exception occured: %s" % str(e))
        return


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    # Download models
    to_zone = tz.gettz("America/New_York")
    now = datetime.datetime.now()
    now = now.astimezone(to_zone)
    logging.info("Current time: %s." % now)
    month = now.month

    file_service = FileService(
        account_name='nyctaxistorageacc', 
        account_key='26+AjeiwRNGlLNa6P4J8+xOdReRs/xqNIM2qS4JYr0ZeFQ1C9aTF45IiaGnPXgG7KCg498Q8bcfsRNvCOCaC3A=='
    )
    if not os.path.exists('data'):
        os.makedirs('data')
    file_service.get_file_to_path('nyc-taxi-db', None, '%02d-cnt.npy' % month, 'data/%02d-cnt.npy' % month, open_mode='wb')
    file_service.get_file_to_path('nyc-taxi-db', None, '%02d-total-fare.npy' % month, 'data/%02d-total-fare.npy' % month, open_mode='wb')
    logging.info('Successfully downloaded model for month %d.' % month)

    # Load models
    total_fare = np.load("data/%02d-total-fare.npy" % month)
    cnt = np.load("data/%02d-cnt.npy" % month)
    logging.info('Successfully loaded model for month %d.' % month)

    # Retrieve cached data from Azure Cosmos DB
    client, collection_link = SetupConnection()
    query_dt = now - datetime.timedelta(days=365 * YEAR_OFFSET, hours=1)
    query = {
        "query": "SELECT * FROM r WHERE r.year=@year AND r.month=@month AND r.day=@day AND r.hour=@hour",
        "parameters": [
            {"name":"@year", "value": query_dt.year},
            {"name":"@month", "value": query_dt.month},
            {"name":"@day", "value": query_dt.day},
            {"name":"@hour", "value": query_dt.hour}
        ]
    }
    records = QueryDocumentsWithCustomQuery(client, collection_link, query)

    # Update models
    weekday = query_dt.weekday()
    row_idx = weekday * 24 + query_dt.hour
    logging.info("Updating model for %s (%d):" % (str(query_dt), weekday))
    if records is None or len(records) == 0:
        logging.info("Nothing updated.")
    else:
        for record in records:
            assert record["year"] == query_dt.year
            assert record["month"] == query_dt.month
            assert record["day"] == query_dt.day
            assert record["hour"] == query_dt.hour
            PULocationID = record["PULocationID"]
            if PULocationID < 264:
                col_idx = PULocationID - 1
                # logging.info("PULocationID=%d, old count=%d, old fare=%.2f;" % (PULocationID, cnt[row_idx, col_idx], total_fare[row_idx, col_idx]))
                cnt[row_idx, col_idx] += 1
                total_fare[row_idx, col_idx] += record["total_fare"]
                # logging.info("PULocationID=%d, new count=%d, new fare=%.2f;" % (PULocationID, cnt[row_idx, col_idx], total_fare[row_idx, col_idx]))
        
        # Save models
        np.save("data/%02d-cnt.npy" % month, cnt)
        np.save("data/%02d-total-fare.npy" % month, total_fare)
        logging.info('Successfully saved model for month %d.' % month)

        # Upload models
        file_service.create_file_from_path('nyc-taxi-db', None, '%02d-cnt.npy' % month, 'data/%02d-cnt.npy' % month)
        file_service.create_file_from_path('nyc-taxi-db', None, '%02d-total-fare.npy' % month, 'data/%02d-total-fare.npy' % month)
        logging.info('Successfully uploaded model for month %d.' % month)
