package com.example.squid.data

import io.ktor.client.HttpClient
import io.ktor.client.plugins.websocket.WebSockets
import io.ktor.client.plugins.websocket.webSocketSession
import io.ktor.client.request.url
import io.ktor.websocket.Frame
import io.ktor.websocket.WebSocketSession
import io.ktor.websocket.readText
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

class GameRepository {
    private val client = HttpClient { install(WebSockets) }
    private var session: WebSocketSession? = null

    suspend fun connect() {
        session = client.webSocketSession { url(URL) }
        listenForMessages()
    }

    private suspend fun listenForMessages() {
        session?.let { session ->
            for (frame in session.incoming) {
                when (frame) {
                    is Frame.Text -> {
                        val message = frame.readText()
                        handleMessage(message)
                    }

                    is Frame.Binary -> TODO()
                    is Frame.Close -> TODO()
                    is Frame.Ping -> TODO()
                    is Frame.Pong -> TODO()
                    else -> TODO()
                }
            }
        }
    }

    private fun handleMessage(message: String) {
        val json = Json { ignoreUnknownKeys = true }
        val parsedMessage = json.decodeFromString<Map<String, Any>>(message)
        when (parsedMessage["type"]) {
            "game_end_time" -> handleGameEndTime(parsedMessage["data"] as Long)
            "eliminated_players" -> handleEliminatedPlayers(parsedMessage["data"] as List<Int>)
            "game_over" -> handleGameOver()
        }
    }

    private fun handleGameEndTime(data: Long) {
        // Handle game end time
    }

    private fun handleEliminatedPlayers(data: List<Int>) {
        // Handle eliminated players
    }

    private fun handleGameOver() {
        // Handle game over
    }

    suspend fun sendPlayersInfo(players: List<String>) {
        val message = mapOf(
            "type" to "players_info",
            "data" to players
        )
        val jsonMessage = Json.encodeToString(message)
        session?.send(Frame.Text(jsonMessage))
    }

    companion object {
        private const val URL = "ws://10.19.133.46:8765"
    }
}
