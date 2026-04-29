import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Theme Tracker", layout="wide")

if not os.path.exists("theme_scores.csv"):
    st.warning("Noch keine Daten vorhanden – bitte warten oder update ausfuehren.")
    st.stop()

df = pd.read_csv("theme_scores.csv")

if "3M Momentum" not in df.columns:
    st.error("Die Spalte '3M Momentum' fehlt noch. Bitte zuerst update_data.py ausfuehren.")
    st.stop()


def get_status(score):
    if score > 0.7:
        return "Bullisch"
    elif score > 0.5:
        return "Neutral"
    else:
        return "Baerisch"


def get_signal(stock_score, range_momentum, momentum_3m, theme_status, theme_bullish_pct):
    if stock_score < 0.35 and momentum_3m < 0 and theme_status == "Baerisch":
        return "Avoid"
    if stock_score > 0.85 and momentum_3m < 0:
        return "Take Profits"
    if (
        0.55 <= stock_score <= 0.85
        and range_momentum > 0
        and momentum_3m > 0
        and theme_status in ["Bullisch", "Neutral"]
        and theme_bullish_pct >= 50
    ):
        return "Attraktiv"
    if stock_score > 0.85 and momentum_3m > 0:
        return "Hold"
    if stock_score >= 0.50 and range_momentum >= -0.10 and momentum_3m >= 0 and theme_status != "Baerisch":
        return "Hold"
    return "Review"


def get_trend_phase(stock_score, range_momentum, momentum_3m):
    if stock_score < 0.35 and momentum_3m < 0:
        return "Weak"
    elif stock_score > 0.85 and momentum_3m < 0:
        return "Late Trend"
    elif stock_score > 0.75 and range_momentum >= 0.30 and momentum_3m > 0:
        return "Mid Trend"
    elif 0.55 <= stock_score <= 0.75 and range_momentum > 0 and momentum_3m > 0:
        return "Early Trend"
    else:
        return "Transition"


def color_status(val):
    if val == "Bullisch":
        return "background-color: #123524; color: white"
    elif val == "Neutral":
        return "background-color: #5c4b00; color: white"
    else:
        return "background-color: #5a1e1e; color: white"


def color_signal(val):
    if val == "Attraktiv":
        return "background-color: #123524; color: white"
    elif val == "Hold":
        return "background-color: #1f3c88; color: white"
    elif val == "Review":
        return "background-color: #5c4b00; color: white"
    elif val == "Take Profits":
        return "background-color: #6a3d00; color: white"
    elif val == "Avoid":
        return "background-color: #5a1e1e; color: white"
    return ""


def color_trend_phase(val):
    if val == "Early Trend":
        return "background-color: #123524; color: white"
    elif val == "Mid Trend":
        return "background-color: #1f3c88; color: white"
    elif val == "Late Trend":
        return "background-color: #6a3d00; color: white"
    elif val == "Transition":
        return "background-color: #5c4b00; color: white"
    elif val == "Weak":
        return "background-color: #5a1e1e; color: white"
    return ""


df["Status"] = df["Trend Score"].apply(get_status)

st.title("Theme Tracker")
st.caption("Regelbasierter Markt- und Aktien-Screener nach Themes, Trend Score, Range Momentum, 3M Momentum und Fundamentaldaten.")

nav1, nav2, nav3, nav4, nav5 = st.columns(5)

with nav1:
    st.page_link("app.py", label="Startseite", icon="🏠")
with nav2:
    st.page_link("pages/1_Aktien_Detail.py", label="Aktien-Detail", icon="📈")
with nav3:
    st.page_link("pages/2_Aktien_Ranking.py", label="Ranking", icon="🔎")
with nav4:
    st.page_link("pages/3_Top_Opportunities.py", label="Top Opportunities", icon="🔥")
with nav5:
    st.page_link("pages/4_Erklaerungen.py", label="Erklaerungen", icon="ℹ️")

st.markdown("---")

# Gruppierungen
grouped = (
    df.groupby("Sub Theme", as_index=False)
    .agg({
        "Trend Score": "mean",
        "Momentum": "mean",
        "3M Momentum": "mean",
        "Ticker": "count"
    })
    .rename(columns={"Ticker": "Anzahl Aktien"})
)

grouped["Trend Score"] = grouped["Trend Score"].round(2)
grouped["Momentum"] = grouped["Momentum"].round(2)
grouped["3M Momentum"] = grouped["3M Momentum"].round(2)
grouped["Status"] = grouped["Trend Score"].apply(get_status)
grouped = grouped.sort_values(by="Trend Score", ascending=False)

main_grouped = (
    df.groupby("Main Theme", as_index=False)
    .agg({
        "Trend Score": "mean",
        "Momentum": "mean",
        "3M Momentum": "mean"
    })
)

main_grouped["Trend Score"] = main_grouped["Trend Score"].round(2)
main_grouped["Momentum"] = main_grouped["Momentum"].round(2)
main_grouped["3M Momentum"] = main_grouped["3M Momentum"].round(2)
main_grouped["Status"] = main_grouped["Trend Score"].apply(get_status)
main_grouped = main_grouped.sort_values(by="Trend Score", ascending=False)

top_theme = grouped.iloc[0]["Sub Theme"]
top_score = grouped.iloc[0]["Trend Score"]
top_3m = grouped.iloc[0]["3M Momentum"]

flop_theme = grouped.iloc[-1]["Sub Theme"]
flop_score = grouped.iloc[-1]["Trend Score"]
flop_3m = grouped.iloc[-1]["3M Momentum"]

st.subheader("Marktueberblick")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.caption("Top Theme")
    st.markdown(f"### {top_theme}")
    st.caption(f"Trend Score: {top_score:.2f}")

with kpi2:
    st.caption("3M Momentum Top Theme")
    st.markdown(f"### {top_3m * 100:.1f}%")

with kpi3:
    st.caption("Schwaechstes Theme")
    st.markdown(f"### {flop_theme}")
    st.caption(f"Trend Score: {flop_score:.2f}")

with kpi4:
    st.caption("3M Momentum schwach")
    st.markdown(f"### {flop_3m * 100:.1f}%")

st.caption("Range Momentum = Position in der 52W-Spanne | 3M Momentum = echte Kursveraenderung der letzten ca. 3 Monate")

st.markdown("---")

# Filter
filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    filter_status = st.selectbox(
        "Status filtern",
        ["Alle", "Bullisch", "Neutral", "Baerisch"]
    )

with filter_col2:
    filter_main_theme = st.selectbox(
        "Main Theme filtern",
        ["Alle"] + sorted(df["Main Theme"].dropna().unique().tolist())
    )

filtered_df = df.copy()

if filter_main_theme != "Alle":
    filtered_df = filtered_df[filtered_df["Main Theme"] == filter_main_theme]

filtered_grouped = (
    filtered_df.groupby("Sub Theme", as_index=False)
    .agg({
        "Trend Score": "mean",
        "Momentum": "mean",
        "3M Momentum": "mean",
        "Ticker": "count"
    })
    .rename(columns={"Ticker": "Anzahl Aktien"})
)

filtered_grouped["Trend Score"] = filtered_grouped["Trend Score"].round(2)
filtered_grouped["Momentum"] = filtered_grouped["Momentum"].round(2)
filtered_grouped["3M Momentum"] = filtered_grouped["3M Momentum"].round(2)
filtered_grouped["Status"] = filtered_grouped["Trend Score"].apply(get_status)

bullish_pct = (
    filtered_df.assign(IsBullish=filtered_df["Status"] == "Bullisch")
    .groupby("Sub Theme")["IsBullish"]
    .mean()
    .mul(100)
    .round(0)
    .reset_index(name="Bullisch %")
)

neutral_pct = (
    filtered_df.assign(IsNeutral=filtered_df["Status"] == "Neutral")
    .groupby("Sub Theme")["IsNeutral"]
    .mean()
    .mul(100)
    .round(0)
    .reset_index(name="Neutral %")
)

bearish_pct = (
    filtered_df.assign(IsBearish=filtered_df["Status"] == "Baerisch")
    .groupby("Sub Theme")["IsBearish"]
    .mean()
    .mul(100)
    .round(0)
    .reset_index(name="Baerisch %")
)

filtered_grouped = filtered_grouped.merge(bullish_pct, on="Sub Theme", how="left")
filtered_grouped = filtered_grouped.merge(neutral_pct, on="Sub Theme", how="left")
filtered_grouped = filtered_grouped.merge(bearish_pct, on="Sub Theme", how="left")

filtered_grouped = filtered_grouped.sort_values(by="Trend Score", ascending=False)

if filter_status != "Alle":
    filtered_grouped = filtered_grouped[filtered_grouped["Status"] == filter_status]

show_details = st.toggle("Mehr Details anzeigen", value=False)

st.markdown("### Main Theme Uebersicht")

main_display = main_grouped.rename(columns={"Momentum": "Range Momentum"})

if show_details:
    main_columns = ["Main Theme", "Trend Score", "Range Momentum", "3M Momentum", "Status"]
else:
    main_columns = ["Main Theme", "Trend Score", "3M Momentum", "Status"]

st.dataframe(
    main_display[main_columns]
    .style
    .map(color_status, subset=["Status"])
    .format({
        "Trend Score": "{:.2f}",
        "Range Momentum": "{:.2f}",
        "3M Momentum": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("### Sub Theme Uebersicht")

sub_display = filtered_grouped.rename(columns={"Momentum": "Range Momentum"})

if show_details:
    sub_columns = [
        "Sub Theme",
        "Trend Score",
        "Range Momentum",
        "3M Momentum",
        "Anzahl Aktien",
        "Status",
        "Bullisch %",
        "Neutral %",
        "Baerisch %"
    ]
else:
    sub_columns = [
        "Sub Theme",
        "Trend Score",
        "3M Momentum",
        "Anzahl Aktien",
        "Status"
    ]

height = min(900, 50 + len(sub_display) * 35)

st.dataframe(
    sub_display[sub_columns]
    .style
    .map(color_status, subset=["Status"])
    .format({
        "Trend Score": "{:.2f}",
        "Range Momentum": "{:.2f}",
        "3M Momentum": "{:.2f}",
        "Bullisch %": "{:.0f}%",
        "Neutral %": "{:.0f}%",
        "Baerisch %": "{:.0f}%"
    }),
    use_container_width=True,
    hide_index=True,
    height=height
)

st.markdown("---")

# Suche
st.subheader("Aktiensuche")

search_term = st.text_input("Suche nach Aktienname oder Ticker", key="global_search")

if search_term:
    result_df = df[
        df["Name"].str.contains(search_term, case=False, na=False) |
        df["Ticker"].str.contains(search_term, case=False, na=False)
    ].copy()

    if len(result_df) > 0:
        grouped_search = (
            result_df.groupby(["Name", "Ticker"], as_index=False)
            .agg({
                "Preis": "first",
                "Trend Score": "mean",
                "Momentum": "mean",
                "3M Momentum": "mean",
                "Status": "first"
            })
        )

        theme_map = (
            result_df.groupby(["Name", "Ticker"])["Sub Theme"]
            .apply(lambda x: ", ".join(sorted(set(x))))
            .reset_index(name="Sub Themes")
        )

        main_theme_map = (
            result_df.groupby(["Name", "Ticker"])["Main Theme"]
            .apply(lambda x: ", ".join(sorted(set(x))))
            .reset_index(name="Main Themes")
        )

        grouped_search = grouped_search.merge(theme_map, on=["Name", "Ticker"], how="left")
        grouped_search = grouped_search.merge(main_theme_map, on=["Name", "Ticker"], how="left")

        grouped_search["Signal"] = grouped_search.apply(
            lambda row: get_signal(
                row["Trend Score"],
                row["Momentum"],
                row["3M Momentum"],
                row["Status"],
                50
            ),
            axis=1
        )

        search_display = grouped_search.rename(columns={"Momentum": "Range Momentum"})

        st.dataframe(
            search_display[[
                "Name",
                "Ticker",
                "Preis",
                "Trend Score",
                "3M Momentum",
                "Status",
                "Signal"
            ]]
            .style
            .map(color_status, subset=["Status"])
            .map(color_signal, subset=["Signal"])
            .format({
                "Preis": "{:.2f}",
                "Trend Score": "{:.2f}",
                "3M Momentum": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True,
            height=min(600, 50 + len(search_display) * 35)
        )
    else:
        st.warning("Keine passende Aktie gefunden.")

st.markdown("---")

# Detailbereich einklappbar
with st.expander("Sub Theme im Detail anzeigen", expanded=False):
    if filtered_grouped.empty:
        st.warning("Keine Sub Themes fuer diese Filterkombination gefunden.")
        st.stop()

    selected_theme = st.selectbox(
        "Waehle ein Sub Theme",
        filtered_grouped["Sub Theme"].tolist()
    )

    detail_df = filtered_df[filtered_df["Sub Theme"] == selected_theme].copy()
    detail_df = detail_df.sort_values(by="Trend Score", ascending=False)

    theme_status_detail = filtered_grouped[
        filtered_grouped["Sub Theme"] == selected_theme
    ]["Status"].iloc[0]

    theme_bullish_pct_detail = filtered_grouped[
        filtered_grouped["Sub Theme"] == selected_theme
    ]["Bullisch %"].iloc[0]

    detail_df["Signal"] = detail_df.apply(
        lambda row: get_signal(
            row["Trend Score"],
            row["Momentum"],
            row["3M Momentum"],
            theme_status_detail,
            theme_bullish_pct_detail
        ),
        axis=1
    )

    detail_df["Trendphase"] = detail_df.apply(
        lambda row: get_trend_phase(
            row["Trend Score"],
            row["Momentum"],
            row["3M Momentum"]
        ),
        axis=1
    )

    selected_main_theme = filtered_df[
        filtered_df["Sub Theme"] == selected_theme
    ]["Main Theme"].iloc[0]

    st.write(f"**Main Theme:** {selected_main_theme}")

    best_stock = detail_df.iloc[0]["Name"]
    best_score = detail_df.iloc[0]["Trend Score"]
    weakest_stock = detail_df.iloc[-1]["Name"]
    weakest_score = detail_df.iloc[-1]["Trend Score"]
    stock_count = len(detail_df)
    bullish_pct_detail = round((detail_df["Status"] == "Bullisch").mean() * 100, 0)

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Staerkste Aktie", best_stock, f"{best_score:.2f}")
    col_b.metric("Relativ schwaechste Aktie", weakest_stock, f"{weakest_score:.2f}")
    col_c.metric("Anzahl Aktien", stock_count)
    col_d.metric("Bullisch %", f"{bullish_pct_detail:.0f}%")

    search_term_detail = st.text_input(
        "Suche innerhalb dieses Sub Themes nach Name oder Ticker",
        key="detail_search"
    )

    detail_filtered_df = detail_df.copy()

    if search_term_detail:
        detail_filtered_df = detail_filtered_df[
            detail_filtered_df["Name"].str.contains(search_term_detail, case=False, na=False) |
            detail_filtered_df["Ticker"].str.contains(search_term_detail, case=False, na=False)
        ].copy()

    display_detail = detail_filtered_df.rename(columns={"Momentum": "Range Momentum"})

    st.dataframe(
        display_detail[[
            "Name",
            "Ticker",
            "Preis",
            "Trend Score",
            "Range Momentum",
            "3M Momentum",
            "Trendphase",
            "Signal"
        ]]
        .style
        .map(color_trend_phase, subset=["Trendphase"])
        .map(color_signal, subset=["Signal"])
        .format({
            "Preis": "{:.2f}",
            "Trend Score": "{:.2f}",
            "Range Momentum": "{:.2f}",
            "3M Momentum": "{:.2f}"
        }),
        use_container_width=True,
        hide_index=True,
        height=min(700, 50 + len(display_detail) * 35)
    )

    st.markdown("### Aktie direkt oeffnen")

    if len(detail_filtered_df) > 0:
        jump_options = detail_filtered_df[["Name", "Ticker"]].drop_duplicates().copy()
        jump_options["Label"] = jump_options["Name"] + " (" + jump_options["Ticker"] + ")"

        selected_jump_label = st.selectbox(
            "Waehle eine Aktie fuer die Detailseite",
            jump_options["Label"].tolist(),
            key="jump_to_stock_detail"
        )

        selected_jump_ticker = jump_options.loc[
            jump_options["Label"] == selected_jump_label, "Ticker"
        ].iloc[0]

        st.page_link(
            "pages/1_Aktien_Detail.py",
            label=f"Zur Detailseite von {selected_jump_label}",
            icon="📈",
            query_params={"ticker": selected_jump_ticker}
        )

with st.expander("Legende anzeigen", expanded=False):
    st.write(
        """
**Status**

- Bullisch: Trend Score ueber 0.70
- Neutral: Trend Score ueber 0.50 bis 0.70
- Baerisch: Trend Score 0.50 oder niedriger

**Range Momentum**

Zeigt die Position relativ zur Mitte der 52W-Spanne. Es ist kein echtes Zeit-Momentum.

**3M Momentum**

Zeigt die echte Kursveraenderung der letzten ca. 3 Monate.
"""
    )
    
