import pandas as pd
import yfinance as yf
import wikipedia
from datetime import datetime
from deep_translator import GoogleTranslator

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
        description = info.get("longBusinessSummary") or ""

                # 2. Wenn Yahoo nichts liefert -> Wikipedia Fallback
        if not description or len(description.strip()) < 50:
            try:
                wikipedia.set_lang("en")
                results = wikipedia.search(name)

                if not results:
                    results = wikipedia.search(f"{ticker} company")

                if results:
                    description = wikipedia.summary(results[0], sentences=3, auto_suggest=False)
                else:
                    description = ""
            except Exception as e:
                print(f"Wikipedia-Fehler bei {ticker}: {e}")
                description = ""

        # 3. Wenn Beschreibung vorhanden ist -> ins Deutsche uebersetzen
        if description and len(description.strip()) > 0:
            try:
                description = GoogleTranslator(source="auto", target="de").translate(description)
            except Exception as e:
                print(f"Uebersetzungsfehler bei {ticker}: {e}")

        return price, high, low, name, description

    except Exception as e:
        print(f"Fehler bei {ticker}: {e}")
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

    df.to_csv(OUTPUT_FILE, index=False)

    with open("last_update.txt", "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M"))

    print("Fertig: theme_scores.csv erstellt")
    print(df[df["Ticker"].isin(["META", "NVDA", "CVX"])][["Ticker", "Name", "Description"]])


if __name__ == "__main__":
    main()
