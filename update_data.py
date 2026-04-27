import os
import pandas as pd
import yfinance as yf
import wikipedia
from datetime import datetime
from deep_translator import GoogleTranslator

INPUT_FILE = "theme_universe.csv"
OUTPUT_FILE = "theme_scores.csv"


def get_existing_descriptions():
    if not os.path.exists(OUTPUT_FILE):
        return {}

    try:
        old_df = pd.read_csv(OUTPUT_FILE)

        if "Ticker" not in old_df.columns or "Description" not in old_df.columns:
            return {}

        old_df["Description"] = old_df["Description"].fillna("")
        return dict(zip(old_df["Ticker"], old_df["Description"]))

    except Exception as e:
        print(f"Konnte alte Beschreibungen nicht laden: {e}")
        return {}


def get_description(ticker, name, existing_description):
    if existing_description and str(existing_description).strip():
        return existing_description

    description = ""

    try:
        data = yf.Ticker(ticker)
        info = data.info
        description = info.get("longBusinessSummary") or ""
    except Exception as e:
        print(f"Yahoo-Beschreibung Fehler bei {ticker}: {e}")

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

    return description


def fetch_data(ticker, existing_description=""):
    try:
        data = yf.Ticker(ticker)
        info = data.info
        hist = data.history(period="1y")

        if hist.empty:
            return None, None, None, None, ticker, existing_description, None, None, None, None, None, None

        price = hist["Close"].iloc[-1]
        high = hist["High"].max()
        low = hist["Low"].min()

        if len(hist) >= 64:
            price_3m_ago = hist["Close"].iloc[-64]
            momentum_3m = (price / price_3m_ago) - 1
        else:
            momentum_3m = None

        name = info.get("shortName") or info.get("longName") or ticker
        description = get_description(ticker, name, existing_description)

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
            momentum_3m,
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
        return None, None, None, None, ticker, existing_description, None, None, None, None, None, None


def main():
    df = pd.read_csv(INPUT_FILE, sep=None, engine="python")
    df.columns = df.columns.str.strip()

    existing_descriptions = get_existing_descriptions()

    prices = []
    highs = []
    lows = []
    momentum_3m_list = []
    names = []
    descriptions = []

    pe_list = []
    forward_pe_list = []
    revenue_growth_list = []
    earnings_growth_list = []
    profit_margin_list = []
    market_cap_list = []

    for ticker in df["Ticker"]:
        existing_description = existing_descriptions.get(ticker, "")

        (
            price,
            high,
            low,
            momentum_3m,
            name,
            description,
            pe,
            forward_pe,
            revenue_growth,
            earnings_growth,
            profit_margin,
            market_cap
        ) = fetch_data(ticker, existing_description)

        prices.append(price)
        highs.append(high)
        lows.append(low)
        momentum_3m_list.append(momentum_3m)
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
    df["3M Momentum"] = momentum_3m_list
    df["Name"] = names
    df["Description"] = descriptions

    df["PE"] = pe_list
    df["Forward PE"] = forward_pe_list
    df["Revenue Growth"] = revenue_growth_list
    df["Earnings Growth"] = earnings_growth_list
    df["Profit Margin"] = profit_margin_list
    df["Market Cap"] = market_cap_list

    df = df.dropna(subset=["Preis", "52W High", "52W Low"]).copy()

    df["Trend Score"] = (df["Preis"] - df["52W Low"]) / (df["52W High"] - df["52W Low"])
    df["Momentum"] = (
        (df["Preis"] - ((df["52W High"] + df["52W Low"]) / 2)) /
        ((df["52W High"] - df["52W Low"]) / 2)
    )

    df["Trend Score"] = df["Trend Score"].round(2)
    df["Momentum"] = df["Momentum"].round(2)
    df["3M Momentum"] = df["3M Momentum"].round(2)

    df.to_csv(OUTPUT_FILE, index=False)

    with open("last_update.txt", "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M"))

    print("Fertig: theme_scores.csv erstellt")


if __name__ == "__main__":
    main()
    
