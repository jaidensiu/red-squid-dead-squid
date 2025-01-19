package com.example.squid.ui.countdown

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.squid.ui.theme.SevenSegmentFontFamily
import com.example.squid.ui.theme.ZenDotsFontFamily
import kotlinx.coroutines.delay

@Composable
fun CountdownScreen(onFinish: () -> Unit) {
    var countdown by remember { mutableStateOf(value = 5) }

    LaunchedEffect(Unit) {
        while (countdown > 0) {
            delay(timeMillis = 1000L)
            countdown--
        }
        onFinish()
    }

    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "GAME IS STARTING IN...",
            color = Color.White,
            fontSize = 48.sp,
            fontFamily = ZenDotsFontFamily()
        )
        Spacer(modifier = Modifier.height(48.dp))
        Text(
            text = countdown.toString(),
            color = Color.White,
            fontSize = 144.sp,
            fontFamily = SevenSegmentFontFamily(),
            style = TextStyle(
                shadow = Shadow(
                    color = MaterialTheme.colors.primary,
                    offset = Offset(x = 0f, y = 0f),
                    blurRadius = 10f
                )
            )
        )
    }
}
