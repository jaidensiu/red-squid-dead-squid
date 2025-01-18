package com.example.squid.app

import kotlinx.serialization.Serializable

sealed interface Route {
    @Serializable
    data object RouteGraph : Route

    @Serializable
    data object Welcome : Route

    @Serializable
    data object Register : Route
}
