package com.example.squid.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material.darkColors
import androidx.compose.material.lightColors
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val LightTextFieldPlaceholder = Color(color = 0xFFB0B0B0)
val DarkTextFieldPlaceholder = Color(color = 0xFF424242)

@Composable
fun TextFieldPlaceHolder() = if (isSystemInDarkTheme()) DarkTextFieldPlaceholder else LightTextFieldPlaceholder

val Primary = Color(color = 0xFFFF367A) // the pink one
val PrimaryVariant = Color(color = 0xFFFFA000)
val Secondary = Color(color = 0xFF35DAC3) // the green one
val Background = Color(color = 0xFF0E051B) // the background
val Surface = Color(color = 0xFFFCFBF4)
val OnPrimary = Color(color = 0xFF000000)
val OnSecondary = Color(color = 0xFF000000)
val OnBackground = Color(color = 0xFF000000)
val OnSurface = Color(color = 0xFF000000)

val LightColorPalette = lightColors(
    primary = Primary,
    primaryVariant = PrimaryVariant,
    secondary = Secondary,
    background = Background,
    surface = Surface,
    onPrimary = OnPrimary,
    onSecondary = OnSecondary,
    onBackground = OnBackground,
    onSurface = OnSurface
)

val DarkColorPalette = darkColors(
    primary = Primary,
    primaryVariant = PrimaryVariant,
    secondary = Secondary,
    background = Background,
    surface = Surface,
    onPrimary = OnPrimary,
    onSecondary = OnSecondary,
    onBackground = OnBackground,
    onSurface = OnSurface
)
