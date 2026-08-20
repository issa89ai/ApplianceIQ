package com.applianceiq.app


import androidx.compose.ui.platform.LocalContext
import androidx.compose.foundation.clickable
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.applianceiq.app.ui.theme.ApplianceIQTheme
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            ApplianceIQTheme {
                ApplianceIqScreen()
            }
        }
    }
}

@Composable
fun ApplianceIqScreen() {
    var query by rememberSaveable { mutableStateOf("") }
    var results by remember { mutableStateOf<List<SearchResult>>(emptyList()) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    val context = LocalContext.current
    val searchCache = remember(context) { SearchCache(context) }
    var cacheMessage by remember { mutableStateOf<String?>(null) }

    val scope = rememberCoroutineScope()

    Scaffold { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                Text(
                    text = "ApplianceIQ",
                    style = MaterialTheme.typography.headlineMedium
                )
            }

            item {
                Text(
                    text = "Describe your dryer's symptom to find likely causes.",
                    style = MaterialTheme.typography.bodyMedium
                )
            }

            item {
                TextField(
                    value = query,
                    onValueChange = { query = it },
                    label = { Text("Example: clothes come out still wet") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
            }

            item {
                Button(
                    onClick = {
                        val searchQuery = query.trim()

                        scope.launch {
                            isLoading = true
                            errorMessage = null
                            cacheMessage = null

                            try {
                                val response = ApplianceIqApiClient.api.search(searchQuery)

                                results = response.results
                                searchCache.save(searchQuery, response)
                            } catch (exception: Exception) {
                                val cachedResponse = searchCache.get(searchQuery)

                                if (cachedResponse != null) {
                                    results = cachedResponse.results
                                    cacheMessage = "Showing a saved result from this phone."
                                } else {
                                    errorMessage =
                                        "Could not reach the ApplianceIQ backend, and no saved result exists " +
                                                "for this symptom yet."
                                }
                            } finally {
                                isLoading = false
                            }
                        }
                    },
                    enabled = query.isNotBlank() && !isLoading,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Search troubleshooting guides")
                }
            }

            if (isLoading) {
                item {
                    CircularProgressIndicator()
                }
            }

            errorMessage?.let { message ->
                item {
                    Text(
                        text = message,
                        color = MaterialTheme.colorScheme.error
                    )
                }
            }

            items(results, key = { it.wikiid }) { result ->
                SearchResultCard(result)
            }
        }
    }
}

@Composable
fun SearchResultCard(result: SearchResult) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = result.title,
                style = MaterialTheme.typography.titleMedium
            )

            Text(
                text = "Match score: ${(result.score * 100).toInt()}%",
                style = MaterialTheme.typography.bodySmall
            )

            Text(
                text = result.description,
                style = MaterialTheme.typography.bodyMedium
            )

            result.causes?.takeIf { it.isNotEmpty() }?.let { causes ->
                Text(
                    text = "Possible causes:",
                    style = MaterialTheme.typography.titleSmall
                )

                causes.forEach { cause ->
                    ExpandableCause(cause)
                }
            }

            result.branches?.takeIf { it.isNotEmpty() }?.let { branches ->
                Text(
                    text = "Related troubleshooting guides:",
                    style = MaterialTheme.typography.titleSmall
                )

                branches.forEach { branch ->
                    Text(text = "• ${branch.title}")
                }
            }
        }
    }
}
@Composable
fun ExpandableCause(cause: Cause) {
    var isExpanded by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { isExpanded = !isExpanded }
            .padding(vertical = 4.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Text(
            text = "• ${cause.title}",
            style = MaterialTheme.typography.bodyLarge
        )

        Text(
            text = if (isExpanded) {
                "Tap to hide repair steps"
            } else {
                "Tap to see repair steps"
            },
            style = MaterialTheme.typography.bodySmall
        )

        if (isExpanded) {
            Text(
                text = cause.steps,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}