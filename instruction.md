# コーディング指示書: MACDによる株価予測とバックテスト実装

## 概要

MACD（Moving Average Convergence Divergence）を用いて、株価チャートから売買シグナル（Buy / Sell）を検出するアルゴリズムを構築し、backtesting ライブラリを使用して過去のデータでその有効性を検証する Python コードを作成してください。

## 目的

- MACD 指標に基づく売買シグナルの検出ロジックの実装
- 過去の株価データを用いたバックテストによる有効性の評価

## 開発環境

| 項目             | 内容                        |
|------------------|-----------------------------|
| OS               | クロスプラットフォーム（Linux を想定） |
| Python バージョン| 3.11.8                      |
| 仮想環境         | venv を使用               |

## 使用ライブラリ

| ライブラリ名             | 用途               |
| ------------------ | ---------------- |
| pandas\_datareader | 株価データの取得         |
| pandas             | データ処理            |
| ta-lib             | テクニカル指標（MACD）の計算 |
| backtesting        | バックテストの実行        |
| matplotlib（任意）     | データ可視化（グラフ表示）    |


## 仕様要件

1. データ取得
   - 指定した銘柄（例: AAPL）の過去1年間の日次株価データを取得
   - データ取得元は Yahoo Finance（pandas_datareader.data.DataReader を使用）

2. MACD の計算
   - 12日EMAと26日EMAを計算してMACDラインを作成
   - MACDラインの9日EMAをシグナルラインとする
   - MACD - シグナル = MACDヒストグラム

### MACD の計算サンプル（TA-Lib 使用）

```python
import pandas_datareader.data as web
import datetime
import talib

# ▼ 日付範囲の設定（過去1年）
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=365)

# ▼ 銘柄の指定とデータ取得（Stooq）
ticker = "AAPL"
df = web.DataReader(ticker, data_source="stooq").sort_index()

# ▼ MACDの計算
# talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
macd, signal, hist = talib.MACD(df["Close"], fastperiod=12, slowperiod=26, signalperiod=9)

data = df[start_date : end_date]

# ▼ 計算結果のDataFrameへの追加
df["macd"] = macd
df["signal"] = signal
df["hist"] = hist
```

#### 補足

- talib.MACD() は 3つの配列を返します：
   - MACD：短期EMA - 長期EMA
   - Signal：MACDのシグナルライン（MACDの9日EMA）
   - Hist：MACDとSignalの差（MACDヒストグラム）

3. 売買シグナルルール

- 以下のルールに基づいて売買シグナルを判定：
   - 買いシグナル：MACDがシグナルラインを下から上にクロス
   - 売りシグナル：MACDがシグナルラインを上から下にクロス

4. バックテストロジック

- backtesting ライブラリの Strategy クラスを継承して実装
- 戦略名は MACDStrategy
- 初期資金、ポジションサイズなどは任意だが明示的に指定すること
- 結果として、勝率、リターン、トレード数などの評価指標を表示する

### backtesting のサンプル

```python
from backtesting import Strategy
from backtesting.lib import crossover

def MACD(data):
    return data.macd, data.signal

class MACDStrategy(Strategy):
    def init(self):
        self.macd, self.signal = self.I(MACD, self.data)

    def next(self):
        # 買いシグナル: MACDがシグナルラインを下から上にクロス
        if crossover(self.macd, self.signal):
            self.buy()

        # 売りシグナル: MACDがシグナルラインを上から下にクロス
        elif crossover(self.signal, self.macd):
            self.position.close()
```
