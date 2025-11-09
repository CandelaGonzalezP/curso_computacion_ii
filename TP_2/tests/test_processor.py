# tests/test_processor.py

import unittest
import base64
import sys
import os
import io
import struct

# --- INICIO: AJUSTE DE RUTA UNIVERSAL ---
# Esto permite que el script se ejecute directamente o como módulo de unittest
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- FIN: AJUSTE DE RUTA UNIVERSAL ---

# Importaciones absolutas desde la raíz del proyecto (TP_2/)
from processor.screenshot import generate_screenshot
from processor.performance import analyze_performance
from processor.image_processor import generate_thumbnails
from common.serialization import serialize_message, deserialize_message, HEADER_SIZE


class TestProcessor(unittest.TestCase):

    def test_01_generate_screenshot(self):
        """Prueba que el screenshot simulado devuelve una cadena base64 válida y no vacía."""
        url = "https://test.com"
        result = generate_screenshot(url)
        
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 100) # Debe ser una cadena base64 lo suficientemente larga
        
        # Intentar decodificar la cadena base64 para verificar su validez
        try:
            decoded_bytes = base64.b64decode(result, validate=True)
            self.assertIsInstance(decoded_bytes, bytes)
        except Exception:
            self.fail("La cadena de screenshot simulada no es un base64 válido.")


    def test_02_analyze_performance(self):
        """Prueba que los datos de rendimiento son generados con la estructura y tipos correctos."""
        url = "https://test.com"
        result = analyze_performance(url)
        
        self.assertIsInstance(result, dict)
        self.assertIn('load_time_ms', result)
        self.assertIn('total_size_kb', result)
        self.assertIn('num_requests', result)
        
        self.assertIsInstance(result['num_requests'], int)
        self.assertTrue(result['num_requests'] > 0)


    def test_03_generate_thumbnails(self):
        """Prueba que se genera una lista de thumbnails en formato base64."""
        url = "https://test.com"
        result = generate_thumbnails(url)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2) # Esperamos 2 thumbnails por la simulación
        
        # Verificar que ambos elementos sean base64 válidos
        for thumb in result:
            self.assertIsInstance(thumb, str)
            self.assertTrue(len(thumb) > 10)
            try:
                base64.b64decode(thumb, validate=True)
            except Exception:
                self.fail("Uno de los thumbnails simulados no es base64.")

    
    def test_04_serialization_protocol(self):
        """Prueba la serialización y deserialización del protocolo de sockets."""
        test_data = {"url": "http://test.com/data", "operation": "screenshot"}
        
        # 1. Serializar
        serialized = serialize_message(test_data)
        self.assertIsInstance(serialized, bytes)
        self.assertTrue(len(serialized) > HEADER_SIZE)

        # 2. Deserializar (Verificar que el dato original se recupera)
        deserialized = deserialize_message(serialized)
        self.assertEqual(deserialized, test_data)

        # 3. Probar longitud (Verificar que el encabezado es correcto)
        (data_len,) = struct.unpack('<I', serialized[:HEADER_SIZE])
        self.assertEqual(data_len, len(serialized) - HEADER_SIZE)


if __name__ == '__main__':
    # Este if permite ejecutar el archivo como script normal para pruebas rápidas
    unittest.main()