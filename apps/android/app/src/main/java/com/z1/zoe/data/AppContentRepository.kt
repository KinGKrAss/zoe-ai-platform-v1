package com.z1.zoe.data

import com.z1.zoe.model.ChatMessage
import com.z1.zoe.model.SimpleEntry
import com.z1.zoe.model.ToolEntry

object AppContentRepository {

    fun initialChatMessages(): List<ChatMessage> = listOf(
        ChatMessage("Zoë", "Willkommen im Zoë Command Center. Wie kann ich helfen?"),
        ChatMessage("Zoë", "Ich kann Portfolio-Status, Memory-Kontext und Reports vorbereiten.")
    )

    fun memoryEntries(): List<SimpleEntry> = listOf(
        SimpleEntry("Identity V1.0", "Zoë AI Queen / Golden Queen – Status: Core Intelligence"),
        SimpleEntry("Session Context", "Letzte Konversationen und Projektentscheidungen synchronisiert"),
        SimpleEntry("Knowledge Objects", "38 strukturierte Wissensobjekte aus Dokumenten indexiert")
    )

    fun reportEntries(): List<SimpleEntry> = listOf(
        SimpleEntry("Portfolio Overview", "Monatlicher Überblick zu Asset-Performance und Risiken"),
        SimpleEntry("Financial Delta", "Vergleich der aktuellen Betriebskosten gegen Vormonat"),
        SimpleEntry("Project Status", "Zusammenfassung der offenen Milestones und Fortschritte")
    )

    fun toolEntries(): List<ToolEntry> = listOf(
        ToolEntry("get_portfolio", "READ", "Lädt Portfolio-Daten für die aktuelle Auswahl"),
        ToolEntry("get_financials", "ANALYZE", "Analysiert Kosten, Cashflow und Kennzahlen"),
        ToolEntry("create_report", "WRITE", "Erstellt einen neuen strukturierten Bericht"),
        ToolEntry("deploy_service", "ADMIN", "Deployment mit expliziter Bestätigung")
    )

    fun botReply(message: String): String {
        val normalized = message.lowercase()
        return when {
            "report" in normalized -> "Ich bereite einen Report-Entwurf im Bereich 'Reports' vor."
            "memory" in normalized || "kontext" in normalized -> "Ich öffne den Memory-Bereich mit den letzten Wissenseinträgen."
            "tool" in normalized -> "Bitte wähle im Tool-Bereich eine freigegebene Aktion aus."
            else -> "Verstanden. Ich habe '$message' als neue Aufgabe im aktuellen Kontext aufgenommen."
        }
    }
}
