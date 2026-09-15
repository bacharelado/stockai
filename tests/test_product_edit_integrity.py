import unittest

from pydantic import ValidationError

from app.schemas import ProdutoUpdate


class ProductEditIntegrityTestCase(unittest.TestCase):
    def test_update_requires_cost_and_barcode_fields(self):
        with self.assertRaises(ValidationError):
            ProdutoUpdate(
                nome="Café especial",
                categoria="Bebidas",
                preco=24.90,
                estoque_minimo=5,
            )

    def test_update_accepts_existing_optional_barcode_as_empty(self):
        produto = ProdutoUpdate(
            nome="Café especial",
            categoria="Bebidas",
            preco=24.90,
            custo=12.50,
            codigo_barras=None,
            estoque_minimo=5,
        )

        self.assertEqual(produto.custo, 12.50)
        self.assertIsNone(produto.codigo_barras)

    def test_update_preserves_barcode_value_in_payload(self):
        produto = ProdutoUpdate(
            nome="Café especial",
            categoria="Bebidas",
            preco=24.90,
            custo=12.50,
            codigo_barras="7891234567890",
            estoque_minimo=5,
        )

        self.assertEqual(produto.codigo_barras, "7891234567890")


if __name__ == "__main__":
    unittest.main()
