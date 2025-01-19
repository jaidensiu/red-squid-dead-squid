package com.example.squid.data

import kotlinx.serialization.Serializable

@Serializable
data class TestSenderMessage(
    val type: String,
    val data: String
)

@Serializable
data class PlayerInfoSenderMessage(
    val type: String,
    val data: List<String>
)

@Serializable
data class ReceiverMessage(
    val type: String,
    val data: String
)
