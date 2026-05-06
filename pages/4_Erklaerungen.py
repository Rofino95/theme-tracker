import streamlit as st

st.set_page_config(
    page_title="Erklaerungen",
    page_icon="assets/logo.png",
    layout="wide"
)

st.title("Erklaerungen & Transparenz")
st.caption("Wie der Theme Tracker Scores, Signale und Rankings berechnet.")

st.markdown("### Navigation")

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

st.info(
    """
Der Theme Tracker ist ein regelbasiertes Analyse-Tool.  
Er bewertet Aktien nicht nach Bauchgefühl, sondern nach klaren technischen und fundamentalen Regeln.

Wichtig: Das ist keine Finanzberatung und keine Kauf- oder Verkaufsempfehlung.
"""
)

st.markdown("## 1. Datenbasis")

st.write(
    """
Die App nutzt Daten aus `theme_universe.csv` und `theme_scores.csv`.

Für jede Aktie werden unter anderem gespeichert:

- Preis
- 52W High
- 52W Low
- Trend Score
- Range Momentum
- 3M Momentum
- Fundamentaldaten wie Forward PE, Revenue Growth, Earnings Growth und Profit Margin
"""
)

st.markdown("---")

st.markdown("## 2. Trend Score")

st.info(
    """
Der Trend Score zeigt, wo eine Aktie innerhalb ihrer 52-Wochen-Spanne steht.

Formel:

`Trend Score = (Preis - 52W Low) / (52W High - 52W Low)`

Interpretation:

- 0.00 = nahe am 52W Low
- 0.50 = Mitte der 52W-Spanne
- 1.00 = nahe am 52W High

Der Trend Score ist kein Momentum im eigentlichen Sinn. Er zeigt die Position innerhalb der Range.
"""
)

st.markdown("## 3. Range Momentum")

st.info(
    """
Range Momentum ist der alte Momentum-Wert der App.

Er zeigt, ob der aktuelle Preis über oder unter der Mitte der 52W-Spanne liegt.

Formel vereinfacht:

`Range Momentum = (Preis - Mitte der 52W-Spanne) / halbe 52W-Spanne`

Interpretation:

- positiv = Aktie steht über der Mitte ihrer 52W-Spanne
- negativ = Aktie steht unter der Mitte ihrer 52W-Spanne

Wichtig:
Range Momentum misst keine echte Kursentwicklung über Zeit.
"""
)

st.markdown("## 4. 3M Momentum")

st.info(
    """
3M Momentum ist das echte zeitliche Momentum.

Formel:

`3M Momentum = (aktueller Preis / Preis vor ca. 63 Handelstagen) - 1`

Interpretation:

- positiv = Aktie ist in den letzten ca. 3 Monaten gestiegen
- negativ = Aktie ist in den letzten ca. 3 Monaten gefallen

Warum wichtig:
Eine Aktie kann gut in ihrer 52W-Spanne stehen, aber trotzdem seit Monaten seitwärts laufen.  
3M Momentum zeigt, ob wirklich Bewegung im Kurs ist.
"""
)

st.markdown("---")

st.markdown("## 5. Status")

st.info(
    """
Der Status basiert auf dem Trend Score.

Regeln:

- Bullisch: Trend Score > 0.70
- Neutral: Trend Score > 0.50 bis 0.70
- Baerisch: Trend Score <= 0.50

Der Status wird vor allem für Main Themes und Sub Themes genutzt.
"""
)

st.markdown("## 6. Preis-Zonen")

st.info(
    """
Die Preis-Zonen basieren auf der 52W-Spanne.

Regeln:

- Weak Zone: unter 35% der 52W-Spanne
- Transition Zone: 35% bis 55%
- Watchlist Zone: 55% bis 70%
- Hold Zone: 70% bis 85%
- Upper Range: ab 85%

Interpretation:

- Weak Zone = schwach oder früh riskant
- Transition Zone = mögliche Bodenbildung / Übergang
- Watchlist Zone = interessanter Bereich für Beobachtung
- Hold Zone = gesunder Trendbereich
- Upper Range = weit gelaufen, Momentum prüfen
"""
)

st.markdown("---")

st.markdown("## 7. Trendrichtung")

st.info(
    """
Die Trendrichtung basiert auf gleitenden Durchschnitten aus dem 1-Jahres-Chart.

Genutzt werden:

- MA50 = Durchschnitt der letzten 50 Handelstage
- MA200 = Durchschnitt der letzten 200 Handelstage

Regeln:

- Aufwaertstrend: Preis > MA50 und MA50 > MA200, stabil bestätigt
- Frischer Aufwaertstrend: Preis > MA50 und MA50 > MA200, aber noch nicht lange bestätigt
- Abwaertstrend: Preis < MA50 und MA50 < MA200
- Turnaround moeglich: Preis > MA50, aber MA50 noch < MA200
- Trend schwaecht sich ab: Preis < MA50, aber MA50 noch > MA200
- Seitwaerts / unklar: kein klares Bild
"""
)

st.markdown("## 8. Trendphase")

st.info(
    """
Die Trendphase kombiniert Trend Score, Range Momentum und 3M Momentum.

Regeln:

- Weak: niedriger Trend Score und negatives 3M Momentum
- Late Trend: sehr hoher Trend Score, aber negatives 3M Momentum
- Mid Trend: hoher Trend Score, starkes Range Momentum und positives 3M Momentum
- Early Trend: mittlerer Trend Score, positives Range Momentum und positives 3M Momentum
- Transition: keine klare Zuordnung

Wichtig:
Trendphase beschreibt die Phase einer Bewegung, nicht automatisch ein Kauf- oder Verkaufssignal.
"""
)

st.markdown("---")

st.markdown("## 9. Signal")

st.info(
    """
Das Signal ist eine technische Einordnung.

Es nutzt:

- Trend Score
- Range Momentum
- 3M Momentum
- Theme Status
- Bullisch-Anteil im Sub Theme

Regeln vereinfacht:

Avoid:
- Trend Score schwach
- 3M Momentum negativ
- Theme baerisch

Take Profits:
- Trend Score sehr hoch
- 3M Momentum negativ

Attraktiv:
- Trend Score im gesunden Bereich
- Range Momentum positiv
- 3M Momentum positiv
- Theme bullisch oder neutral
- mindestens 50% der Aktien im Theme sind bullisch

Hold:
- Aktie ist stark und 3M Momentum bleibt positiv
- oder solides Setup ohne Schwächesignal

Review:
- keine eindeutige Einordnung
"""
)

st.markdown("---")

st.markdown("## 10. Fundamental Score")

st.info(
    """
Der Fundamental Score bewertet die Unternehmensqualität auf Basis fundamentaler Kennzahlen.

Maximalwert: 10 Punkte

Bewertete Faktoren:

Revenue Growth:
- > 20% = 2 Punkte
- > 5% = 1 Punkt

Earnings Growth:
- > 20% = 2 Punkte
- > 5% = 1 Punkt

Forward PE:
- 0 bis 20 = 2 Punkte
- 20 bis 35 = 1 Punkt

Profit Margin:
- > 20% = 2 Punkte
- > 10% = 1 Punkt

Bonus:
- Revenue Growth > 15%
- Earnings Growth > 15%
- Profit Margin > 15%
→ zusätzlich 2 Punkte
"""
)

st.markdown("## 11. Fundamental Quality")

st.info(
    """
Fundamental Quality ist die vereinfachte Kategorie aus dem Fundamental Score.

Regeln:

- Hoch: Score >= 8
- Mittel: Score >= 5
- Niedrig: Score < 5

Der Score ist zum Sortieren gedacht.  
Die Quality ist für schnelle Interpretation gedacht.
"""
)

st.markdown("---")

st.markdown("## 12. Entry Score")

st.info(
    """
Der Entry Score ist einer der wichtigsten Scores der App.

Er bewertet, ob der aktuelle Einstieg technisch und fundamental interessant wirkt.

Maximalwert: 10 Punkte

Einbezogene Faktoren:

1. Preiszone:
- Watchlist Zone = +3
- Transition Zone = +2
- Hold Zone = +1
- Upper Range = 0
- Weak Zone = 0

2. Trendrichtung:
- Frischer Aufwaertstrend / Turnaround moeglich = +2
- Aufwaertstrend = +1
- Abwaertstrend / Trend schwaecht sich ab = -1

3. Range Momentum:
- positiv = +1
- stark negativ = -1

4. 3M Momentum:
- > 10% = +2
- > 0% = +1
- < -10% = -2
- < 0% = -1

5. Fundamentals:
- Fundamental Quality Hoch = +2
- Fundamental Quality Mittel = +1

6. Bewertung:
- Forward PE unter 20 = +1
- Forward PE über 60 = -1

7. Growth:
- Umsatz- oder Gewinnwachstum über 5% = +1

Der Entry Score wird auf 0 bis 10 begrenzt.
"""
)

st.markdown("## 13. Entry Quality")

st.info(
    """
Entry Quality ist die Kategorie aus dem Entry Score.

Regeln:

- Sehr gut: Entry Score >= 8
- Gut: Entry Score >= 6
- Neutral: Entry Score >= 4
- Riskant: Entry Score < 4

Wichtig:
Ein hoher Entry Score bedeutet nicht automatisch Gewinn.  
Er bedeutet nur, dass mehrere Faktoren gleichzeitig positiv sind.
"""
)

st.markdown("---")

st.markdown("## 14. Risiko")

st.info(
    """
Das Risiko basiert auf Zone und Trendrichtung.

Regeln:

- Sehr hoch: Weak Zone
- Hoch: Turnaround moeglich oder frischer Aufwaertstrend
- Mittel: Upper Range
- Niedrig: stabile Lage ohne klare Risikowarnung

Wichtig:
Ein frischer Aufwärtstrend kann attraktiv sein, ist aber oft noch nicht bestätigt. Deshalb wird er als höheres Risiko gewertet.
"""
)

st.markdown("## 15. Exit Signal")

st.info(
    """
Das Exit Signal zeigt, ob eher Halten, Vorsicht oder Gewinnsicherung naheliegt.

Regeln:

- Gewinne sichern: Upper Range und Range Momentum schwächt sich ab
- Vorsicht: Trend schwaecht sich ab
- Hold: kein klares Ausstiegssignal

Das ist keine Verkaufsaufforderung, sondern ein Warnhinweis.
"""
)

st.markdown("---")

st.markdown("## 16. Master Score")

st.info(
    """
Der Master Score kombiniert Entry Score, Fundamental Score und Risiko.

Formel vereinfacht:

`Master Score = Entry Score * 0.5 + Fundamental Score * 0.3 + Risiko-Anpassung`

Risiko-Anpassung:

- Niedrig = +1
- Mittel = 0
- Hoch = -1
- Sehr hoch = -2

Interpretation:
Der Master Score ist die verdichtete Gesamtbewertung einer Aktie.
"""
)

st.markdown("## 17. Master Signal")

st.info(
    """
Das Master Signal ist die einfache Handlungseinordnung.

Regeln:

- 🟢 Einstieg sinnvoll: Master Score >= 7
- 🟡 Beobachten: Master Score >= 5
- 🔴 Kein Einstieg: Master Score < 5

Wichtig:
Das Master Signal soll Orientierung geben, ersetzt aber keine eigene Analyse.
"""
)

st.markdown("---")

st.markdown("## 18. Short Term Ranking")

st.info(
    """
Short Term bedeutet in dieser App:

ca. 2 Wochen bis 3 Monate

Das Short-Term-Ranking gewichtet stärker:

- Entry Score
- 3M Momentum
- Risiko
- Fundamental Quality als Bonus

Ziel:
Aktien finden, die kurzfristig bis mittelfristig ein interessantes technisches Setup zeigen.
"""
)

st.markdown("## 19. Long Term Ranking")

st.info(
    """
Long Term bedeutet in dieser App:

ca. 6 Monate bis mehrere Jahre

Das Long-Term-Ranking gewichtet stärker:

- Fundamental Score
- Trend Score
- Entry Score als Zusatz
- Risiko
- 3M Momentum nur leicht

Ziel:
Aktien finden, die langfristig qualitativ interessant wirken und technisch nicht komplett schwach sind.
"""
)

st.markdown("---")

st.markdown("## 20. Early Plays")

st.info(
    """
Early Plays sind ein zusätzlicher Screening-Bereich der App.

Ziel:
Aktien identifizieren, die sich noch früh in einer möglichen Aufwärtsbewegung befinden.

Wichtig:
Early Plays sind keine fertigen Trends, sondern potenzielle Anfangsphasen.

Filterbedingungen:

- Trend Score unter 0.65  
→ Aktie ist noch nicht weit in der 52W-Spanne gelaufen

- Positives 3M Momentum  
→ erste Aufwärtsbewegung vorhanden

- Trendrichtung:
  - Frischer Aufwaertstrend oder
  - Turnaround moeglich

Interpretation:

- Early Plays sind oft volatiler
- Signale können häufiger fehlschlagen
- bieten aber potenziell höhere Upside

Der Bereich ist bewusst strenger gefiltert als das normale Ranking.
"""
)

st.markdown("## 21. Early Score")

st.info(
    """
Der Early Score bewertet die Qualität eines möglichen frühen Trends.

Er kombiniert mehrere Faktoren:

1. Fundamentaldaten:
- Fundamental Score wird stärker gewichtet als im Short Term Bereich

2. Position in der Range:
- niedriger Trend Score wird belohnt (früh im Move)

3. 3M Momentum:
- leicht positives Momentum ist ideal
- zu starkes Momentum wird teilweise negativ bewertet (zu spät)

4. Trendrichtung:
- Frischer Aufwaertstrend wird stark belohnt
- Turnaround moeglich leicht positiv
- schwache Trends werden abgewertet

5. Range Momentum:
- bestätigt interne Stärke

6. Risiko:
- sehr hohes Risiko wird bestraft

Wichtig:

Der Early Score ist bewusst aggressiver als andere Scores.  
Er soll Unterschiede zwischen wenigen starken Kandidaten klar sichtbar machen.
"""
)

st.markdown("## 22. Smart Money (Volume)")

st.info(
    """
Smart Money ist ein zusätzlicher Faktor im Early Score.

Er basiert auf Handelsvolumen.

Verglichen wird:

aktuelles Volumen vs. durchschnittliches Volumen (30 Tage)

Regeln:

- Volumen > 2x Durchschnitt → sehr starkes Signal
- Volumen > 1.5x Durchschnitt → starkes Signal
- Volumen > 1.2x Durchschnitt → leicht positiv

Interpretation:

- steigendes Volumen kann auf institutionelle Käufe hinweisen
- bestätigt häufig den Beginn eines Trends

Wichtig:

Volumen allein ist kein Kaufsignal.  
Es verstärkt nur bestehende technische Signale.
"""
)

st.markdown("## 23. High Conviction")

st.info(
    """
High Conviction ist eine zusätzliche Kennzeichnung für besonders starke Early Plays.

Bedingungen:

- hoher Early Score (>= 8)
- Fundamental Quality = Hoch
- positives 3M Momentum

Interpretation:

- mehrere starke Faktoren treffen gleichzeitig zusammen
- höhere Wahrscheinlichkeit für ein sauberes Setup

Wichtig:

High Conviction bedeutet nicht garantiert Erfolg.  
Es zeigt nur, dass viele Kriterien gleichzeitig erfüllt sind.
"""
)

st.markdown("## 24. Unterschiede der Rankings")

st.info(
    """
Die App unterscheidet drei Perspektiven:

Short Term:
- Fokus auf Momentum und Entry Timing
- Zeitraum: Wochen bis wenige Monate

Long Term:
- Fokus auf Fundamentaldaten und Stabilität
- Zeitraum: Monate bis Jahre

Early Plays:
- Fokus auf frühe Trends und mögliche Breakouts
- Kombination aus Technik, Momentum und Volumen

Wichtig:

Eine Aktie kann:

- im Long Term gut sein, aber kein Early Play
- im Early Bereich interessant sein, aber fundamental schwach
- im Short Term stark sein, aber schon weit gelaufen

Deshalb sollten die Rankings immer im Kontext betrachtet werden.
"""
)

st.markdown("---")

st.markdown("## 25. Grenzen des Modells")

st.warning(
    """
Das Modell hat klare Grenzen:

- Es garantiert keine Gewinne.
- Es kann Fake Breakouts nicht sicher verhindern.
- Es berücksichtigt keine Nachrichtenlage.
- Es bewertet Managementqualität nur indirekt.
- Fundamentaldaten können fehlen oder veraltet sein.
- Yahoo-Finance-Daten können unvollständig sein.
- Ein gutes Signal bedeutet nicht, dass die Aktie nicht trotzdem fällt.
- Ein schlechtes Signal bedeutet nicht, dass die Aktie nicht steigen kann.

Das Tool ist ein Screening- und Strukturierungstool, keine Finanzberatung.
"""
)

st.markdown("## 26. Warum Transparenz wichtig ist")

st.success(
    """
Alle Scores sind regelbasiert.  
Es gibt keine bezahlten Platzierungen, keine manuelle Bevorzugung einzelner Aktien und keine versteckten Gewichtungen.

Wenn eine Aktie gut rankt, dann weil sie nach den definierten Regeln gut abschneidet.
"""
)
