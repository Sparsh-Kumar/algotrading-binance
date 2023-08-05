import gc
import sys
import argparse
import pandas as pd
from logger import Logger
from loadenv import loadEnvironmentVariables
from binance import Client
from binance import BinanceSocketManager
from binanceHelper import BinanceHelper
from strategyCodes import SMA_CROSSOVER, SMA_CROSSOVER_RSI_TSL, REGULAR_MODE, SYNC_MODE

from strategies.smaCrossover import SMACrossOver
from strategies.smaCrossoverRSITSL import SMACrossOverRSITSL
from strategies.syncliveprize import SyncPriceInfo

def main():
    strategyCode = None
    strategyInstance = None
    argumentParser = argparse.ArgumentParser(description='Algo Trading Binance.')
    argumentParser.add_argument('--quantity', type=float, dest='quantity', help='Quantity of asset to trade.')
    argumentParser.add_argument('--symbol', type=str, dest='symbol', help='Asset Symbol.')
    argumentParser.add_argument('--number', type=int, dest='number', help='Number Of Trades to Execute.')
    argumentParser.add_argument('--strategy', type=str, choices=[SMA_CROSSOVER, SMA_CROSSOVER_RSI_TSL], dest='strategy', help=f'Strategy code to use ({ SMA_CROSSOVER }, { SMA_CROSSOVER_RSI_TSL })')
    argumentParser.add_argument('--mode', type=str, choices=[REGULAR_MODE, SYNC_MODE], dest='mode', help=f'Mode of the bot ({REGULAR_MODE}, {SYNC_MODE})')
    arguments = argumentParser.parse_args()
    loggerInstance = Logger()
    jsonEnvContent = loadEnvironmentVariables(loggerInstance, 'binance.json')
    binanceClient = Client(jsonEnvContent['BINANCE_API_KEY'], jsonEnvContent['BINANCE_API_SECRET'])

    strategyCode = arguments.strategy
    assetSymbol = arguments.symbol
    quantity = arguments.quantity
    numberOfTrades = arguments.number
    mode = arguments.mode

    if mode == REGULAR_MODE or not mode:
        if not strategyCode or not assetSymbol or not quantity or not numberOfTrades:
            raise Exception(f'[-] If the mode is not regular mode, then strategyCode, assetSymbol, quantity, numberOfTrades are mandatory.')
        if strategyCode == SMA_CROSSOVER:
            strategyConfig = { 'short': 20, 'long': 50, 'sl': 0.005 }
            for i in range (numberOfTrades):
                strategyInstance = SMACrossOver(jsonEnvContent, binanceClient, loggerInstance, strategyConfig)
                strategyInstance.executeStrategy(assetSymbol, quantity)
                del strategyInstance
                gc.collect()
        if strategyCode == SMA_CROSSOVER_RSI_TSL:
            strategyConfig = { 'short': 20, 'long': 50, 'sl': 0.005, 'rsi': 50 }
            for i in range(numberOfTrades):
                strategyInstance = SMACrossOverRSITSL(jsonEnvContent, binanceClient, loggerInstance, strategyConfig)
                strategyInstance.executeStrategy(assetSymbol, quantity)
                del strategyInstance
                gc.collect()
    elif mode == SYNC_MODE:
        if not assetSymbol:
            raise Exception(f'Asset Symbol is required in sync mode.')
        syncPriceInfoInstance = SyncPriceInfo(jsonEnvContent, binanceClient, loggerInstance, assetSymbol)
        syncPriceInfoInstance.syncInformation()
        del syncPriceInfoInstance
        gc.collect()

if __name__ == '__main__':
    main()
