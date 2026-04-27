import streamlit as st

st.set_page_config(page_title="Erklaerungen", layout="wide")

st.title("Erklaerungen & Transparenz")

st.info(
    """
Diese Seite erklaert, wie die Scores, Zonen und Signale im Theme Tracker berechnet werden.

Wichtig:
Das Tool ist keine Finanzberatung. Es nutzt regelbasierte technische und fundamentale Kennzahlen, um Aktien besser vergleichbar zu machen.
"""
)

st.markdown("## 1. Trend Score")

st.info(
    """
Der Trend Score zeigt, wo der aktuelle Kurs innerhalb seiner 52-Wochen-Spanne liegt.

Formel:

Trend Score = (Preis - 52W Low) / (52W High - 52W Low)

Interpretation:
- 0.00 = nahe 52W Low
- 0.50 = Mitte der 52W-Spanne
- 1.00 = nahe 52W High

Beispiel:
Ein Trend Score von 0.80 bedeutet, dass die Aktie relativ weit oben in ihrer 52-Wochen-Spanne steht.
"""
)

st.markdown("## 2. Momentum")

st.info(
    """
Momentum zeigt, ob der aktuelle Preis eher oberhalb oder unterhalb der Mitte der 52-Wochen-Spanne liegt.

Vereinfacht:
- positives Momentum = Aktie steht ueber der Mitte ihrer 52W-Spanne
- negatives Momentum = Aktie steht unter der Mitte ihrer 52W-Spanne

Interpretation:
- ab 0.50 = stark positiv
- 0.00 bis 0.49 = leicht positiv
- -0.49 bis -0.01 = schwach
- ab -0.50 = stark negativ
"""
)

st.markdown("## 3. Status")

st.info(
    """
Der Status basiert auf dem Trend Score.

Regeln:
- Bullisch: Trend Score ueber 0.70
- Neutral: Trend Score ueber 0.50 bis 0.70
- Baerisch: Trend Score 0.50 oder niedriger

Der Status wird vor allem fuer Main Themes und Sub Themes genutzt.
"""
)

st.markdown("## 4. Preis-Zonen")

st.info(
    """
Die Preis-Zonen werden aus der 52-Wochen-Spanne berechnet.

Zonen:
- Weak Zone: unter 35% der 52W-Spanne
- Transition Zone: 35% bis 55%
- Watchlist Zone: 55% bis 70%
- Hold Zone: 70% bis 85%
- Upper Range: ab 85%

Wichtig:
Upper Range bedeutet nicht automatisch verkaufen. Es bedeutet nur, dass die Aktie bereits weit oben in ihrer 52W-Spanne steht.
"""
)

st.markdown("## 5. Signal")

st.info(
    """
Das Signal kombiniert Aktie, Momentum und Theme-Kontext.

Regeln:
- Avoid: sehr schwacher Trend Score, negatives Momentum und baerisches Theme
- Take Profits: hoher Trend Score, aber Momentum flacht ab
- Attraktiv: gesunder Trend Score, positives Momentum, Theme nicht baerisch und ausreichend viele bullische Aktien im Theme
- Hold: starker Trend oder solide Lage ohne klares Schwaechesignal
- Review: alles, was nicht eindeutig in die anderen Kategorien faellt

Das Signal ist keine Kauf- oder Verkaufsempfehlung.
"""
)

st.markdown("## 6. Trendphase")

st.info(
    """
Die Trendphase beschreibt, wo sich eine Aktie innerhalb ihres Bewegungszyklus befindet.

Regeln:
- Early Trend: fruehe positive Bewegung
- Mid Trend: etablierter Aufwaertstrend
- Late Trend: weit gelaufen, Momentum flacht ab
- Transition: uneindeutige Lage
- Weak: schwacher Trend mit negativem Momentum

Trendphase beschreibt nicht automatisch die Richtung des Charts. Dafuer gibt es die Trendrichtung.
"""
)

st.markdown("## 7. Trendrichtung")

st.info(
    """
Die Trendrichtung basiert auf gleitenden Durchschnitten.

Genutzt werden:
- MA50: Durchschnitt der letzten 50 Handelstage
- MA200: Durchschnitt der letzten 200 Handelstage

Regeln:
- Aufwaertstrend: Preis ueber MA50, MA50 ueber MA200 und Trend bereits laenger bestaetigt
- Frischer Aufwaertstrend: Preis ueber MA50 und MA50 ueber MA200, aber noch nicht lange genug bestaetigt
- Abwaertstrend: Preis unter MA50 und MA50 unter MA200
- Turnaround moeglich: Preis ueber MA50, aber MA50 noch unter MA200
- Trend schwaecht sich ab: Preis unter MA50, aber MA50 noch ueber MA200
- Seitwaerts / unklar: keine klare Richtung

Diese Logik hilft dabei, Bounce-Bewegungen von stabileren Trends zu unterscheiden.
"""
)

st.markdown("## 8. Entry Quality")

st.info(
    """
Entry Quality bewertet, ob der aktuelle Zeitpunkt fuer einen Einstieg technisch interessant wirkt.

Regeln:
- Sehr gut: Watchlist oder Transition Zone, positives Momentum und Turnaround/frischer Aufwaertstrend
- Gut: Hold Zone und positives Momentum
- Zu spaet: Upper Range
- Riskant: Weak Zone
- Neutral: keine klare Einstiegsqualitaet

Je strenger die Kriterien, desto seltener erscheinen sehr gute Setups.
"""
)

st.markdown("## 9. Exit Signal")

st.info(
    """
Das Exit Signal bewertet, ob eher Halten, Vorsicht oder Gewinnsicherung naheliegt.

Regeln:
- Gewinne sichern: Upper Range und Momentum flacht ab
- Vorsicht: Trend schwaecht sich ab
- Hold: kein klares Ausstiegssignal

Auch hier gilt:
Das ist keine Verkaufsaufforderung, sondern ein Risikohinweis.
"""
)

st.markdown("## 10. Risiko")

st.info(
    """
Das Risiko basiert auf Preiszone und Trendrichtung.

Regeln:
- Sehr hoch: Weak Zone
- Hoch: Turnaround moeglich oder frischer Aufwaertstrend
- Mittel: Upper Range
- Niedrig: stabile Lage ohne klare Risikowarnung

Ein hoher Score kann trotzdem hohes Risiko haben, wenn die Aktie gerade erst dreht.
"""
)

st.markdown("## 11. Fundamental Score")

st.info(
    """
Der Fundamental Score bewertet die Qualitaet des Unternehmens anhand fundamentaler Kennzahlen.

Genutzt werden:
- Revenue Growth
- Earnings Growth
- Forward PE
- Profit Margin

Punkte:
- starkes Umsatzwachstum: bis zu 2 Punkte
- starkes Gewinnwachstum: bis zu 2 Punkte
- akzeptables Forward PE: bis zu 2 Punkte
- hohe Profit Margin: bis zu 2 Punkte
- Bonus fuer Kombination aus Wachstum und Profitabilitaet: bis zu 2 Punkte

Maximalwert: 10 Punkte
"""
)

st.markdown("## 12. Fundamental Quality")

st.info(
    """
Fundamental Quality ist die vereinfachte Kategorie des Fundamental Scores.

Regeln:
- Hoch: Score 8 bis 10
- Mittel: Score 5 bis 7
- Niedrig: Score 0 bis 4

Der Score ist zum Sortieren gedacht.
Die Quality ist fuer schnelle Interpretation gedacht.
"""
)

st.markdown("## 13. Opportunity Score")

st.info(
    """
Der Opportunity Score kombiniert technische Einstiegslage, Fundamentaldaten und Risiko.

Grundidee:
- gute Entry Quality gibt Pluspunkte
- hohe Fundamental Quality gibt Pluspunkte
- niedriges Risiko gibt Pluspunkte
- positives Momentum gibt Pluspunkte

Ziel:
Nicht die perfekte Aktie vorherzusagen, sondern die besten Kandidaten aus dem aktuellen Universum hervorzuheben.
"""
)

st.markdown("## 14. Short Term vs. Long Term")

st.info(
    """
Short Term:
- Zeitraum: ca. 2 Wochen bis 3 Monate
- Fokus: Momentum, Entry Quality, Zone, Trendrichtung

Long Term:
- Zeitraum: ca. 6 Monate bis mehrere Jahre
- Fokus: Fundamentaldaten, strukturelle Themes, stabile Trends

Eine Aktie kann kurzfristig interessant sein, aber langfristig schwach.
Umgekehrt kann ein starkes Unternehmen langfristig interessant sein, aber kurzfristig kein guter Einstieg sein.
"""
)

st.markdown("## 15. Grenzen des Modells")

st.warning(
    """
Das Modell hat klare Grenzen:

- Es garantiert keine Gewinne.
- Es kann Fake Breakouts nicht sicher verhindern.
- Fundamentaldaten von Yahoo Finance koennen fehlen oder veraltet sein.
- Das Modell beruecksichtigt keine Nachrichten, Bilanzdetails, Managementqualitaet oder politische Risiken.
- Ein gutes Signal bedeutet nicht, dass die Aktie nicht trotzdem fallen kann.

Das Tool soll helfen, Aktien strukturierter zu vergleichen, ersetzt aber keine eigene Analyse.
"""
)
