package com.example.squid.ui.welcome

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.Button
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import org.jetbrains.compose.resources.painterResource
import redsquiddeadsquid.composeapp.generated.resources.Res
import redsquiddeadsquid.composeapp.generated.resources.red_squid_dead_squid_logo

@Composable
fun WelcomeScreen(onRegisterPlayers: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Image(
            painter = painterResource(Res.drawable.red_squid_dead_squid_logo),
            contentDescription = null
        )
        Button(
            onClick = onRegisterPlayers,
            shape = RoundedCornerShape(24.dp)
        ) {
            Text(text = "Register Players")
        }
    }
}
