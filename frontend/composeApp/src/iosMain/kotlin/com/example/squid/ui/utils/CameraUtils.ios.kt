@file:OptIn(BetaInteropApi::class, ExperimentalForeignApi::class)

package com.example.squid.ui.utils

import androidx.compose.runtime.Composable
import androidx.compose.ui.interop.LocalUIViewController
import kotlinx.cinterop.BetaInteropApi
import kotlinx.cinterop.ExperimentalForeignApi
import kotlinx.cinterop.ObjCAction
import kotlinx.cinterop.addressOf
import kotlinx.cinterop.usePinned
import platform.Foundation.NSData
import platform.Foundation.NSURL
import platform.Foundation.dataWithContentsOfURL
import platform.UIKit.UIImagePickerController
import platform.UIKit.UIImagePickerControllerDelegateProtocol
import platform.UIKit.UIImagePickerControllerReferenceURL
import platform.UIKit.UIImagePickerControllerSourceType
import platform.UIKit.UINavigationControllerDelegateProtocol
import platform.UIKit.UIViewController
import platform.darwin.NSObject
import platform.posix.memcpy

@Composable
actual fun rememberCameraLauncher(onImageCaptured: (ByteArray) -> Unit): () -> Unit {
    val viewController = LocalUIViewController.current

    return {
        viewController.launchCamera { imageUri ->
            val imageData = NSData.dataWithContentsOfURL(imageUri)
            val imageBytes = imageData?.toByteArray() ?: ByteArray(0)
            onImageCaptured(imageBytes)
        }
    }
}

private fun NSData.toByteArray(): ByteArray {
    val bytes = ByteArray(length.toInt())
    bytes.usePinned {
        memcpy(it.addressOf(0), bytes, length)
    }
    return bytes
}

class CameraDelegate(
    private val onImageCaptured: (NSURL) -> Unit
) : NSObject(), UIImagePickerControllerDelegateProtocol, UINavigationControllerDelegateProtocol {
    @ObjCAction
    fun imagePickerController(
        picker: UIImagePickerController,
        didFinishPickingMediaWithInfo: Map<Any?, *>?
    ) {
        val imageUri =
            didFinishPickingMediaWithInfo?.get(UIImagePickerControllerReferenceURL) as? NSURL
        imageUri?.let { onImageCaptured(it) }
        picker.dismissViewControllerAnimated(true, null)
    }

    @ObjCAction
    override fun imagePickerControllerDidCancel(picker: UIImagePickerController) {
        picker.dismissViewControllerAnimated(true, null)
    }
}

fun UIViewController.launchCamera(onImageCaptured: (NSURL) -> Unit) {
    val picker = UIImagePickerController()
    picker.sourceType = UIImagePickerControllerSourceType.UIImagePickerControllerSourceTypeCamera
    picker.delegate = CameraDelegate(onImageCaptured)
    presentViewController(picker, animated = true, completion = null)
}
