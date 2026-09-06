package com.applianceiq.app

import android.os.Bundle
import android.content.Intent
import android.net.Uri
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.clickable
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
    var currentGuideIndex by remember { mutableStateOf(0) }
    var diagnosisSession by remember { mutableStateOf(0) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var cacheMessage by remember { mutableStateOf<String?>(null) }

    val context = LocalContext.current
    val searchCache = remember(context) { SearchCache(context) }
    val scope = rememberCoroutineScope()
    val currentResult = results.getOrNull(currentGuideIndex)

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
                    text = "Describe your dryer's symptom to begin a guided diagnosis.",
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
                            results = emptyList()
                            currentGuideIndex = 0

                            try {
                                val response = ApplianceIqApiClient.api.search(searchQuery)

                                results = response.results
                                diagnosisSession += 1
                                searchCache.save(searchQuery, response)
                            } catch (exception: Exception) {
                                val cachedResponse = searchCache.get(searchQuery)

                                if (cachedResponse != null) {
                                    results = cachedResponse.results
                                    diagnosisSession += 1
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
                    Text("Start diagnosis")
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

            cacheMessage?.let { message ->
                item {
                    Text(
                        text = message,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }

            currentResult?.let { result ->
                item {
                    GuidedDiagnosisCard(
                        result = result,
                        diagnosisSession = diagnosisSession,
                        onTryNextGuide = if (currentGuideIndex < results.lastIndex) {
                            { currentGuideIndex += 1 }
                        } else {
                            null
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun GuidedDiagnosisCard(
    result: SearchResult,
    diagnosisSession: Int,
    onTryNextGuide: (() -> Unit)?
) {
    val causes = result.causes.orEmpty()
    val context = LocalContext.current
    var currentCauseIndex by rememberSaveable(result.wikiid, diagnosisSession) {
        mutableStateOf(0)
    }
    var showSteps by rememberSaveable(result.wikiid, diagnosisSession) {
        mutableStateOf(false)
    }
    var isResolved by rememberSaveable(result.wikiid, diagnosisSession) {
        mutableStateOf(false)
    }

    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Best matching issue",
                style = MaterialTheme.typography.labelLarge
            )

            Text(
                text = result.title,
                style = MaterialTheme.typography.titleLarge
            )


            Text(
                text = result.description,
                style = MaterialTheme.typography.bodyMedium
            )
            result.source?.let { source ->
                Text(
                    text = "Source: ${source.provider} · ${source.license}",
                    style = MaterialTheme.typography.labelSmall
                )

                source.source_page_url?.let { url ->
                    Text(
                        text = "View original source",
                        style = MaterialTheme.typography.labelMedium,
                        modifier = Modifier.clickable {
                            context.startActivity(
                                Intent(Intent.ACTION_VIEW, Uri.parse(url))
                            )
                        }
                    )
                }
            }
            if (causes.isEmpty()) {
                Text(
                    text = "This issue needs a more specific troubleshooting guide.",
                    style = MaterialTheme.typography.titleSmall
                )

                result.branches?.forEach { branch ->
                    Text(text = "• ${branch.title}")
                }

                onTryNextGuide?.let { showNextGuide ->
                    Button(
                        onClick = showNextGuide,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Try the next matching issue")
                    }
                }
            } else if (isResolved) {
                Text(
                    text = "Great — this issue has been marked as resolved.",
                    style = MaterialTheme.typography.titleMedium
                )

                Button(
                    onClick = {
                        currentCauseIndex = 0
                        showSteps = false
                        isResolved = false
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Start this guide again")
                }
            } else {
                val cause = causes[currentCauseIndex]

                Text(
                    text = "Suggested check ${currentCauseIndex + 1} of ${causes.size}",
                    style = MaterialTheme.typography.titleSmall
                )

                Text(
                    text = cause.title,
                    style = MaterialTheme.typography.titleMedium
                )

                Button(
                    onClick = { showSteps = !showSteps },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        if (showSteps) {
                            "Hide repair steps"
                        } else {
                            "Show repair steps"
                        }
                    )
                }

                if (showSteps) {
                    Text(
                        text = cause.steps,
                        style = MaterialTheme.typography.bodyMedium
                    )

                    Button(
                        onClick = { isResolved = true },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("This fixed it")
                    }

                    if (currentCauseIndex < causes.lastIndex) {
                        Button(
                            onClick = {
                                currentCauseIndex += 1
                                showSteps = false
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("Not this — show next check")
                        }
                    } else {
                        onTryNextGuide?.let { showNextGuide ->
                            Button(
                                onClick = showNextGuide,
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text("None fixed it — try next matching issue")
                            }
                        } ?: Text(
                            text = "No more matching troubleshooting guides are available.",
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }
        }
    }
}