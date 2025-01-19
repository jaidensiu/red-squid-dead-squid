package com.example.squid.ui.utils

import android.app.Activity
import android.content.Context
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.FileProvider
import java.io.File

@Composable
actual fun rememberCameraLauncher(onImageCaptured: (ByteArray) -> Unit): () -> Unit {
    val context = LocalContext.current
    val imageUri = remember { createImageUri(context) }

    val launcher = rememberLauncherForActivityResult(ActivityResultContracts.TakePicture()) { success ->
        if (success) {
            val imageBytes = imageUri.toByteArray(context)
            onImageCaptured(imageBytes)
        }
    }

    return {
        launcher.launch(imageUri)
    }
}

private fun createImageUri(context: Context): Uri {
    val imageFile = File(context.cacheDir, "captured_image.jpg")
    return FileProvider.getUriForFile(context, "${context.packageName}.provider", imageFile)
}

private fun Uri.toByteArray(context: Context): ByteArray {
    return context.contentResolver.openInputStream(this)?.readBytes() ?: ByteArray(0)
}
