import pandas as pd
from logger import Logger
from loadenv import loadEnvironmentVariables
from binance import Client
from binance import BinanceSocketManager
from binanceHelper import BinanceHelper

def main():
    ticker = 'BTCUSDT'
    loggerInstance = Logger()
    jsonEnvContent = loadEnvironmentVariables(loggerInstance, 'binance.json')
    binanceClient = Client(jsonEnvContent['BINANCE_API_KEY'], jsonEnvContent['BINANCE_API_SECRET'])

if __name__ == '__main__':
    main()
