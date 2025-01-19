package com.example.squid

import androidx.compose.ui.window.ComposeUIViewController
import com.example.squid.app.App
import com.example.squid.di.KoinInitializer.initKoin

fun MainViewController() = ComposeUIViewController(configure = { initKoin() }) {
    App()
}
