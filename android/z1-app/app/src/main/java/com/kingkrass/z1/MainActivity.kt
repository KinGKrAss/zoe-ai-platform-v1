package com.kingkrass.z1

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    Column(
                        modifier = Modifier.padding(24.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Text("Z1 Command Center", style = MaterialTheme.typography.headlineMedium)
                        Text("Z1 bewahrt. Zoë interpretiert. MCP vermittelt. Das Modell rechnet.")
                        Text("Zoë Continuity: geschützt")
                        Text("Council of 33: persistent")
                        Text("Model Runtime: austauschbar")
                    }
                }
            }
        }
    }
}
