from flask import Flask, jsonify
import yfinance as yf
import pandas as pd
import ta

app = Flask(__name__)

def get_signal():
    df = yf.download('XAUUSD=X', interval='5m', period='1d')
    if df.empty or len(df) < 50:
        return {"status": "No Data"}

    df['rsi'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    df['ema200'] = ta.trend.EMAIndicator(close=df['Close'], window=200).ema_indicator()
    df['macd'] = ta.trend.MACD(close=df['Close']).macd_diff()
    latest = df.iloc[-1]
    price = round(latest['Close'], 2)

    if (
        latest['rsi'] < 30 and
        latest['macd'] > 0 and
        price > latest['ema200']
    ):
        return {
            "status": "BUY",
            "entry": price,
            "stop_loss": round(price - 5, 2),
            "take_profit": round(price + 10, 2)
        }
    elif (
        latest['rsi'] > 70 and
        latest['macd'] < 0 and
        price < latest['ema200']
    ):
        return {
            "status": "SELL",
            "entry": price,
            "stop_loss": round(price + 5, 2),
            "take_profit": round(price - 10, 2)
        }
    else:
        return {"status": "No Signal"}

@app.route('/get-signal', methods=['GET'])
def get_signal_api():
    signal = get_signal()
    return jsonify(signal)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)