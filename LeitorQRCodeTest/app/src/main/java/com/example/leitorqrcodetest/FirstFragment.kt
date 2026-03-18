package com.example.leitorqrcodetest
import android.util.Log
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.activity.result.ActivityResultCallback
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanIntentResult
import com.journeyapps.barcodescanner.ScanOptions

import androidx.activity.result.contract.ActivityResultContracts
import androidx.fragment.app.Fragment
import com.example.leitorqrcodetest.databinding.FragmentFirstBinding
import com.google.zxing.BarcodeFormat
import com.journeyapps.barcodescanner.*

/**
 * A simple [Fragment] subclass as the default destination in the navigation.
 */
class FirstFragment : Fragment() {

    private var _binding: FragmentFirstBinding? = null

    // This property is only valid between onCreateView and
    // onDestroyView.
    private val binding get() = _binding!!

    // Scanner contínuo
    private lateinit var barcodeView: DecoratedBarcodeView
    private var lastText: String? = null

    /*// Register the launcher and result handler
    private val barcodeLauncher = registerForActivityResult<ScanOptions?, ScanIntentResult?>(
        ScanContract(),
        ActivityResultCallback { result: ScanIntentResult? ->
            if (result!!.getContents() == null) {
                Toast.makeText(requireContext(), "Cancelled", Toast.LENGTH_LONG).show()
            } else {
                Toast.makeText(
                    requireContext(),
                    "Scanned: " + result.getContents(),
                    Toast.LENGTH_LONG
                ).show()
                binding.textoLidoTextView.text = result.contents
            }
        })*/

    // Scanner em nova tela
    private val barcodeLauncher =
        registerForActivityResult(ScanContract()) { result: ScanIntentResult ->

            if (result.contents == null) {
                Toast.makeText(requireContext(), "Leitura cancelada", Toast.LENGTH_LONG).show()
            } else {

                val text = result.contents

                Toast.makeText(
                    requireContext(),
                    "Scanned: $text",
                    Toast.LENGTH_LONG
                ).show()

                binding.textoLidoTextView.text = text
            }
        }

    // Launch
    fun onButtonClick() {
        val options = ScanOptions()
        options.setDesiredBarcodeFormats(ScanOptions.QR_CODE)
        options.setPrompt("Ler qrcode...")
        options.setCameraId(0) // Use a specific camera of the device
        options.setBeepEnabled(true)
        //options.setBarcodeImageEnabled(true)
        barcodeLauncher.launch(options)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {

        _binding = FragmentFirstBinding.inflate(inflater, container, false)

        configurarScanner()

        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.lerQRCodeButton.setOnClickListener {
            abrirScannerTelaCheia()
        }
        //binding.lerQRCodeButton.setOnClickListener {
        //    onButtonClick()
        //}
    }

    private fun configurarScanner() {

        barcodeView = binding.barcodeView

        val formats = listOf(
            BarcodeFormat.QR_CODE,
            BarcodeFormat.CODE_39
        )

        barcodeView.barcodeView.decoderFactory = DefaultDecoderFactory(formats)
        val cameraSettings = barcodeView.barcodeView.cameraSettings
        //1 ou 0 para camera frontal
        cameraSettings.requestedCameraId = 1

        barcodeView.decodeContinuous(scannerCallback)
    }

    // Callback da leitura contínua
    private val scannerCallback = BarcodeCallback { result ->

        val text = result.text ?: return@BarcodeCallback

        // Evita leituras duplicadas
        if (text == lastText) return@BarcodeCallback

        lastText = text

        Log.d("QRAPP", "QR lido: $text")

        Toast.makeText(
            requireContext(),
            "QR lido: $text",
            Toast.LENGTH_SHORT
        ).show()

        binding.textoLidoTextView.text = text
    }

    // Scanner em nova Activity
    private fun abrirScannerTelaCheia() {

        val options = ScanOptions().apply {
            setDesiredBarcodeFormats(ScanOptions.QR_CODE)
            setPrompt("Ler QR Code...")
            setBeepEnabled(false)
            setCameraId(0)
        }

        barcodeLauncher.launch(options)
    }

    override fun onResume() {
        super.onResume()
        barcodeView.resume()
    }

    override fun onPause() {
        super.onPause()
        barcodeView.pause()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        barcodeView.pause()
        _binding = null
    }
}


//.\AppData\Local\Android\Sdk\emulator\emulator.exe -avd Pixel_8 -feature -Vulkan -gpu host -no-snapshot -no-boot-anim -memory 2048 -scale 0.7