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
    val branches: List<Branch>? = null
)

data class Cause(
    val title: String,
    val steps: String
)

data class Branch(
    val wikiid: Int,
    val title: String
)