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

class SMACrossOver(BinanceHelper):
    def __init__ (self, creds, binanceClient, loggerInstance, strategyConfig = {}):
        super().__init__(binanceClient, loggerInstance)
        self.strategyConfig = strategyConfig
        self.creds = creds
        self.sleepTime = 2 # In seconds
        self.uuidOfTrade = None
        self.stopLossPrice = None
        self.buyAssetPrice = None
        self.totalAssetBuyPrice = None
        self.sellAssetPrice = None
        self.totalAssetSellPrice = None
        self.position = None
        self.dbClient = None
        self.databaseHandle = None
        self.collectionHandle = None
        self.buyOrderDetails = None
        self.sellOrderDetails = None
        self.mongoDbBuyOrderDetailsDoc = None
        self.mongoDbSellOrderDetailsDoc = None
        self.dbConnect()
        self.initializeTradeInDB()
    
    def dbConnect(self):
        try:
            self.dbClient = MongoClient(self.creds['databaseURI'])
            self.databaseHandle = self.dbClient.get_database(self.creds['databaseName'])
            self.collectionHandle = self.databaseHandle[f"trades-{datetime.now().strftime('%Y-%m-%d')}"]
        except Exception as e:
            self.loggerInstance.logError(str(e))
            sys.exit()

    def initializeTradeInDB(self):
        try:
            self.uuidOfTrade = str(uuid.uuid4())
            if self.collectionHandle is not None:
                self.collectionHandle.insert_one({ 'tradeId': self.uuidOfTrade })
        except Exception as e:
            self.loggerInstance.logError(str(e))
            sys.exit()

    def executeStrategy(self, symbol = None, quantity = None):
        try:
            if not symbol:
                raise Exception('Asset symbol required.')
            if not quantity or quantity < 0:
                raise Exception('Asset quantity required.')
            self.collectionHandle.find_one_and_update({ 'tradeId': self.uuidOfTrade}, { '$set': {'assetSymbol': symbol } })

            # Buying Loop
            while True:
                time.sleep(self.sleepTime)
                klineData = self.getKLinesData(symbol, 1, '1m') # 1 min candle from last 1 day.
                klineData = klineData.dropna()
                klineData = klineData[klineData['volume'] != 0]
                klineData['shortsma'] = klineData['close'].rolling(self.strategyConfig['short']).mean()
                klineData['longsma'] = klineData['close'].rolling(self.strategyConfig['long']).mean()

                if (self.position is None) and (klineData.iloc[-1]['shortsma'] > klineData.iloc[-1]['longsma']) and (klineData.iloc[-2]['shortsma'] < klineData.iloc[-2]['longsma']):
                    self.position = 'long'
                    self.buyAssetPrice = klineData.iloc[-1]['close']
                    self.totalAssetBuyPrice = self.buyAssetPrice * quantity
                    self.stopLossPrice = self.buyAssetPrice * (1 - self.strategyConfig['sl'])
                    self.mongoDbBuyOrderDetailsDoc = self.collectionHandle.find_one_and_update(
                        {
                            'tradeId': self.uuidOfTrade
                        },
                        {
                            '$set': {
                                'buyAssetPrice': self.buyAssetPrice,
                                'stopLossPrice': self.stopLossPrice,
                                'quantity': quantity,
                                'totalAssetBuyPrice': self.totalAssetBuyPrice,
                                'timeOfBuy': str(klineData.index[-1]),
                            }
                        },
                        return_document=ReturnDocument.AFTER
                    )
                    print(f"Bought the asset {self.mongoDbBuyOrderDetailsDoc}")
                    break

                os.system('cls' if os.name == 'nt' else 'clear')
                print('\nTrying to Buy\n=============')
                print(klineData)

            # Selling Loop
            while True:
                time.sleep(self.sleepTime)
                klineData = self.getKLinesData(symbol, 1, '1m') # 1 min candle from last 1 day.
                klineData = klineData.dropna()
                klineData = klineData[klineData['volume'] != 0]
                klineData['shortsma'] = klineData['close'].rolling(self.strategyConfig['short']).mean()
                klineData['longsma'] = klineData['close'].rolling(self.strategyConfig['long']).mean()

                if (self.position == 'long') and (((klineData.iloc[-1]['shortsma'] < klineData.iloc[-1]['longsma']) and (klineData.iloc[-2]['shortsma'] > klineData.iloc[-2]['longsma'])) or (klineData.iloc[-1]['close'] <= self.stopLossPrice)):
                    self.position = None
                    self.sellAssetPrice = klineData.iloc[-1]['close']
                    self.totalAssetSellPrice = self.sellAssetPrice * quantity
                    stopLossHit = bool(klineData.iloc[-1]['close'] <= self.stopLossPrice)
                    self.mongoDbSellOrderDetailsDoc = self.collectionHandle.find_one_and_update(
                        {
                            'tradeId': self.uuidOfTrade
                        },
                        {
                            '$set': {
                                'sellAssetPrice': self.sellAssetPrice,
                                'quantity': quantity,
                                'totalAssetSellPrice': self.totalAssetSellPrice,
                                'timeOfSell': str(klineData.index[-1]),
                                'stopLossHit': stopLossHit
                            }
                        },
                        return_document=ReturnDocument.AFTER
                    )
                    print(f"Sold the asset {self.mongoDbSellOrderDetailsDoc}")
                    break

                os.system('cls' if os.name == 'nt' else 'clear')
                print('\nTrying to Sell\n=============')
                print(self.mongoDbBuyOrderDetailsDoc)
                print(klineData)

        except Exception as e:
            self.loggerInstance.logError(str(e))
            sys.exit()

    def __del__ (self):
        pass
