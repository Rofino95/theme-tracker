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
                description = wikipedia.summary(
                    results[0],
                    sentences=3,
                    auto_suggest=False
                )
            else:
                description = ""

        except Exception as e:
            print(f"Wikipedia-Fehler bei {ticker}: {e}")
            description = ""

    if description and len(description.strip()) > 0:

        try:
            description = GoogleTranslator(
                source="auto",
                target="de"
            ).translate(description)

        except Exception as e:
            print(f"Uebersetzungsfehler bei {ticker}: {e}")

    return description


def calculate_momentum(hist, days):
    try:
        if len(hist) >= days + 1:
            current_price = hist["Close"].iloc[-1]
            old_price = hist["Close"].iloc[-days]

            if old_price != 0:
                return (current_price - old_price) / old_price

    except Exception:
        return None

    return None


def calculate_moving_averages(hist, price):
    ma50 = None
    ma200 = None
    ma50_distance = None
    ma200_distance = None
    price_above_ma50 = None
    price_above_ma200 = None

    try:
        if len(hist) >= 50:
            ma50 = hist["Close"].rolling(50).mean().iloc[-1]

            if pd.notna(ma50) and ma50 != 0:
                ma50_distance = (price - ma50) / ma50
                price_above_ma50 = price > ma50

        if len(hist) >= 200:
            ma200 = hist["Close"].rolling(200).mean().iloc[-1]

            if pd.notna(ma200) and ma200 != 0:
                ma200_distance = (price - ma200) / ma200
                price_above_ma200 = price > ma200

    except Exception:
        pass

    return (
        ma50,
        ma200,
        ma50_distance,
        ma200_distance,
        price_above_ma50,
        price_above_ma200
    )


def calculate_volume_data(hist):
    volume = None
    avg_volume = None
    volume_ratio = None

    try:
        if "Volume" not in hist.columns:
            return volume, avg_volume, volume_ratio

        volume_series = hist["Volume"].dropna()

        if volume_series.empty:
            return volume, avg_volume, volume_ratio

        volume = volume_series.iloc[-1]

        if len(volume_series) >= 20:
            avg_volume = volume_series.tail(20).mean()
        else:
            avg_volume = volume_series.mean()

        if pd.notna(avg_volume) and avg_volume != 0:
            volume_ratio = volume / avg_volume

    except Exception:
        pass

    return volume, avg_volume, volume_ratio


def empty_result(ticker, existing_description):
    return (
        None, None, None,
        ticker,
        existing_description,
        None, None, None,
        None, None, None,
        None, None, None,
        None, None, None, None,
        None, None,
        None, None, None
    )


def fetch_data(ticker, existing_description=""):

    try:
        data = yf.Ticker(ticker)

        info = data.info

        hist = data.history(period="1y")

        if hist.empty:
            return empty_result(ticker, existing_description)

        price = hist["Close"].iloc[-1]

        high = hist["High"].max()
        low = hist["Low"].min()

        name = (
            info.get("shortName")
            or info.get("longName")
            or ticker
        )

        description = get_description(
            ticker,
            name,
            existing_description
        )

        pe = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        revenue_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")
        profit_margin = info.get("profitMargins")
        market_cap = info.get("marketCap")

        momentum_3m = calculate_momentum(hist, 63)
        momentum_1m = calculate_momentum(hist, 21)
        momentum_20d = calculate_momentum(hist, 20)

        (
            ma50,
            ma200,
            ma50_distance,
            ma200_distance,
            price_above_ma50,
            price_above_ma200
        ) = calculate_moving_averages(hist, price)

        (
            volume,
            avg_volume,
            volume_ratio
        ) = calculate_volume_data(hist)

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
            market_cap,
            momentum_3m,
            momentum_1m,
            momentum_20d,
            ma50,
            ma200,
            ma50_distance,
            ma200_distance,
            price_above_ma50,
            price_above_ma200,
            volume,
            avg_volume,
            volume_ratio
        )

    except Exception as e:

        print(f"Fehler bei {ticker}: {e}")

        return empty_result(ticker, existing_description)


def main():

    df = pd.read_csv(
        INPUT_FILE,
        sep=None,
        engine="python"
    )

    df.columns = df.columns.str.strip()

    existing_descriptions = get_existing_descriptions()

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

    momentum_3m_list = []
    momentum_1m_list = []
    momentum_20d_list = []

    ma50_list = []
    ma200_list = []
    ma50_distance_list = []
    ma200_distance_list = []
    price_above_ma50_list = []
    price_above_ma200_list = []

    volume_list = []
    avg_volume_list = []
    volume_ratio_list = []

    for ticker in df["Ticker"]:

        existing_description = existing_descriptions.get(ticker, "")

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
            market_cap,
            momentum_3m,
            momentum_1m,
            momentum_20d,
            ma50,
            ma200,
            ma50_distance,
            ma200_distance,
            price_above_ma50,
            price_above_ma200,
            volume,
            avg_volume,
            volume_ratio

        ) = fetch_data(
            ticker,
            existing_description
        )

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

        momentum_3m_list.append(momentum_3m)
        momentum_1m_list.append(momentum_1m)
        momentum_20d_list.append(momentum_20d)

        ma50_list.append(ma50)
        ma200_list.append(ma200)
        ma50_distance_list.append(ma50_distance)
        ma200_distance_list.append(ma200_distance)
        price_above_ma50_list.append(price_above_ma50)
        price_above_ma200_list.append(price_above_ma200)

        volume_list.append(volume)
        avg_volume_list.append(avg_volume)
        volume_ratio_list.append(volume_ratio)

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

    df["3M Momentum"] = momentum_3m_list
    df["1M Momentum"] = momentum_1m_list
    df["20D Momentum"] = momentum_20d_list

    df["MA50"] = ma50_list
    df["MA200"] = ma200_list
    df["MA50 Abstand"] = ma50_distance_list
    df["MA200 Abstand"] = ma200_distance_list
    df["Preis ueber MA50"] = price_above_ma50_list
    df["Preis ueber MA200"] = price_above_ma200_list

    df["Volume"] = volume_list
    df["Avg Volume"] = avg_volume_list
    df["Volume Ratio"] = volume_ratio_list

    df = df.dropna(
        subset=["Preis", "52W High", "52W Low"]
    ).copy()

    df["Trend Score"] = (
        (df["Preis"] - df["52W Low"])
        /
        (df["52W High"] - df["52W Low"])
    )

    df["Momentum"] = (
        (
            df["Preis"]
            -
            (
                (df["52W High"] + df["52W Low"]) / 2
            )
        )
        /
        (
            (df["52W High"] - df["52W Low"]) / 2
        )
    )

    df["Trend Score"] = df["Trend Score"].round(2)
    df["Momentum"] = df["Momentum"].round(2)

    df["3M Momentum"] = df["3M Momentum"].round(2)
    df["1M Momentum"] = df["1M Momentum"].round(2)
    df["20D Momentum"] = df["20D Momentum"].round(2)

    df["MA50"] = df["MA50"].round(2)
    df["MA200"] = df["MA200"].round(2)
    df["MA50 Abstand"] = df["MA50 Abstand"].round(2)
    df["MA200 Abstand"] = df["MA200 Abstand"].round(2)

    df["Volume"] = df["Volume"].round(0)
    df["Avg Volume"] = df["Avg Volume"].round(0)
    df["Volume Ratio"] = df["Volume Ratio"].round(2)

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    with open("last_update.txt", "w") as f:
        f.write(
            datetime.now().strftime("%Y-%m-%d %H:%M")
        )

    print("Fertig: theme_scores.csv erstellt")


if __name__ == "__main__":
    main()
