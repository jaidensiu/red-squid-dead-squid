package com.example.squid.app

import kotlinx.serialization.Serializable

sealed interface Route {
    @Serializable
    data object RouteGraph : Route

    @Serializable
    data object Landing : Route

    @Serializable
    data object Players : Route
}
