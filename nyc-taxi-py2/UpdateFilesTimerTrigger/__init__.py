import datetime
import logging

import azure.functions as func
from azure.storage.file import FileService
import os


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    # https://docs.microsoft.com/en-us/azure/storage/files/storage-python-how-to-use-file-storage
    file_service = FileService(
        account_name='nyctaxistorageacc', 
        account_key='26+AjeiwRNGlLNa6P4J8+xOdReRs/xqNIM2qS4JYr0ZeFQ1C9aTF45IiaGnPXgG7KCg498Q8bcfsRNvCOCaC3A=='
    )
    if not os.path.exists('data'):
        os.makedirs('data')
    for i in range(1, 13):
        file_service.get_file_to_path('nyc-taxi-db', None, '%02d-cnt.npy' % i, 'data/%02d-cnt.npy' % i, open_mode='wb')
        file_service.get_file_to_path('nyc-taxi-db', None, '%02d-total-fare.npy' % i, 'data/%02d-total-fare.npy' % i, open_mode='wb')
    logging.info('Successfully updated model.')
