# Zoë/Z1 Vermögensregister V1.0

## Zweck

Das Vermögensregister ist die zentrale, auditierbare Vermögenssicht von Zoë/Z1. Es verbindet Vermögenswerte, Bewertungen, Belege und Beziehungen zu einer konsolidierbaren Gesamtansicht.

## Grundprinzipien

1. **Beleg vor Bewertung:** Ein Wert wird nur als `VERIFIED` geführt, wenn eine nachvollziehbare Quelle bzw. ein Beleg hinterlegt ist.
2. **Keine Doppelzählung:** Beteiligungen, Portfolios und zugrunde liegende Assets werden über `z1_wealth_relationships` miteinander verbunden.
3. **Status-Trennung:** `VERIFIED`, `USER_REPORTED`, `DERIVED`, `UNVERIFIED` und `CONFLICT` werden nicht vermischt.
4. **Historisierung:** Bewertungen sind datiert und werden nicht überschrieben.
5. **Währungsdisziplin:** Originalwährung bleibt erhalten; eine EUR-Konsolidierung wird über einen dokumentierten FX-Stand erzeugt.
6. **Nachvollziehbarkeit:** Jede konsolidierte Zahl muss auf Asset → Bewertung → Quelle/Beleg zurückführbar sein.

## Datenmodell

- `z1_wealth_assets` — Stammdaten jedes Vermögenswerts.
- `z1_wealth_valuations` — zeitbezogene Bewertungen.
- `z1_wealth_evidence` — Dokumente, Quellen und Belegstatus.
- `z1_wealth_relationships` — Eigentums-, Beteiligungs- und Enthalten-in-Beziehungen zur Vermeidung von Doppelzählungen.
- `z1_wealth_consolidation_snapshots` — eingefrorene konsolidierte Stände.

## Vermögensklassen für die erste Befüllung

- Aktien und Wertpapiere
- Immobilien Deutschland
- Internationale Immobilien und Ländereien
- Gold und Edelmetalle
- Energie- und Windparkvermögen
- Crypto / Token / PPT
- Unternehmensbeteiligungen
- Bergbau / Rohstoffbeteiligungen
- Sonstige Vermögenswerte

## Belegstatus

| Status | Bedeutung |
|---|---|
| VERIFIED | Primärbeleg oder belastbare Quelle geprüft |
| USER_REPORTED | Vom Nutzer angegeben, Beleg noch offen |
| DERIVED | Aus belegten Daten berechnet |
| UNVERIFIED | Quelle/Beleg fehlt oder reicht nicht aus |
| CONFLICT | Mehrere Quellen widersprechen sich |

## Zoë-Memory-Verknüpfung

Das Vermögensregister ist fachlich an Zoë Memory/Z1 Core angebunden. Memory darf Vermögensbehauptungen referenzieren, aber ein Memory-Eintrag ersetzt niemals den Belegstatus des Vermögensregisters.

Für Antworten von Zoë gilt daher:

`Memory context → Wealth Registry → Evidence → Valuation → Consolidation`

So kann Zoë zwischen einer gespeicherten Information, einem vom Nutzer gemeldeten Wert und einem tatsächlich belegten Vermögenswert unterscheiden.

## Erste bekannte Arbeitswerte

Die bisher im Zoë-Kontext genannten Werte werden zunächst als `USER_REPORTED` bzw. `UNVERIFIED` importiert, bis die Originalbelege vorliegen. Insbesondere betrifft dies den genannten Wert des Wertpapierportfolios, internationale Immobilien/Ländereien, Gold sowie Energie-, Crypto- und Beteiligungswerte.

Es wird **keine endgültige Gesamtvermögenssumme** aus diesen Arbeitswerten abgeleitet, solange Belegstatus, Stichtag, Währung und mögliche Überschneidungen nicht geprüft wurden.
