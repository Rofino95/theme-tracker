import pandas as pd
import yfinance as yf
import wikipedia
from deep_translator import GoogleTranslator
from datetime import datetime

INPUT_FILE = "theme_universe.csv"
OUTPUT_FILE = "theme_scores.csv"

def fetch_data(ticker):
    try:
        data = yf.Ticker(ticker)
        info = data.info
        hist = data.history(period="1y")

        if hist.empty:
            return None, None, None, ticker, ""

        price = hist["Close"].iloc[-1]
        high = hist["High"].max()
        low = hist["Low"].min()

        name = info.get("shortName") or info.get("longName") or ticker

        # 1. Erst Yahoo versuchen
        description_en = info.get("longBusinessSummary") or ""

        # 2. Wenn Yahoo nichts liefert -> Wikipedia Fallback
        if not description_en or len(description_en.strip()) < 50:
            try:
                wikipedia.set_lang("de")
                description_en = wikipedia.summary(name, sentences=3)
            except:
                try:
                    wikipedia.set_lang("en")
                    description_en = wikipedia.summary(name, sentences=3)
                except:
                    description_en = ""

        # 3. Falls Beschreibung nicht deutsch ist -> nach deutsch uebersetzen
        description = description_en
        if description_en:
            try:
                description = GoogleTranslator(source="auto", target="de").translate(description_en)
            except:
                description = description_en

        return price, high, low, name, description

    except:
        return None, None, None, ticker, ""

def main():
    df = pd.read_csv(INPUT_FILE, sep=None, engine="python")
    df.columns = df.columns.str.strip()

    prices = []
    highs = []
    lows = []
    names = []
    descriptions = []

    for ticker in df["Ticker"]:
    price, high, low, name, description = fetch_data(ticker)
    prices.append(price)
    highs.append(high)
    lows.append(low)
    names.append(name)
    descriptions.append(description)
    
    df["Preis"] = prices
    df["52W High"] = highs
    df["52W Low"] = lows
    df["Name"] = names
    df["Description"] = descriptions

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
