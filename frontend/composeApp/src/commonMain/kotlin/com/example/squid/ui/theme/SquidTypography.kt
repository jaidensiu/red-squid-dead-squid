package com.example.squid.ui.theme

import androidx.compose.material.Typography
import androidx.compose.runtime.Composable
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import org.jetbrains.compose.resources.Font
import redsquiddeadsquid.composeapp.generated.resources.Res
import redsquiddeadsquid.composeapp.generated.resources.SplineSansMono_Bold
import redsquiddeadsquid.composeapp.generated.resources.SplineSansMono_Medium
import redsquiddeadsquid.composeapp.generated.resources.SplineSansMono_Regular
import redsquiddeadsquid.composeapp.generated.resources.ZenDots_Regular
import redsquiddeadsquid.composeapp.generated.resources._7segment
import redsquiddeadsquid.composeapp.generated.resources.game_of_squids

// Font families

@Composable
fun SquidFontFamily() = FontFamily(
    Font(Res.font.game_of_squids, FontWeight.Normal)
)

@Composable
fun SplineSansMonoFamily() = FontFamily(
    Font(Res.font.SplineSansMono_Regular, FontWeight.Normal),
    Font(Res.font.SplineSansMono_Medium, FontWeight.Medium),
    Font(Res.font.SplineSansMono_Bold, FontWeight.Bold)
)

@Composable
fun ZenDotsFontFamily() = FontFamily(
    Font(Res.font.ZenDots_Regular)
)

@Composable
fun SevenSegmentFontFamily() = FontFamily(
    Font(Res.font._7segment)
)

// Typographies

@Composable
fun SplineSansMonoTypography() = Typography(defaultFontFamily = SplineSansMonoFamily())
