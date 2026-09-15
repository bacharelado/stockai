import unittest
from types import SimpleNamespace

from app.services import produto_to_out


class SecuritySerializationTestCase(unittest.TestCase):
    def setUp(self):
        self.product = SimpleNamespace(
            id=7,
            nome="Café especial",
            categoria="Bebidas",
            codigo_barras="7891234567890",
            preco=24.90,
            custo=12.50,
            estoque_atual=8,
            estoque_minimo=5,
        )

    def test_operator_payload_omits_sensitive_fields(self):
        payload = produto_to_out(self.product, incluir_campos_sensiveis=False)

        self.assertNotIn("custo", payload)
        self.assertNotIn("margem", payload)
        self.assertNotIn("codigo_barras", payload)
        self.assertEqual(payload["preco"], 24.90)

    def test_management_payload_keeps_sensitive_fields(self):
        payload = produto_to_out(self.product, incluir_campos_sensiveis=True)

        self.assertEqual(payload["custo"], 12.50)
        self.assertEqual(payload["codigo_barras"], "7891234567890")
        self.assertEqual(payload["margem"], 49.8)


if __name__ == "__main__":
    unittest.main()
