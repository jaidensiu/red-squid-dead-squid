package com.example.squid.ui.game

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.sp
import com.example.squid.ui.theme.SevenSegmentFontFamily
import kotlinx.coroutines.delay
import org.koin.compose.viewmodel.koinViewModel
import kotlin.time.Duration.Companion.seconds

@Composable
fun GameScreen(viewModel: GameViewModel = koinViewModel()) {
    val state = viewModel.state.collectAsState()
    var remainingTime by remember { mutableStateOf(value = 60L) }

    LaunchedEffect(state.value.endEpoch) {
        while (state.value.endEpoch != null) {
//            val currentTime = Clock.System.now().epochSeconds
//            remainingTime = state.value.endEpoch?.minus(currentTime) ?: 0L
            delay(1.seconds)
            remainingTime--
        }
    }

    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        val minutes = remainingTime / 60
        val seconds = remainingTime % 60
        val formattedTime = "${if (minutes < 10) "0" else ""}$minutes:${if (seconds < 10) "0" else ""}$seconds"

        Text(
            text = formattedTime,
            color = Color.White,
            fontSize = 144.sp,
            fontFamily = SevenSegmentFontFamily()
        )
    }
}
