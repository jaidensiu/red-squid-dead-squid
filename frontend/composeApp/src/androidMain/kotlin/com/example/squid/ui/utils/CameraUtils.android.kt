package com.example.squid.ui.utils

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.FileProvider
import java.io.ByteArrayOutputStream
import java.io.File

@Composable
actual fun rememberCameraLauncher(onImageCaptured: (ByteArray) -> Unit): () -> Unit {
    val context = LocalContext.current
    val imageUri = remember { createImageUri(context) }

    val launcher = rememberLauncherForActivityResult(ActivityResultContracts.TakePicture()) { success ->
        if (success) {
            val imageBytes = imageUri.toCompressedByteArray(context, quality = 20)
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

private fun Uri.toCompressedByteArray(context: Context, quality: Int): ByteArray {
    val inputStream = context.contentResolver.openInputStream(this)
    val bitmap = BitmapFactory.decodeStream(inputStream)
    val outputStream = ByteArrayOutputStream()
    bitmap.compress(Bitmap.CompressFormat.JPEG, quality, outputStream)
    return outputStream.toByteArray()
}
