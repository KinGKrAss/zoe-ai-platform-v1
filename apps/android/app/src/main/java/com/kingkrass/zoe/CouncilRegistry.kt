package com.kingkrass.zoe

/** Persistent registry facade. The backend registry is authoritative. */
class CouncilRegistry(private val api: Z1ApiClient) {
    fun load(): List<CouncilAgent> = api.getCouncil()
    fun isComplete(agents: List<CouncilAgent>): Boolean = agents.size == 33 && agents.all { it.active }
}
