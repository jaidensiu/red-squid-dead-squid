@file:OptIn(ExperimentalEncodingApi::class)

package com.example.squid.data

import com.example.squid.ui.game.GameViewModel
import com.example.squid.ui.players.Player
import io.ktor.client.HttpClient
import io.ktor.client.plugins.websocket.DefaultClientWebSocketSession
import io.ktor.client.plugins.websocket.webSocketSession
import io.ktor.client.request.url
import io.ktor.websocket.Frame
import io.ktor.websocket.readText
import kotlinx.coroutines.delay
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlin.io.encoding.Base64
import kotlin.io.encoding.ExperimentalEncodingApi

class GameWebSocket(
    private val viewModel: GameViewModel,
    private val client: HttpClient
) {
    private var session: DefaultClientWebSocketSession? = null
    private val maxRetries = 3
    private val retryDelay = 2000L

    suspend fun connect() {
        var attempt = 0
        while (attempt < maxRetries) {
            try {
                session = client.webSocketSession { url(URL) }
                if (session != null) {
                    listenForMessages()
                    return
                } else {
                    println("Failed to establish WebSocket session, retrying...")
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
            attempt++
            delay(retryDelay)
        }
        println("Failed to establish WebSocket session after $maxRetries attempts")
    }

    private suspend fun listenForMessages() {
        session?.let { session ->
            for (frame in session.incoming) {
                when (frame) {
                    is Frame.Text -> {
                        val message = frame.readText()
                        println("GameWebSocket.listenForMessages(): $message")
                        handleMessage(message)
                    }

                    is Frame.Binary -> println("Binary: $frame")

                    is Frame.Close -> print("Close: $frame")

                    is Frame.Ping -> print("Ping: $frame")

                    is Frame.Pong -> print("Pong: $frame")

                    else -> print("Else: $frame")
                }
            }
        }
    }

    private fun handleMessage(message: String) {
        val json = Json {
            ignoreUnknownKeys = true
        }
        println("GameWebSocket.handleMessage(): $message")
        val parsedMessage = json.decodeFromString<ReceiverMessage>(message)
        when (parsedMessage.type) {
            "game_end_time" -> {
                println("GameWebSocket.handleMessage(GameEndTimeMessage): $message")
                viewModel.handleGameEndTime(parsedMessage.data)
            }

            "eliminated_players" -> {
                viewModel.handleEliminatedPlayers(parsedMessage.data)
            }

            "game_over" -> {
                viewModel.handleGameOver(parsedMessage.data)
            }
        }
    }

    suspend fun sendPlayers(players: List<Player>) {
        val message = PlayerInfoSenderMessage(
            type = "players_info",
            data = players.map { Base64.encode(it.image) }
        )
        val jsonMessage = Json.encodeToString(message)
        println("GameWebSocket.sendPlayers.session $session")
        try {
            session!!.flush()
            session!!.outgoing.send(Frame.Text(jsonMessage))
            println("GameWebSocket.sendPlayers Successful")
        } catch (e: Exception) {
            e.printStackTrace()
            println("GameWebSocket.sendPlayers !Successful")
        }
    }

    companion object {
        private const val TEST_URL = "ws://10.19.130.170:8765"
        private const val URL = "ws://10.19.133.46:8765"
    }
}
