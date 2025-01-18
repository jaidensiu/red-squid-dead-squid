package com.example.squid.ui.theme

import androidx.compose.material.Typography
import androidx.compose.runtime.Composable
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import org.jetbrains.compose.resources.Font
import redsquiddeadsquid.composeapp.generated.resources.Res
import redsquiddeadsquid.composeapp.generated.resources.game_of_squids

@Composable
fun SquidFontFamily() = FontFamily(
    Font(Res.font.game_of_squids, FontWeight.Normal)
)

@Composable
fun SquidTypography() = Typography(
    defaultFontFamily = SquidFontFamily()
)
