package com.z1.zoe

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ModuleCatalogTest {

    @Test
    fun moduleCatalogContainsCoreSections() {
        val moduleIds = listOf("chat", "memory", "tools", "reports")

        assertEquals(4, moduleIds.size)
        assertTrue(moduleIds.contains("chat"))
        assertTrue(moduleIds.contains("memory"))
        assertTrue(moduleIds.contains("tools"))
        assertTrue(moduleIds.contains("reports"))
    }
}
