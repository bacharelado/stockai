import unittest

from app.plans import PLANOS, limite_atingido, obter_plano


class PlanosTestCase(unittest.TestCase):
    def test_plano_desconhecido_volta_para_gratis(self):
        self.assertEqual(obter_plano("nao-existe").codigo, "gratuito")
        self.assertEqual(obter_plano(None).codigo, "gratuito")

    def test_limites_dos_planos(self):
        self.assertEqual(PLANOS["gratuito"].max_produtos, 50)
        self.assertEqual(PLANOS["gratuito"].max_usuarios, 2)
        self.assertEqual(PLANOS["pro"].max_produtos, 500)
        self.assertEqual(PLANOS["pro"].max_usuarios, 10)
        self.assertIsNone(PLANOS["empresa"].max_produtos)
        self.assertIsNone(PLANOS["empresa"].max_usuarios)

    def test_limite_atingido(self):
        self.assertFalse(limite_atingido(49, 50))
        self.assertTrue(limite_atingido(50, 50))
        self.assertTrue(limite_atingido(1000, None)) is False


if __name__ == "__main__":
    unittest.main()
