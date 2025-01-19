package com.example.squid.ui.game

import com.example.squid.ui.players.Player

data class GameScreenState(
    val endEpoch: Long? = null,
    val players: List<Player> = emptyList(),
    val eliminatedPlayers: List<Int> = emptyList(),
    val isGameOver: Boolean = false
)
