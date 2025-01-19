package com.example.squid.app

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.navigation
import androidx.navigation.compose.rememberNavController
import com.example.squid.ui.players.PlayersScreen
import com.example.squid.ui.theme.SquidTheme
import com.example.squid.ui.landing.LandingScreen
import com.example.squid.ui.players.PlayersViewModel
import org.koin.compose.viewmodel.koinViewModel

@Composable
fun App() {
    val navController = rememberNavController()

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
                    val viewModel = koinViewModel<PlayersViewModel>()

                    PlayersScreen(
                        viewModel = viewModel
                    )
                }
            }
        }
    }
}
