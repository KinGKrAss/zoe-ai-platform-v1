package com.z1.zoe

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.tabs.TabLayout
import com.z1.zoe.adapters.ChatAdapter
import com.z1.zoe.adapters.SimpleEntryAdapter
import com.z1.zoe.adapters.ToolEntryAdapter
import com.z1.zoe.data.AppContentRepository
import com.z1.zoe.model.ChatMessage

class MainActivity : AppCompatActivity() {

    private lateinit var moduleTitle: TextView
    private lateinit var moduleDescription: TextView

    private lateinit var chatSection: View
    private lateinit var memorySection: View
    private lateinit var toolsSection: View
    private lateinit var reportsSection: View

    private lateinit var chatAdapter: ChatAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        moduleTitle = findViewById(R.id.moduleTitle)
        moduleDescription = findViewById(R.id.moduleDescription)

        chatSection = findViewById(R.id.chatSection)
        memorySection = findViewById(R.id.memorySection)
        toolsSection = findViewById(R.id.toolsSection)
        reportsSection = findViewById(R.id.reportsSection)

        setupTabs()
        setupChat()
        setupLists()
        setupReportAction()
        showSection(0)
    }

    private fun setupTabs() {
        val tabs = findViewById<TabLayout>(R.id.moduleTabs)
        tabs.addTab(tabs.newTab().setText(getString(R.string.module_chat_title)))
        tabs.addTab(tabs.newTab().setText(getString(R.string.module_memory_title)))
        tabs.addTab(tabs.newTab().setText(getString(R.string.module_tools_title)))
        tabs.addTab(tabs.newTab().setText(getString(R.string.module_reports_title)))

        tabs.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab) {
                showSection(tab.position)
            }

            override fun onTabUnselected(tab: TabLayout.Tab) = Unit
            override fun onTabReselected(tab: TabLayout.Tab) = Unit
        })
    }

    private fun setupChat() {
        val chatList = findViewById<RecyclerView>(R.id.chatList)
        val chatInput = findViewById<EditText>(R.id.chatInput)
        val sendButton = findViewById<Button>(R.id.chatSendButton)

        chatAdapter = ChatAdapter(AppContentRepository.initialChatMessages())
        chatList.layoutManager = LinearLayoutManager(this)
        chatList.adapter = chatAdapter

        sendButton.setOnClickListener {
            val message = chatInput.text.toString().trim()
            if (message.isEmpty()) return@setOnClickListener

            chatAdapter.addMessage(ChatMessage("You", message))
            chatAdapter.addMessage(ChatMessage("Zoë", AppContentRepository.botReply(message)))
            chatInput.text?.clear()
            chatList.scrollToPosition(chatAdapter.itemCount - 1)
        }
    }

    private fun setupLists() {
        findViewById<RecyclerView>(R.id.memoryList).apply {
            layoutManager = LinearLayoutManager(this@MainActivity)
            adapter = SimpleEntryAdapter(AppContentRepository.memoryEntries())
        }

        findViewById<RecyclerView>(R.id.toolsList).apply {
            layoutManager = LinearLayoutManager(this@MainActivity)
            adapter = ToolEntryAdapter(AppContentRepository.toolEntries())
        }

        findViewById<RecyclerView>(R.id.reportsList).apply {
            layoutManager = LinearLayoutManager(this@MainActivity)
            adapter = SimpleEntryAdapter(AppContentRepository.reportEntries())
        }
    }

    private fun setupReportAction() {
        findViewById<Button>(R.id.generateReportButton).setOnClickListener {
            Toast.makeText(this, R.string.report_generation_hint, Toast.LENGTH_SHORT).show()
        }
    }

    private fun showSection(index: Int) {
        chatSection.visibility = if (index == 0) View.VISIBLE else View.GONE
        memorySection.visibility = if (index == 1) View.VISIBLE else View.GONE
        toolsSection.visibility = if (index == 2) View.VISIBLE else View.GONE
        reportsSection.visibility = if (index == 3) View.VISIBLE else View.GONE

        when (index) {
            0 -> setModuleInfo(R.string.module_chat_title, R.string.module_chat_description)
            1 -> setModuleInfo(R.string.module_memory_title, R.string.module_memory_description)
            2 -> setModuleInfo(R.string.module_tools_title, R.string.module_tools_description)
            3 -> setModuleInfo(R.string.module_reports_title, R.string.module_reports_description)
        }
    }

    private fun setModuleInfo(titleRes: Int, descriptionRes: Int) {
        moduleTitle.text = getString(titleRes)
        moduleDescription.text = getString(descriptionRes)
    }
}
