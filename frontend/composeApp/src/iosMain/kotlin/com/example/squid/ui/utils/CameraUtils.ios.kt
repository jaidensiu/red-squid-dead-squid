@file:OptIn(ExperimentalForeignApi::class, BetaInteropApi::class)

package com.example.squid.ui.utils

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import kotlinx.cinterop.BetaInteropApi
import kotlinx.cinterop.ExperimentalForeignApi
import kotlinx.cinterop.ObjCAction
import kotlinx.cinterop.refTo
import kotlinx.cinterop.usePinned
import platform.Foundation.NSData
import platform.Foundation.NSDictionary
import platform.UIKit.UIApplication
import platform.UIKit.UIImage
import platform.UIKit.UIImageJPEGRepresentation
import platform.UIKit.UIImagePickerController
import platform.UIKit.UIImagePickerControllerDelegateProtocol
import platform.UIKit.UIImagePickerControllerOriginalImage
import platform.UIKit.UIImagePickerControllerSourceType
import platform.UIKit.UINavigationControllerDelegateProtocol
import platform.UIKit.UIViewController
import platform.darwin.NSObject
import platform.posix.memcpy

@Composable
actual fun rememberCameraLauncher(onImageCaptured: (ByteArray) -> Unit): () -> Unit {
    val imagePicker = remember { UIImagePickerController() }
    val delegate = remember { ImagePickerDelegate(onImageCaptured) }

    imagePicker.delegate = delegate
    imagePicker.sourceType =
        UIImagePickerControllerSourceType.UIImagePickerControllerSourceTypeCamera

    return {
        val topViewController = getTopViewController()
        topViewController?.presentViewController(imagePicker, animated = true, completion = null)
    }
}

fun getTopViewController(): UIViewController? {
    val keyWindow = UIApplication.sharedApplication.keyWindow
    var topViewController = keyWindow?.rootViewController
    while (topViewController?.presentedViewController != null) {
        topViewController = topViewController.presentedViewController
    }
    return topViewController
}

class ImagePickerDelegate(
    private val onImageCaptured: (ByteArray) -> Unit
) : NSObject(), UIImagePickerControllerDelegateProtocol, UINavigationControllerDelegateProtocol {
    @ObjCAction
    fun imagePickerController(
        picker: UIImagePickerController,
        didFinishPickingMediaWithInfo: NSDictionary
    ) {
        val image = didFinishPickingMediaWithInfo
            .objectForKey(UIImagePickerControllerOriginalImage) as? UIImage
        val imageData = image?.let { UIImageJPEGRepresentation(it, 1.0) }
        val byteArray = imageData?.toByteArray() ?: ByteArray(0)
        onImageCaptured(byteArray)
        picker.dismissViewControllerAnimated(true, completion = null)
    }

    @ObjCAction
    override fun imagePickerControllerDidCancel(picker: UIImagePickerController) {
        picker.dismissViewControllerAnimated(true, completion = null)
    }
}

fun NSData.toByteArray(): ByteArray {
    val bytes = ByteArray(this.length.toInt())
    this.usePinned { memcpy(bytes.refTo(0), this.bytes, this.length) }
    return bytes
}
