package com.applianceiq.app

data class SearchResponse(
    val query: String,
    val results: List<SearchResult>
)

data class SearchResult(
    val score: Double,
    val wikiid: Int,
    val title: String,
    val type: String,
    val description: String,
    val causes: List<Cause>? = null,
    val branches: List<Branch>? = null,
    val source: SourceMetadata? = null,
)

data class Cause(
    val title: String,
    val steps: String
)

data class Branch(
    val wikiid: Int,
    val title: String
)
data class SourceMetadata(
    val provider: String,
    val source_page_id: Int,
    val source_page_url: String?,
    val source_api_url: String,
    val license: String,
    val license_url: String,
    val source_modified_unix: Long?,
    val adapted_for_applianceiq: Boolean
)