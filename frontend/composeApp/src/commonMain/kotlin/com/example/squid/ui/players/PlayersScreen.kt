package com.example.squid.ui.players

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil3.compose.rememberAsyncImagePainter
import com.example.squid.ui.theme.ZenDotsFontFamily
import com.example.squid.ui.utils.rememberCameraLauncher
import org.jetbrains.compose.resources.painterResource
import org.koin.compose.viewmodel.koinViewModel
import redsquiddeadsquid.composeapp.generated.resources.Res
import redsquiddeadsquid.composeapp.generated.resources.plus

@Composable
fun PlayersScreen(
    viewModel: PlayersViewModel = koinViewModel()
) {
    val state = viewModel.state.collectAsState()
    val launchCamera = rememberCameraLauncher { viewModel.onAddPlayer(it) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "PLAYERS",
            color = Color.White,
            fontSize = 48.sp,
            fontFamily = ZenDotsFontFamily()
        )
        Spacer(modifier = Modifier.height(48.dp))
        Row {
            repeat(PlayersViewModel.NUM_PLAYERS) { idx ->
                Box(
                    modifier = Modifier
                        .padding(16.dp)
                        .background(color = MaterialTheme.colors.primary)
                        .height(100.dp)
                        .width(100.dp)
                        .clickable(
                            enabled = idx <= state.value.players.size,
                            onClick = {
                                launchCamera()
                            }
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    when {
                        idx < state.value.players.size && idx >= 0 -> {
                            Image(
                                painter = rememberAsyncImagePainter(model = state.value.players[idx].image),
                                contentDescription = null
                            )
                        }

                        idx == state.value.players.size -> {
                            Image(
                                painter = painterResource(Res.drawable.plus),
                                contentDescription = null
                            )
                        }
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(48.dp))
        Text(
            text = "${state.value.players.size} players registered. Click on the \"+\" to add a player.",
            color = Color.White
        )
    }
}
