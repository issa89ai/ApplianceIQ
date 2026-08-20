package com.applianceiq.app

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.Query

interface ApplianceIqApi {
    @GET("search")
    suspend fun search(
        @Query("q") query: String,
        @Query("top_k") topK: Int = 3
    ): SearchResponse
}

object ApplianceIqApiClient {
    private const val BASE_URL = "http://127.0.0.1:8000/"

    val api: ApplianceIqApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApplianceIqApi::class.java)
    }
}