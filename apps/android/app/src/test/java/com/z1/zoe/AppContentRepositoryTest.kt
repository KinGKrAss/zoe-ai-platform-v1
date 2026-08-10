package com.z1.zoe

import com.z1.zoe.data.AppContentRepository
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class AppContentRepositoryTest {

    @Test
    fun coreSectionsContainExpectedEntries() {
        assertTrue(AppContentRepository.memoryEntries().isNotEmpty())
        assertTrue(AppContentRepository.toolEntries().isNotEmpty())
        assertTrue(AppContentRepository.reportEntries().isNotEmpty())
    }

    @Test
    fun botReplyHandlesReportKeyword() {
        val reply = AppContentRepository.botReply("Bitte report für August")
        assertTrue(reply.contains("Report", ignoreCase = true))
    }

    @Test
    fun chatBootstrapsWithWelcomeMessages() {
        assertEquals(2, AppContentRepository.initialChatMessages().size)
    }
}
