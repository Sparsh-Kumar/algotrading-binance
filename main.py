import gc
import argparse
import pandas as pd
from logger import Logger
from loadenv import loadEnvironmentVariables
from binance import Client
from binance import BinanceSocketManager
from binanceHelper import BinanceHelper
from strategyCodes import SMA_CROSSOVER

from strategies.smaCrossover import SMACrossOver

def main():
    strategyCode = None
    strategyInstance = None
    argumentParser = argparse.ArgumentParser(description='Algo Trading Binance.')
    argumentParser.add_argument('--quantity', type=float, dest='quantity', help='Quantity of asset to trade.')
    argumentParser.add_argument('--symbol', type=str, dest='symbol', help='Asset Symbol.')
    argumentParser.add_argument('--number', type=int, dest='number', help='Number Of Trades to Execute.')
    argumentParser.add_argument('--strategy', type=str, choices=[SMA_CROSSOVER], dest='strategy', help=f'Strategy code to use ({ SMA_CROSSOVER })')
    arguments = argumentParser.parse_args()
    loggerInstance = Logger()
    jsonEnvContent = loadEnvironmentVariables(loggerInstance, 'binance.json')
    binanceClient = Client(jsonEnvContent['BINANCE_API_KEY'], jsonEnvContent['BINANCE_API_SECRET'])

    strategyCode = arguments.strategy
    assetSymbol = arguments.symbol
    quantity = arguments.quantity
    numberOfTrades = arguments.number

    if strategyCode == SMA_CROSSOVER:
        strategyConfig = { 'short': 20, 'long': 50, 'sl': 0.005 }
        for i in range (numberOfTrades):
            strategyInstance = SMACrossOver(jsonEnvContent, binanceClient, loggerInstance, strategyConfig)
            strategyInstance.executeStrategy(assetSymbol, quantity)
            del strategyInstance
            gc.collect()

if __name__ == '__main__':
    main()
