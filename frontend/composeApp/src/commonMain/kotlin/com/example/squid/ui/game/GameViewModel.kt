package com.example.squid.ui.game

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

class GameViewModel : ViewModel() {
    private val _state = MutableStateFlow(GameScreenState())
    val state = _state.asStateFlow()

    fun handleGameEndTime(data: String) {
        println("GameViewModel: handleGameEndTime($data)")
        _state.update { it.copy(endEpoch = data.toLong()) }
    }

    fun handleEliminatedPlayers(data: String) {
        val eliminatedPlayers = data.map { it.toString().toInt() }
        _state.value = _state.value.copy(eliminatedPlayers = eliminatedPlayers)
    }

    fun handleGameOver(data: String) {
        val isGameOver = data.equals(other = "true", ignoreCase = true)
        _state.value = _state.value.copy(isGameOver = isGameOver)
    }
}
