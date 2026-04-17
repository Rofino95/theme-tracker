import pandas as pd
import yfinance as yf

INPUT_FILE = "theme_universe.csv"
OUTPUT_FILE = "theme_scores.csv"

def fetch_data(ticker):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="1y")

        if hist.empty:
            return None, None, None

        price = hist["Close"].iloc[-1]
        high = hist["High"].max()
        low = hist["Low"].min()

        return price, high, low
    except:
        return None, None, None

def main():
    df = pd.read_csv(INPUT_FILE, sep=None, engine="python")
    df.columns = df.columns.str.strip()

    print(df.columns.tolist())

    prices = []
    highs = []
    lows = []

    for ticker in df["Ticker"]:
        price, high, low = fetch_data(ticker)
        prices.append(price)
        highs.append(high)
        lows.append(low)

    df["Preis"] = prices
    df["52W High"] = highs
    df["52W Low"] = lows

    df = df.dropna()

    df["Trend Score"] = (df["Preis"] - df["52W Low"]) / (df["52W High"] - df["52W Low"])
    df["Momentum"] = (
        (df["Preis"] - ((df["52W High"] + df["52W Low"]) / 2)) /
        ((df["52W High"] - df["52W Low"]) / 2)
    )

    df["Trend Score"] = df["Trend Score"].round(2)
    df["Momentum"] = df["Momentum"].round(2)

    df.to_csv(OUTPUT_FILE, index=False)

    print("Fertig: theme_scores.csv erstellt")

if __name__ == "__main__":
    main()