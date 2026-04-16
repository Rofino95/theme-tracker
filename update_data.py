import pandas as pd
import yfinance as yf

INPUT_FILE = "themes_clean.xlsx"
OUTPUT_FILE = "themes_clean.xlsx"

def fetch_prices(ticker: str):
    t = yf.Ticker(ticker)
    hist = t.history(period="1y", interval="1d", auto_adjust=False)

    if hist.empty:
        return None, None, None

    close = float(hist["Close"].dropna().iloc[-1])
    high_52w = float(hist["High"].max())
    low_52w = float(hist["Low"].min())
    return close, high_52w, low_52w

def main():
    df = pd.read_excel(INPUT_FILE)

    updated_prices = []
    updated_highs = []
    updated_lows = []

    for ticker in df["Ticker"]:
        try:
            price, high, low = fetch_prices(str(ticker))
        except Exception:
            price, high, low = None, None, None

        updated_prices.append(price)
        updated_highs.append(high)
        updated_lows.append(low)

    df["Preis"] = updated_prices
    df["52W High"] = updated_highs
    df["52W Low"] = updated_lows

    df = df.dropna(subset=["Preis", "52W High", "52W Low"]).copy()

    df["Trend Score"] = (
        (df["Preis"] - df["52W Low"]) / (df["52W High"] - df["52W Low"])
    )

    df["Momentum"] = (
        (df["Preis"] - ((df["52W High"] + df["52W Low"]) / 2))
        / ((df["52W High"] - df["52W Low"]) / 2)
    )

    df["Trend Score"] = df["Trend Score"].round(2)
    df["Momentum"] = df["Momentum"].round(2)

    df.to_excel(OUTPUT_FILE, index=False)
    print("themes_clean.xlsx aktualisiert")

if __name__ == "__main__":
    main()
