import sys
import time
import json
import os
import pandas as pd
import numpy as np
import uuid
from datetime import datetime
from binanceHelper import BinanceHelper
from pymongo import MongoClient
from pymongo import ReturnDocument

class SyncPriceInfo(BinanceHelper):
    def __init__ (self, creds, binanceClient, loggerInstance, assetSymbol):
        super().__init__ (binanceClient, loggerInstance)
        self.creds = creds
        self.sleepTime = 5 # In Seconds
        self.dbClient = None
        self.databaseHandle = None
        self.collectionHandle = None
        self.assetSymbol = assetSymbol
        self.dbConnect()

    def dbConnect(self):
        try:
            self.dbClient = MongoClient(self.creds['databaseURI'])
            self.databaseHandle = self.dbClient.get_database(self.creds['databaseName'])
            self.collectionHandle = self.databaseHandle[self.assetSymbol]
        except Exception as e:
            self.loggerInstance.logError(str(e))
            sys.exit()

    def syncInformation(self):
        try:
            while True:
                [priceInfo] = self.getLivePrice(self.assetSymbol)
                self.collectionHandle.insert_one(
                    {
                        'timestamp': priceInfo[0],
                        'price': priceInfo[1],
                        'assetSymbol': self.assetSymbol,
                    }
                )
                time.sleep(self.sleepTime)

        except Exception as e:
            self.loggerInstance.logError(str(e))
            sys.exit()

    def __del__ (self):
        pass


