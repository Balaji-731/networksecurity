import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(f"MONGO_DB_URL: {MONGO_DB_URL}")

import certifi
ca = certifi.where()
import pandas as pd
import pymongo
import numpy as np
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class NetworkDataExtraction():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def csv_to_json_converter(self, file_path):
        """
        This function will convert csv file to json file
        """
        try:
            data = pd.read_csv(file_path)
            logging.info(f"csv file: {file_path} loaded successfully")
            data.reset_index(drop=True, inplace=True)

            # Improved conversion
            records = data.to_dict(orient="records")

            logging.info(f"csv file: {file_path} converted to json successfully")
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def insert_data_mongodb(self, records, db_name, collection_name):
        """
        This function will insert data into mongodb collection
        """
        try:
            self.db_name = db_name
            self.collection_name = collection_name
            self.records = records

            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
            self.database = self.mongo_client[self.db_name]
            self.collection = self.database[self.collection_name]

            self.collection.insert_many(self.records)

            logging.info(f"{len(records)} records inserted into {db_name}.{collection_name}")
            return len(self.records)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
if __name__ == "__main__":
    FILE_PATH = "Network_Data/phisingData.csv"
    DATABASE_NAME = "network_security"
    COLLECTION_NAME = "NetworkData"

    networkobject = NetworkDataExtraction()
    records = networkobject.csv_to_json_converter(FILE_PATH)
    print(records[:2])  # print only first 2 (not whole 5000 rows)

    inserted_count = networkobject.insert_data_mongodb(records, DATABASE_NAME, COLLECTION_NAME)
    print(f"Inserted {inserted_count} records successfully.")
