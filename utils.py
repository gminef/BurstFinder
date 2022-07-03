from time import time
import pandas as pd
from pathlib import Path
import datetime
import callistoDownloader

def read_parameters_file(parameters_file_path):
    df = pd.read_csv(parameters_file_path)
    return df

def create_output_folder(folder_path):
    path = Path(folder_path)
    path.mkdir(parents=True, exist_ok=True)

def get_current_utc_time():
    utc_time = datetime.datetime.now(datetime.timezone.utc)
    utc_time.month
    return utc_time

def download_current_date_data(time,instrument_code): # example 2022-05-27 11:27:24.051235
    callistoDownloader.download(time.year,time.month,time.day,instrument_code)

