package ai.zoe.z1

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class Session(val userId: String, val accessToken: String)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { Z1App() }
    }
}

@Composable
private fun Z1App() {
    var session by remember { mutableStateOf<Session?>(null) }
    MaterialTheme {
        if (session == null) LoginScreen { session = Session(it, "server-issued-token") }
        else DashboardScreen(session!!.userId)
    }
}

@Composable
private fun LoginScreen(onLogin: (String) -> Unit) {
    Column(Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.Center) {
        Text("Z1", style = MaterialTheme.typography.headlineLarge)
        Text("Secure Z1 client", modifier = Modifier.padding(top = 8.dp, bottom = 24.dp))
        Button(onClick = { onLogin("demo-user") }) { Text("Login") }
    }
}

@Composable
private fun DashboardScreen(userId: String) {
    Column(Modifier.fillMaxSize().padding(24.dp)) {
        Text("Z1 Command Center", style = MaterialTheme.typography.headlineMedium)
        Text("Session: $userId", modifier = Modifier.padding(top = 12.dp))
        Text("FORTUNA · CryptoMarketData · Zoë Memory Core", modifier = Modifier.padding(top = 12.dp))
    }
}
