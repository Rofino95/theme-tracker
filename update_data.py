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
            return None, None, None, ticker, "", None, None, None, None, None, None

        price = hist["Close"].iloc[-1]
        high = hist["High"].max()
        low = hist["Low"].min()

        name = info.get("shortName") or info.get("longName") or ticker

        description = info.get("longBusinessSummary") or ""

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

        if description and len(description.strip()) > 0:
            try:
                description = GoogleTranslator(source="auto", target="de").translate(description)
            except Exception as e:
                print(f"Uebersetzungsfehler bei {ticker}: {e}")

        pe = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        revenue_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")
        profit_margin = info.get("profitMargins")
        market_cap = info.get("marketCap")

        return (
            price,
            high,
            low,
            name,
            description,
            pe,
            forward_pe,
            revenue_growth,
            earnings_growth,
            profit_margin,
            market_cap
        )

    except Exception as e:
        print(f"Fehler bei {ticker}: {e}")
        return None, None, None, ticker, "", None, None, None, None, None, None


def main():
    df = pd.read_csv(INPUT_FILE, sep=None, engine="python")
    df.columns = df.columns.str.strip()

    prices = []
    highs = []
    lows = []
    names = []
    descriptions = []

    pe_list = []
    forward_pe_list = []
    revenue_growth_list = []
    earnings_growth_list = []
    profit_margin_list = []
    market_cap_list = []

    for ticker in df["Ticker"]:
        (
            price,
            high,
            low,
            name,
            description,
            pe,
            forward_pe,
            revenue_growth,
            earnings_growth,
            profit_margin,
            market_cap
        ) = fetch_data(ticker)

        prices.append(price)
        highs.append(high)
        lows.append(low)
        names.append(name)
        descriptions.append(description)

        pe_list.append(pe)
        forward_pe_list.append(forward_pe)
        revenue_growth_list.append(revenue_growth)
        earnings_growth_list.append(earnings_growth)
        profit_margin_list.append(profit_margin)
        market_cap_list.append(market_cap)

    df["Preis"] = prices
    df["52W High"] = highs
    df["52W Low"] = lows
    df["Name"] = names
    df["Description"] = descriptions

    df["PE"] = pe_list
    df["Forward PE"] = forward_pe_list
    df["Revenue Growth"] = revenue_growth_list
    df["Earnings Growth"] = earnings_growth_list
    df["Profit Margin"] = profit_margin_list
    df["Market Cap"] = market_cap_list

    df = df.dropna(subset=["Preis", "52W High", "52W Low"])

    df["Trend Score"] = (df["Preis"] - df["52W Low"]) / (df["52W High"] - df["52W Low"])
    df["Momentum"] = (
        (df["Preis"] - ((df["52W High"] + df["52W Low"]) / 2)) /
        ((df["52W High"] - df["52W Low"]) / 2)
    )

    df["Trend Score"] = df["Trend Score"].round(2)
    df["Momentum"] = df["Momentum"].round(2)

    df.to_csv(OUTPUT_FILE, index=False)

    with open("last_update.txt", "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M"))

    print("Fertig: theme_scores.csv erstellt")

    if __name__ == "__main__":
        main()
