package com.example.squid.data

import io.ktor.client.HttpClient

expect object HttpClientFactory {
    fun create(): HttpClient
}
