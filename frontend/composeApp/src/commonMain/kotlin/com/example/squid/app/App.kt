package com.example.squid.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.rememberCoroutineScope
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.navigation
import androidx.navigation.compose.rememberNavController
import com.example.squid.data.GameWebSocket
import com.example.squid.data.HttpClientFactory
import com.example.squid.ui.countdown.CountdownScreen
import com.example.squid.ui.game.GameScreen
import com.example.squid.ui.game.GameViewModel
import com.example.squid.ui.landing.LandingScreen
import com.example.squid.ui.players.PlayersScreen
import com.example.squid.ui.players.PlayersViewModel
import com.example.squid.ui.theme.SquidTheme
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import org.koin.compose.viewmodel.koinViewModel

@Composable
fun App() {
    val navController = rememberNavController()
    val gameViewModelViewModel = GameViewModel()
    val httpClient = HttpClientFactory.create()
    val webSocket = GameWebSocket(
        viewModel = gameViewModelViewModel,
        client = httpClient
    )
    val coroutineScope = rememberCoroutineScope()
    val playersViewModel = koinViewModel<PlayersViewModel>()

    LaunchedEffect(Unit) {
        webSocket.connect()
    }

    SquidTheme {
        NavHost(
            navController = navController,
            startDestination = Route.RouteGraph
        ) {
            navigation<Route.RouteGraph>(startDestination = Route.Landing) {
                composable<Route.Landing> {
                    LandingScreen(
                        onRegisterPlayers = { navController.navigate(route = Route.Players) }
                    )
                }

                composable<Route.Players> {
                    PlayersScreen(
                        viewModel = playersViewModel,
                        onStartGame = {
                            coroutineScope.launch {
                                webSocket.sendPlayers(playersViewModel.state.value.players)
                                delay(timeMillis = 5000L)
                            }
                            navController.navigate(route = Route.Countdown)
                        }
                    )
                }

                composable<Route.Countdown> {
                    CountdownScreen(onFinish = { navController.navigate(route = Route.Game) })
                }

                composable<Route.Game> {
                    GameScreen(
                        gameViewModel = gameViewModelViewModel,
                        playersViewModel = playersViewModel
                    )
                }
            }
        }
    }
}
