package com.example.squid.ui.game

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material.MaterialTheme
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
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil3.compose.rememberAsyncImagePainter
import com.example.squid.ui.players.PlayersViewModel
import com.example.squid.ui.theme.SevenSegmentFontFamily
import com.example.squid.ui.theme.ZenDotsFontFamily
import kotlinx.coroutines.delay
import org.koin.compose.viewmodel.koinViewModel
import kotlin.time.Duration.Companion.seconds

@Composable
fun GameScreen(
    gameViewModel: GameViewModel = koinViewModel(),
    playersViewModel: PlayersViewModel = koinViewModel()
) {
    val gameState = gameViewModel.state.collectAsState()
    val playersState = playersViewModel.state.collectAsState()
    var remainingTime by remember { mutableStateOf(value = 60) }

    LaunchedEffect(gameState.value.endEpoch) {
        while (gameState.value.endEpoch != null) {
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

        if (!gameState.value.isGameOver) {
            Text(
                text = formattedTime,
                color = Color.White,
                fontSize = 144.sp,
                fontFamily = SevenSegmentFontFamily()
            )
            Spacer(modifier = Modifier.height(48.dp))
            Row {
                repeat(playersState.value.players.size) { idx ->
                    val playerNumber = idx + 1
                    val isEliminated = gameState.value.eliminatedPlayers.contains(playerNumber)

                    Box(
                        modifier = Modifier
                            .padding(16.dp)
                            .background(color = if (isEliminated) Color.Transparent else MaterialTheme.colors.primary)
                            .height(200.dp)
                            .width(200.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Image(
                            painter = rememberAsyncImagePainter(model = playersState.value.players[idx].image),
                            contentDescription = null,
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Crop,
                            alpha = if (isEliminated) 0.2f else 1f
                        )
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .background(Color.Black.copy(alpha = 0.1f)),
                            contentAlignment = Alignment.BottomCenter
                        ) {
                            Text(
                                text = "OO${idx + 1}",
                                color = Color.White,
                                fontSize = 24.sp,
                                fontFamily = SevenSegmentFontFamily(),
                                modifier = Modifier.padding(4.dp),
                                style = TextStyle(
                                    shadow = Shadow(
                                        color = MaterialTheme.colors.secondary,
                                        offset = Offset(x = 0f, y = 0f),
                                        blurRadius = 10f
                                    )
                                )
                            )
                        }
                    }
                }
            }
        } else {
            Text(
                text = "GAME OVER",
                color = Color.White,
                fontSize = 96.sp,
                fontFamily = ZenDotsFontFamily()
            )
        }
    }
}
