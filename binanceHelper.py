import sys
import pytz
import pandas as pd
from datetime import datetime, timedelta

class BinanceHelper:
    def __init__ (self, creds, binanceClient, loggerInstance):
        self.creds = creds
        self.binanceClient = binanceClient
        self.loggerInstance = loggerInstance

    def getLivePrice(self, tickerSymbol = None):
        try:
            tickerInfo = None
            if not tickerSymbol:
                raise Exception('Ticker symbol required.')
            allTickersInfo = self.binanceClient.get_all_tickers()
            for i in range(len(allTickersInfo)):
                if allTickersInfo[i]['symbol'] == tickerSymbol:
                    tickerInfo = allTickersInfo[i]
                    break
            return tickerInfo
        except Exception as e:
            self.loggerInstance.logError(str(e))
            sys.exit(1)

    def getKLinesData(self, tickerSymbol = None, fromDaysBack = 5, candleTimePeriod = '1h', timeZone = 'Asia/Kolkata'):
        try:
            if not tickerSymbol:
                raise Exception('Ticker symbol required.')
            endDate = datetime.now()
            startDate = endDate - timedelta(days = fromDaysBack)
            startDate = startDate.strftime('%d %b, %Y')
            endDate = endDate.strftime('%d %b, %Y')
            kLinesInfo = self.binanceClient.get_historical_klines(
                tickerSymbol,
                candleTimePeriod,
                startDate
            )
            dataFrame = pd.DataFrame(
                data = [row[1:7] for row in kLinesInfo],
                columns = ['open', 'high', 'low', 'close', 'volume', 'time']
            ).set_index('time')
            dataFrame.index = pd.to_datetime(dataFrame.index + 1, unit = 'ms')
            dataFrame.index = dataFrame.index.tz_localize(pytz.UTC).tz_convert(timeZone)
            dataFrame = dataFrame.sort_index()
            dataFrame = dataFrame.apply(pd.to_numeric, axis = 1)
            return dataFrame
        except Exception as e:
            self.loggerInstance.logError(str(e))
            sys.exit(1)

    def __del__ (self):
        pass
