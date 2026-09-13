import unittest

from fastapi import HTTPException

from app import auth_signup


class SignupSecurityTestCase(unittest.TestCase):
    def setUp(self):
        with auth_signup._signup_lock:
            auth_signup._signup_attempts.clear()

    def test_bloqueia_mais_de_cinco_tentativas_na_mesma_chave(self):
        chave = "empresa-teste::admin"
        for _ in range(auth_signup.SIGNUP_RATE_MAX_ATTEMPTS):
            auth_signup._registrar_tentativa_signup(chave)

        with self.assertRaises(HTTPException) as contexto:
            auth_signup._registrar_tentativa_signup(chave)

        self.assertEqual(contexto.exception.status_code, 429)

    def test_limpar_tentativas_libera_nova_tentativa(self):
        chave = "empresa-teste::admin"
        for _ in range(auth_signup.SIGNUP_RATE_MAX_ATTEMPTS):
            auth_signup._registrar_tentativa_signup(chave)

        auth_signup._limpar_tentativas_signup(chave)
        auth_signup._registrar_tentativa_signup(chave)

        self.assertEqual(len(auth_signup._signup_attempts[chave]), 1)


if __name__ == "__main__":
    unittest.main()
