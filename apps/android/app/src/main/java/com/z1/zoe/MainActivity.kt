package com.z1.zoe

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val moduleTitle = findViewById<TextView>(R.id.moduleTitle)
        val moduleDescription = findViewById<TextView>(R.id.moduleDescription)

        val modules = mapOf(
            R.id.buttonChat to Pair(
                getString(R.string.module_chat_title),
                getString(R.string.module_chat_description)
            ),
            R.id.buttonMemory to Pair(
                getString(R.string.module_memory_title),
                getString(R.string.module_memory_description)
            ),
            R.id.buttonTools to Pair(
                getString(R.string.module_tools_title),
                getString(R.string.module_tools_description)
            ),
            R.id.buttonReports to Pair(
                getString(R.string.module_reports_title),
                getString(R.string.module_reports_description)
            )
        )

        modules.forEach { (buttonId, content) ->
            findViewById<Button>(buttonId).setOnClickListener {
                moduleTitle.text = content.first
                moduleDescription.text = content.second
            }
        }
    }
}
