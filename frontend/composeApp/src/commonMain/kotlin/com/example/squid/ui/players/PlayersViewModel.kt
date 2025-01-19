package com.example.squid.ui.players

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

class PlayersViewModel : ViewModel() {
    private val _state = MutableStateFlow(PlayersScreenState())
    val state = _state.asStateFlow()

    fun onAddPlayer(image: ByteArray) {
        val newPlayer = Player(image = image)
        _state.update {
            it.copy(players = it.players + newPlayer)
        }
    }

    companion object {
        const val NUM_PLAYERS = 4
    }
}
