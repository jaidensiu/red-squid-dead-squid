package com.example.squid.ui.utils

import androidx.compose.runtime.Composable

@Composable
expect fun rememberCameraLauncher(onImageCaptured: (ByteArray) -> Unit): () -> Unit
