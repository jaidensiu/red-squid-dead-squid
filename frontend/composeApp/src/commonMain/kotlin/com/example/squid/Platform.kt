package com.example.squid

interface Platform {
    val name: String
}

expect fun getPlatform(): Platform