package com.example.leitorqrcodetest

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.fragment.app.Fragment
import com.example.leitorqrcodetest.databinding.FragmentFirstBinding
import com.google.zxing.BarcodeFormat
import com.journeyapps.barcodescanner.*

class FirstFragment : Fragment() {

    private var _binding: FragmentFirstBinding? = null
    private val binding get() = _binding!!

    // Scanner contínuo
    private lateinit var barcodeView: DecoratedBarcodeView
    private var lastText: String? = null

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