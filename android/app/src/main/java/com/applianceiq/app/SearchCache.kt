package com.applianceiq.app

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.flow.first

private val Context.searchCacheDataStore by preferencesDataStore(
    name = "search_cache"
)

private val CACHED_SEARCHES_KEY = stringPreferencesKey("cached_searches")

class SearchCache(context: Context) {
    private val appContext = context.applicationContext
    private val gson = Gson()

    private val cacheType =
        object : TypeToken<LinkedHashMap<String, SearchResponse>>() {}.type

    suspend fun save(query: String, response: SearchResponse) {
        val normalizedQuery = normalizeQuery(query)

        appContext.searchCacheDataStore.edit { preferences ->
            val cache = readCache(preferences[CACHED_SEARCHES_KEY])

            cache.remove(normalizedQuery)
            cache[normalizedQuery] = response

            while (cache.size > MAX_CACHED_SEARCHES) {
                cache.remove(cache.keys.first())
            }

            preferences[CACHED_SEARCHES_KEY] = gson.toJson(cache)
        }
    }

    suspend fun get(query: String): SearchResponse? {
        val preferences = appContext.searchCacheDataStore.data.first()
        val cache = readCache(preferences[CACHED_SEARCHES_KEY])

        return cache[normalizeQuery(query)]
    }

    private fun readCache(savedJson: String?): LinkedHashMap<String, SearchResponse> {
        if (savedJson.isNullOrBlank()) {
            return LinkedHashMap()
        }

        return try {
            gson.fromJson(savedJson, cacheType) ?: LinkedHashMap()
        } catch (exception: Exception) {
            LinkedHashMap()
        }
    }

    private fun normalizeQuery(query: String): String {
        return query.trim().lowercase()
    }

    private companion object {
        const val MAX_CACHED_SEARCHES = 20
    }
}