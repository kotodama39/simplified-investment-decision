import pandas_datareader.data as web
import datetime
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# データ取得
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=365)
ticker = "{}.JP".format(1570)
df = web.DataReader(ticker, data_source="stooq").sort_index()

# MACDの計算
macd, signal, hist = talib.MACD(df["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
df["macd"] = macd
df["signal"] = signal
df["hist"] = hist

# 過去1年の範囲でスライス
df = df.loc[start_date:end_date]

# MACD戦略の定義
def MACD(data):
    return data.macd, data.signal

class MACDStrategy(Strategy):
    def init(self):
        self.macd, self.signal = self.I(MACD, self.data)

    def next(self):
        if crossover(self.macd, self.signal):
            self.buy()
        elif crossover(self.signal, self.macd):
            self.position.close()

# バックテストの実行
bt = Backtest(
    df,
    MACDStrategy,
    cash=1000000,
    trade_on_close=True,
)
stats = bt.run()
bt.plot()

print(stats)