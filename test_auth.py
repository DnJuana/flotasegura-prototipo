"""
Pruebas del módulo auth.py
FlotaSegura

Responsable:
Yerko Morales
"""

import unittest

from auth import (
    USERS,
    InvalidCredentialsError,
    InvalidTokenError,
    PermissionDeniedError,
    generate_token,
    gestionar_mantenciones,
    hash_password,
    login,
    require_role,
    validate_token,
    verify_password
)


class TestAuthFlotaSegura(unittest.TestCase):

    # --------------------------------------------------------
    # TEST 1
    # --------------------------------------------------------

    def test_hash_no_guarda_password_plano(self):

        password = "Flota123"

        result = hash_password(password)

        self.assertNotEqual(
            result["hash"],
            password
        )

    # --------------------------------------------------------
    # TEST 2
    # --------------------------------------------------------

    def test_password_correcta(self):

        password = "Prueba123"

        result = hash_password(password)

        resultado = verify_password(
            password,
            result["salt"],
            result["hash"]
        )

        self.assertTrue(resultado)

    # --------------------------------------------------------
    # TEST 3
    # --------------------------------------------------------

    def test_password_incorrecta(self):

        result = hash_password(
            "PasswordCorrecta"
        )

        resultado = verify_password(
            "PasswordMala",
            result["salt"],
            result["hash"]
        )

        self.assertFalse(resultado)

    # --------------------------------------------------------
    # TEST 4
    # --------------------------------------------------------

    def test_login_correcto(self):

        token = login(
            "jefe1",
            "Flota123"
        )

        self.assertIsInstance(
            token,
            str
        )

        self.assertGreater(
            len(token),
            20
        )

    # --------------------------------------------------------
    # TEST 5
    # --------------------------------------------------------

    def test_login_password_incorrecta(self):

        with self.assertRaises(
            InvalidCredentialsError
        ):

            login(
                "jefe1",
                "ClaveIncorrecta"
            )

    # --------------------------------------------------------
    # TEST 6
    # --------------------------------------------------------

    def test_usuario_inexistente(self):

        with self.assertRaises(
            InvalidCredentialsError
        ):

            login(
                "usuario_fake",
                "123456"
            )

    # --------------------------------------------------------
    # TEST 7
    # --------------------------------------------------------

    def test_campos_login_vacios(self):

        with self.assertRaises(
            InvalidCredentialsError
        ):

            login(
                "",
                ""
            )

    # --------------------------------------------------------
    # TEST 8
    # --------------------------------------------------------

    def test_token_valido(self):

        token = login(
            "jefe1",
            "Flota123"
        )

        payload = validate_token(token)

        self.assertEqual(
            payload["username"],
            "jefe1"
        )

        self.assertEqual(
            payload["role"],
            "jefe_flota"
        )

    # --------------------------------------------------------
    # TEST 9
    # --------------------------------------------------------

    def test_token_manipulado(self):

        token = login(
            "jefe1",
            "Flota123"
        )

        token_modificado = token[:-5] + "AAAAA"

        with self.assertRaises(
            InvalidTokenError
        ):

            validate_token(
                token_modificado
            )

    # --------------------------------------------------------
    # TEST 10
    # --------------------------------------------------------

    def test_token_expirado(self):

        token = generate_token(
            "jefe1",
            "jefe_flota",
            duration_seconds=-1
        )

        with self.assertRaises(
            InvalidTokenError
        ):

            validate_token(token)

    # --------------------------------------------------------
    # TEST 11
    # --------------------------------------------------------

    def test_conductor_no_puede_gestionar_mantenciones(self):

        token = login(
            "conductor1",
            "Camion123"
        )

        with self.assertRaises(
            PermissionDeniedError
        ):

            gestionar_mantenciones(token)

    # --------------------------------------------------------
    # TEST 12
    # --------------------------------------------------------

    def test_jefe_puede_gestionar_mantenciones(self):

        token = login(
            "jefe1",
            "Flota123"
        )

        resultado = gestionar_mantenciones(
            token
        )

        self.assertEqual(
            resultado,
            "Acceso concedido a gestión de mantenciones."
        )

    # --------------------------------------------------------
    # TEST 13
    # --------------------------------------------------------

    def test_gerente_no_puede_gestionar_mantenciones(self):

        token = login(
            "gerente1",
            "Gerencia123"
        )

        with self.assertRaises(
            PermissionDeniedError
        ):

            gestionar_mantenciones(token)

    # --------------------------------------------------------
    # TEST 14
    # --------------------------------------------------------

    def test_require_role_jefe(self):

        token = login(
            "jefe1",
            "Flota123"
        )

        payload = require_role(
            token,
            ["jefe_flota"]
        )

        self.assertEqual(
            payload["role"],
            "jefe_flota"
        )

    # --------------------------------------------------------
    # TEST 15
    # --------------------------------------------------------

    def test_password_no_esta_guardada_en_texto_plano(self):

        usuario = USERS["jefe1"]

        self.assertNotEqual(
            usuario["password_hash"],
            "Flota123"
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )