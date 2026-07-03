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
Der Theme Tracker ist ein regelbasiertes Screening-Tool.

Er ist **kein automatisches Kaufsignal-System**, sondern soll helfen, Aktien schneller zu sortieren,
Chancen sichtbarer zu machen und offensichtliche Risikofallen besser zu erkennen.

Wichtig: Das ist keine Finanzberatung und keine Kauf- oder Verkaufsempfehlung.
"""
)

st.markdown("---")

st.markdown("## 1. Grundidee des Trackers")

st.write(
    """
Der Tracker bewertet Aktien nach mehreren Bausteinen:

- Position innerhalb der 52-Wochen-Spanne
- echtes Kursmomentum über verschiedene Zeiträume
- Abstand zu wichtigen gleitenden Durchschnitten
- Handelsvolumen
- fundamentale Qualität
- Risiko- und Timing-Faktoren

Das Ziel ist nicht, jede Aktie perfekt vorherzusagen.  
Das Ziel ist, bessere Kandidaten von problematischen Kandidaten zu trennen.
"""
)

st.markdown("---")

st.markdown("## 2. Datenbasis")

st.write(
    """
Die App nutzt Daten aus:

- `theme_universe.csv`
- `theme_scores.csv`

Für jede Aktie werden unter anderem gespeichert:

- Preis
- 52W High
- 52W Low
- Trend Score
- Range Momentum
- 3M Momentum
- 1M Momentum
- 20D Momentum
- MA50
- MA200
- MA50 Abstand
- MA200 Abstand
- Preis ueber MA50
- Preis ueber MA200
- Volume
- Avg Volume
- Volume Ratio
- Fundamentaldaten wie Forward PE, Revenue Growth, Earnings Growth und Profit Margin
"""
)

st.markdown("---")

st.markdown("## 3. Trend Score")

st.info(
    """
Der Trend Score zeigt, wo eine Aktie innerhalb ihrer 52-Wochen-Spanne steht.

Formel:

`Trend Score = (Preis - 52W Low) / (52W High - 52W Low)`

Interpretation:

- 0.00 = nahe am 52W Low
- 0.50 = Mitte der 52W-Spanne
- 1.00 = nahe am 52W High

Wichtig:
Der Trend Score ist **kein echtes Momentum**.  
Er zeigt nur, wo die Aktie innerhalb ihrer 52W-Spanne steht.
"""
)

st.markdown("## 4. Range Momentum")

st.info(
    """
Range Momentum zeigt, ob der aktuelle Preis über oder unter der Mitte der 52W-Spanne liegt.

Formel vereinfacht:

`Range Momentum = (Preis - Mitte der 52W-Spanne) / halbe 52W-Spanne`

Interpretation:

- positiv = Aktie steht über der Mitte ihrer 52W-Spanne
- negativ = Aktie steht unter der Mitte ihrer 52W-Spanne

Wichtig:
Range Momentum misst keine Bewegung über Zeit.  
Dafür werden 3M, 1M und 20D Momentum genutzt.
"""
)

st.markdown("---")

st.markdown("## 5. Echtes Momentum: 3M, 1M und 20D")

st.info(
    """
Das echte Momentum misst, wie stark sich der Kurs über einen bestimmten Zeitraum verändert hat.

Genutzt werden:

**3M Momentum**
- ungefähr 63 Handelstage
- zeigt den mittelfristigen Trend

**1M Momentum**
- ungefähr 21 Handelstage
- zeigt die kurzfristige Entwicklung

**20D Momentum**
- ungefähr 20 Handelstage
- dient als zusätzlicher Kurzfrist-Check

Interpretation:

- positives Momentum = Aktie ist im jeweiligen Zeitraum gestiegen
- negatives Momentum = Aktie ist im jeweiligen Zeitraum gefallen

Warum das wichtig ist:

Eine Aktie kann auf 3 Monate stark aussehen, aber kurzfristig bereits kippen.  
Deshalb prüft der Tracker jetzt zusätzlich 1M und 20D Momentum.
"""
)

st.markdown("---")

st.markdown("## 6. MA50, MA200 und MA-Abstand")

st.info(
    """
MA steht für Moving Average, also gleitender Durchschnitt.

Genutzt werden:

- MA50 = Durchschnittskurs der letzten 50 Handelstage
- MA200 = Durchschnittskurs der letzten 200 Handelstage

Zusätzlich berechnet der Tracker:

- MA50 Abstand
- MA200 Abstand
- Preis ueber MA50
- Preis ueber MA200

Beispiel:

- MA50 Abstand +5% = Kurs liegt 5% über dem MA50
- MA50 Abstand -5% = Kurs liegt 5% unter dem MA50

Warum das wichtig ist:

Wenn eine Aktie stark gelaufen ist, aber unter den MA50 fällt, kann das ein Warnsignal sein.  
Wenn sie knapp über dem MA50 liegt und Momentum positiv ist, kann das ein gesünderes Setup sein.
"""
)

st.markdown("---")

st.markdown("## 7. Volume, Avg Volume und Volume Ratio")

st.info(
    """
Volumen zeigt, wie viele Aktien gehandelt wurden.

Der Tracker nutzt:

**Volume**
- aktuelles Tagesvolumen

**Avg Volume**
- durchschnittliches Volumen der letzten ca. 20 Handelstage

**Volume Ratio**
- aktuelles Volumen geteilt durch durchschnittliches Volumen

Interpretation:

- 1.00 = normales Volumen
- 1.20 = 20% höheres Volumen als normal
- 1.50 = 50% höheres Volumen als normal
- 2.00 = doppelt so hohes Volumen wie normal

Warum das wichtig ist:

Frühe Trends sind stärker, wenn sie nicht nur durch Kursbewegung, sondern auch durch erhöhtes Volumen bestätigt werden.
"""
)

st.markdown("---")

st.markdown("## 8. Status")

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

st.markdown("## 9. Preis-Zonen")

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

st.markdown("## 10. Trendrichtung")

st.info(
    """
Die Trendrichtung basiert auf gleitenden Durchschnitten aus dem 1-Jahres-Chart.

Genutzt werden:

- MA50
- MA200

Regeln vereinfacht:

- Aufwaertstrend: Preis > MA50 und MA50 > MA200, stabil bestätigt
- Frischer Aufwaertstrend: Preis > MA50 und MA50 > MA200, aber noch nicht lange bestätigt
- Abwaertstrend: Preis < MA50 und MA50 < MA200
- Turnaround moeglich: Preis > MA50, aber MA50 noch < MA200
- Trend schwaecht sich ab: Preis < MA50, aber MA50 noch > MA200
- Kurzfristig positiv: Preis > MA50, aber MA200 ist noch nicht aussagekräftig
- Kurzfristig negativ: Preis < MA50, aber MA200 ist noch nicht aussagekräftig
- Seitwaerts / unklar: kein klares Bild
"""
)

st.markdown("## 11. Trendphase")

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

st.markdown("## 12. Momentum Risiko")

st.warning(
    """
Momentum Risiko ist eine der wichtigsten Schutzfunktionen des Trackers.

Es soll verhindern, dass Aktien nur deshalb gut aussehen, weil sie stark gestiegen oder stark gefallen sind.

Mögliche Kategorien:

**Normal**
- Momentum wirkt intakt
- kein klares Überhitzungs- oder Bruchsignal

**Ueberhitzt**
- 3M Momentum über ca. 50%
- Aktie ist stark gelaufen, aber noch nicht klar gebrochen

**Extrem ueberhitzt**
- 3M Momentum über ca. 80%
- sehr hohes Rückschlagrisiko für Neueinstiege

**Kippt**
- 3M Momentum war stark
- aber 1M Momentum, 20D Momentum oder MA50 zeigen Schwäche

**Fallend**
- 1M oder 20D Momentum stark negativ
- oder Kurs deutlich unter MA50
- Risiko eines fallenden Messers

**Unklar**
- Daten fehlen oder sind nicht sauber bewertbar
"""
)

st.markdown("## 13. Warum Momentum Risiko wichtig ist")

st.info(
    """
Vorher konnte eine Aktie gut aussehen, obwohl sie bereits kurzfristig kaputt war.

Beispiel:

- 3M Momentum: +80%
- 1M Momentum: -5%
- 20D Momentum: -6%
- Kurs unter MA50

Früher hätte der Tracker eventuell gesagt:
starkes Momentum.

Jetzt sagt er:
Der Trend kippt oder fällt.

Das macht den Tracker konservativer, aber sinnvoller.
"""
)

st.markdown("---")

st.markdown("## 14. Signal")

st.info(
    """
Das Signal ist eine technische Einordnung.

Es nutzt:

- Trend Score
- Range Momentum
- 3M Momentum
- Theme Status
- Bullisch-Anteil im Sub Theme
- Momentum Risiko als Schutzfilter

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
- oder Momentum Risiko ist erhöht

Wichtig:
Wenn Momentum Risiko Ueberhitzt, Extrem ueberhitzt, Fallend oder Kippt ist, wird das Signal bewusst konservativer.
"""
)

st.markdown("---")

st.markdown("## 15. Fundamental Score")

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

st.markdown("## 16. Fundamental Quality")

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

st.markdown("## 17. Entry Score")

st.info(
    """
Der Entry Score bewertet, ob der aktuelle Einstieg technisch und fundamental interessant wirkt.

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

Danach wird der Entry Score durch Momentum Risiko angepasst.
"""
)

st.markdown("## 18. Anpassung durch Momentum Risiko")

st.warning(
    """
Der Entry Score wird reduziert, wenn das Momentum Risiko erhöht ist.

Regeln:

- Ueberhitzt: Entry Score -2
- Extrem ueberhitzt: Entry Score -4
- Fallend: Entry Score -3
- Kippt: Entry Score -3
- Unklar: Entry Score -1

Warum?

Eine Aktie kann fundamental stark sein und trotzdem kurzfristig ein schlechtes Timing haben.  
Der Abschlag soll verhindern, dass überhitzte oder fallende Aktien zu gut gerankt werden.
"""
)

st.markdown("## 19. Entry Quality")

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

st.markdown("## 20. Risiko")

st.info(
    """
Das Risiko basiert auf Zone und Trendrichtung.

Regeln vereinfacht:

- Sehr hoch: Weak Zone
- Hoch: Turnaround moeglich oder frischer Aufwaertstrend
- Mittel: Upper Range
- Niedrig: stabile Lage ohne klare Risikowarnung

Wichtig:
Ein frischer Aufwärtstrend kann attraktiv sein, ist aber oft noch nicht bestätigt. Deshalb wird er als höheres Risiko gewertet.
"""
)

st.markdown("## 21. Exit Signal")

st.info(
    """
Das Exit Signal zeigt, ob eher Halten, Vorsicht oder Gewinnsicherung naheliegt.

Regeln:

- Gewinne sichern: Upper Range und Momentum schwächt sich ab
- Vorsicht: Trend schwaecht sich ab, Fallend oder Kippt
- Hold: kein klares Ausstiegssignal

Das ist keine Verkaufsaufforderung, sondern ein Warnhinweis.
"""
)

st.markdown("---")

st.markdown("## 22. Master Score")

st.info(
    """
Der Master Score kombiniert Entry Score, Fundamental Score, Risiko und Momentum Risiko.

Formel vereinfacht:

`Master Score = Entry Score * 0.5 + Fundamental Score * 0.3 + Risiko-Anpassung + Momentum-Risiko-Anpassung`

Risiko-Anpassung:

- Niedrig = +1
- Mittel = 0
- Hoch = -1
- Sehr hoch = -2

Momentum-Risiko-Anpassung:

- Ueberhitzt = negativer Abschlag
- Extrem ueberhitzt = starker Abschlag
- Fallend / Kippt = starker Abschlag
- Unklar = kleiner Abschlag

Interpretation:
Der Master Score ist die verdichtete Gesamtbewertung einer Aktie.
"""
)

st.markdown("## 23. Master Signal")

st.info(
    """
Das Master Signal ist die einfache Handlungseinordnung.

Regeln vereinfacht:

- 🟢 Einstieg sinnvoll: Master Score >= 7
- 🟡 Beobachten: Master Score >= 5
- 🔴 Kein Einstieg: Master Score < 5

Zusatzregel:
Wenn Momentum Risiko Extrem ueberhitzt, Fallend oder Kippt ist, wird die Aktie auf Kein Einstieg gesetzt.

Wenn Momentum Risiko Ueberhitzt ist, wird sie höchstens auf Beobachten gesetzt.
"""
)

st.markdown("---")

st.markdown("## 24. Ranking-Seite")

st.info(
    """
Die Ranking-Seite ist die breite Screening-Ansicht.

Sie zeigt viele Aktien gleichzeitig und erlaubt Filter nach:

- Main Theme
- Sub Theme
- Zone
- Signal
- Entry Quality
- Risiko
- Fundamental Quality
- 3M Momentum
- Momentum Risiko

Besonders wichtig:
Die Ranking-Seite zeigt jetzt auch 1M Momentum, 20D Momentum, MA50 Abstand und Momentum Risiko.

Dadurch sieht man schneller, ob ein scheinbar gutes Setup kurzfristig bereits kippt.
"""
)

st.markdown("---")

st.markdown("## 25. Top Opportunities")

st.info(
    """
Top Opportunities ist keine einfache Liste der besten Aktien.

Die Seite trennt zwischen verschiedenen Perspektiven:

1. Short Term Chancen
2. Long Term Core
3. Long Term Entry
4. Early Plays

Jede Kategorie hat einen anderen Zweck.
"""
)

st.markdown("## 26. Short Term Chancen")

st.info(
    """
Short Term bedeutet in dieser App:

ca. 2 Wochen bis 3 Monate.

Das Short-Term-Ranking gewichtet stärker:

- Entry Score
- 3M Momentum
- 1M Momentum
- 20D Momentum
- MA50 Abstand
- Risiko
- Fundamental Quality als Bonus

Ausgeschlossen werden bewusst:

- überhitzte Aktien
- fallende Aktien
- kippende Aktien
- Aktien mit schwacher Trendrichtung

Ziel:
Aktien finden, die kurzfristig bis mittelfristig ein interessantes technisches Setup zeigen.
"""
)

st.markdown("## 27. Long Term Core")

st.info(
    """
Long Term Core zeigt langfristig interessante Qualitätswerte.

Hier stehen stärker im Fokus:

- Fundamental Score
- Fundamental Quality
- Structural Score
- Long Score
- langfristige Themenqualität

Wichtig:
Long Term Core schließt überhitzte Aktien nicht automatisch aus.

Warum?
Eine langfristig starke Aktie kann kurzfristig überhitzt sein, aber trotzdem ein guter langfristiger Beobachtungskandidat bleiben.

Deshalb wird bei Long Term Core eher gewarnt, statt automatisch ausgeschlossen.
"""
)

st.markdown("## 28. Long Term Entry")

st.info(
    """
Long Term Entry sucht langfristig interessante Aktien mit besserem Timing.

Fokus:

- Fundamental Quality Hoch oder Mittel
- gutes Long Score Profil
- Momentum Risiko Normal
- 1M Momentum positiv
- 20D Momentum positiv
- MA50 Abstand nicht deutlich negativ
- keine klare Schwäche in der Trendrichtung

Unterschied zu Long Term Core:

Long Term Core fragt:
Ist das Unternehmen langfristig interessant?

Long Term Entry fragt:
Ist der Einstieg jetzt auch halbwegs sinnvoll?
"""
)

st.markdown("---")

st.markdown("## 29. Early Plays")

st.info(
    """
Early Plays sind ein zusätzlicher Screening-Bereich.

Ziel:
Aktien identifizieren, die sich noch früh in einer möglichen Aufwärtsbewegung befinden.

Early Plays sind keine fertigen Trends, sondern mögliche Anfangsphasen.

Neue Logik:

- Trend Score über 0.20, aber unter 0.78
- 3M Momentum leicht bis moderat positiv
- 1M Momentum nicht stark negativ
- 20D Momentum nicht stark negativ
- Momentum Risiko muss Normal sein
- MA50 Abstand darf nicht stark negativ sein
- MA50 Abstand darf aber auch nicht extrem überhitzt sein
- Trendrichtung darf früh, positiv oder noch unklar sein
- Volume Ratio muss leicht erhöht sein

Interpretation:

Early Plays sind Watchlist-Kandidaten für frühe Trends.  
Sie sind oft riskanter als Short Term Chancen, können aber früher auf neue Bewegungen hinweisen.
"""
)

st.markdown("## 30. Early Score")

st.info(
    """
Der Early Score bewertet die Qualität eines möglichen frühen Trends.

Er kombiniert:

1. Fundamentaldaten
- Fundamental Score wird stark berücksichtigt

2. Position in der Range
- niedriger bis mittlerer Trend Score wird belohnt

3. 3M Momentum
- leicht positives Momentum ist ideal
- zu starkes Momentum wird teilweise negativ bewertet

4. 1M und 20D Momentum
- positives kurzfristiges Momentum wird belohnt
- negatives kurzfristiges Momentum wird bestraft

5. Trendrichtung
- Frischer Aufwaertstrend wird stark belohnt
- Turnaround moeglich wird leicht belohnt
- schwache Trends werden abgewertet

6. MA50 Abstand
- Nähe zum MA50 kann attraktiv sein
- deutlicher Bruch unter MA50 wird bestraft
- extreme Entfernung über MA50 wird ebenfalls bestraft

7. Volume Ratio
- erhöhtes Volumen wird belohnt

8. Momentum Risiko
- alles außer Normal wird stark bestraft
"""
)

st.markdown("## 31. Volume Ratio bei Early Plays")

st.info(
    """
Early Plays nutzen Volume Ratio als Smart-Money-Näherung.

Regeln im Score:

- Volume Ratio > 2.00 = sehr stark positiv
- Volume Ratio > 1.50 = stark positiv
- Volume Ratio > 1.15 = leicht positiv
- Volume Ratio < 0.80 = leicht negativ

Im Filter wird zusätzlich verlangt:

- Volume Ratio > 1.05

Warum?

Ein früher Trend ist glaubwürdiger, wenn der Kurs nicht nur steigt, sondern auch mehr Volumen in die Aktie kommt.
"""
)

st.markdown("## 32. High Conviction")

st.info(
    """
High Conviction ist eine zusätzliche Kennzeichnung für besonders starke Early Plays.

Bedingungen:

- Early Score >= 12
- Fundamental Quality = Hoch
- 3M Momentum positiv
- 1M Momentum positiv
- 20D Momentum positiv
- Momentum Risiko Normal

Interpretation:

- mehrere starke Faktoren treffen gleichzeitig zusammen
- höherwertiges Early-Play-Setup

Wichtig:
High Conviction bedeutet nicht garantiert Erfolg.  
Es zeigt nur, dass viele Kriterien gleichzeitig erfüllt sind.
"""
)

st.markdown("---")

st.markdown("## 33. Structural Score")

st.info(
    """
Der Structural Score ist ein einfacher thematischer Bonus oder Abschlag.

Positiv gewertet werden strukturelle Wachstumsthemen wie:

- AI
- Semiconductors
- Chips
- Photonics
- Cloud
- Data Center
- Networking
- Software
- Automation
- Memory
- Compute

Negativ gewertet werden eher zyklische Themen wie:

- Energy
- Oil
- Gas
- Commodities
- Mining
- Chemicals
- Agriculture

Wichtig:
Das ist nur eine grobe thematische Einordnung.  
Sie ersetzt keine Branchenanalyse.
"""
)

st.markdown("## 34. Long Type")

st.info(
    """
Long Type ordnet eine Aktie thematisch ein.

Mögliche Kategorien:

- Structural Growth
- Cyclical
- Quality / Defensive

Diese Einordnung hilft, Long-Term-Kandidaten besser zu verstehen.
"""
)

st.markdown("## 35. Long Warning")

st.warning(
    """
Long Warning zeigt Warnhinweise bei langfristigen Kandidaten.

Mögliche Warnungen:

- Zu spaet im Trend
- Hype Momentum
- 1M negativ
- 20D negativ
- Unter/nahe MA50
- Ueberhitzt
- Extrem ueberhitzt
- Trend kippt
- Erhoehtes Risiko

Wichtig:
Eine Long-Warning bedeutet nicht automatisch, dass die Aktie schlecht ist.  
Sie zeigt nur, dass das aktuelle Timing oder Risiko genauer geprüft werden sollte.
"""
)

st.markdown("---")

st.markdown("## 36. Warum Review wichtig ist")

st.info(
    """
Review ist kein schlechtes Signal.

Review bedeutet:

- Setup ist nicht eindeutig
- Timing ist nicht sauber
- Momentum Risiko ist erhöht
- Datenlage ist unklar
- Aktie braucht mehr Prüfung

Gerade bei High-Growth- und Halbleiteraktien ist Review oft sinnvoller als ein zu aggressives Attraktiv-Signal.
"""
)

st.markdown("## 37. Warum der Tracker in Bärenmärkten vorsichtiger sein muss")

st.warning(
    """
In Bärenmärkten oder starken Korrekturen können viele Aktien optisch günstig aussehen.

Problem:

- Trend Score fällt
- Aktie ist weit vom Hoch entfernt
- alte Logik könnte das als Chance interpretieren

Aber:

- 1M Momentum kann negativ sein
- 20D Momentum kann negativ sein
- Kurs kann unter MA50 liegen
- Momentum Risiko kann Fallend sein

Deshalb sind die neuen Schutzfilter wichtig.

Der Tracker soll nicht automatisch fallende Aktien als Chancen einstufen.
"""
)

st.markdown("---")

st.markdown("## 38. Unterschiede der Bereiche")

st.info(
    """
Die App unterscheidet mehrere Perspektiven:

Ranking:
- breite Übersicht
- viele Filter
- gut zum Sortieren und Vergleichen

Aktien-Detail:
- Einzelanalyse einer Aktie
- zeigt Score, Fazit, Chart, Momentum Risiko und Fundamentaldaten

Top Opportunities:
- kuratierte Listen
- verschiedene Zeithorizonte

Short Term:
- kurzfristiges technisches Setup

Long Term Core:
- langfristige Qualität

Long Term Entry:
- langfristige Qualität mit besserem Timing

Early Plays:
- frühe mögliche Trendstarts mit Volumenbestätigung
"""
)

st.markdown("---")

st.markdown("## 39. Grenzen des Modells")

st.warning(
    """
Das Modell hat klare Grenzen:

- Es garantiert keine Gewinne.
- Es kann Fake Breakouts nicht sicher verhindern.
- Es berücksichtigt keine Nachrichtenlage.
- Es bewertet Managementqualität nur indirekt.
- Fundamentaldaten können fehlen oder veraltet sein.
- Yahoo-Finance-Daten können unvollständig sein.
- Volumendaten können bei manchen Aktien verzerrt sein.
- Ein gutes Signal bedeutet nicht, dass die Aktie nicht trotzdem fällt.
- Ein schlechtes Signal bedeutet nicht, dass die Aktie nicht steigen kann.
- In Crashs oder Bärenmärkten können technische Signale schnell versagen.

Das Tool ist ein Screening- und Strukturierungstool, keine Finanzberatung.
"""
)

st.markdown("## 40. Praktische Nutzung")

st.success(
    """
Sinnvolle Nutzung:

1. Zuerst Ranking-Seite öffnen
2. Nach Momentum Risiko Normal filtern
3. Entry Quality und Fundamental Quality prüfen
4. Danach Top Opportunities anschauen
5. Einzelwerte auf der Detailseite prüfen
6. Bei Review, Kippt, Fallend oder Extrem ueberhitzt besonders vorsichtig sein

Der Tracker soll helfen, Kandidaten zu priorisieren.  
Die finale Entscheidung muss immer außerhalb des Trackers geprüft werden.
"""
)

st.markdown("## 41. Transparenz")

st.success(
    """
Alle Scores sind regelbasiert.

Es gibt:

- keine bezahlten Platzierungen
- keine manuelle Bevorzugung einzelner Aktien
- keine versteckten Gewichtungen
- keine Blackbox-KI-Entscheidung

Wenn eine Aktie gut rankt, dann weil sie nach den definierten Regeln gut abschneidet.
"""
)
