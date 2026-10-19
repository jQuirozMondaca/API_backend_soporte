from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Solicitud


class SolicitudAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='usuario',
            password='Usuario123!',
        )
        self.other_user = User.objects.create_user(
            username='otro',
            password='Otro123!',
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='Admin123!',
            is_staff=True,
        )
        self.solicitud = Solicitud.objects.create(
            titulo='Equipo sin conexión',
            descripcion='El equipo no logra conectarse a la red.',
            categoria='Redes',
            usuario=self.user,
        )

    def authenticate(self, user):
        self.assertTrue(self.client.login(
            username=user.username,
            password='Admin123!' if user == self.admin else (
                'Otro123!' if user == self.other_user else 'Usuario123!'
            ),
        ))

    def test_usuario_autenticado_crea_solicitud_y_asigna_propietario(self):
        self.authenticate(self.user)

        response = self.client.post('/api/solicitudes/', {
            'titulo': 'Nuevo equipo',
            'descripcion': 'Se necesita revisar el equipo.',
            'categoria': 'Hardware',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['usuario'], self.user.username)
        self.assertEqual(response.data['estado'], 'Pendiente')

    def test_usuario_solo_consulta_sus_solicitudes(self):
        Solicitud.objects.create(
            titulo='Solicitud ajena',
            descripcion='No debe aparecer.',
            categoria='Software',
            usuario=self.other_user,
        )
        self.authenticate(self.user)

        response = self.client.get('/api/solicitudes/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.solicitud.id)

    def test_usuario_no_consulta_solicitud_ajena(self):
        self.authenticate(self.other_user)

        response = self.client.get(
            f'/api/solicitudes/{self.solicitud.id}/',
        )

        self.assertEqual(response.status_code, 404)

    def test_usuario_no_puede_cambiar_estado(self):
        self.authenticate(self.user)

        response = self.client.patch(
            f'/api/solicitudes/{self.solicitud.id}/',
            {'estado': 'Resuelto'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, 'Pendiente')

    def test_administrador_puede_cambiar_estado(self):
        self.authenticate(self.admin)

        response = self.client.patch(
            f'/api/solicitudes/{self.solicitud.id}/',
            {'estado': 'Resuelto'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, 'Resuelto')

    def test_put_actualiza_campos_permitidos_y_protege_campos_automaticos(self):
        self.authenticate(self.user)
        original_fecha = self.solicitud.fecha_creacion

        response = self.client.put(
            f'/api/solicitudes/{self.solicitud.id}/',
            {
                'titulo': 'Equipo actualizado',
                'descripcion': 'La descripción fue actualizada.',
                'categoria': 'Hardware',
                'usuario': self.other_user.username,
                'fecha_creacion': '2000-01-01 00:00:00',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.titulo, 'Equipo actualizado')
        self.assertEqual(self.solicitud.usuario, self.user)
        self.assertEqual(self.solicitud.fecha_creacion, original_fecha)

    def test_datos_invalidos_responden_400(self):
        self.authenticate(self.user)

        response = self.client.post('/api/solicitudes/', {
            'titulo': 'Categoría inválida',
            'descripcion': 'Descripción',
            'categoria': 'Inválida',
        }, format='json')

        self.assertEqual(response.status_code, 400)

    def test_usuario_normal_no_puede_eliminar(self):
        self.authenticate(self.user)

        response = self.client.delete(
            f'/api/solicitudes/{self.solicitud.id}/',
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Solicitud.objects.filter(id=self.solicitud.id).exists())

    def test_administrador_puede_eliminar(self):
        self.authenticate(self.admin)

        response = self.client.delete(
            f'/api/solicitudes/{self.solicitud.id}/',
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Solicitud.objects.filter(id=self.solicitud.id).exists())

    def test_cliente_sin_autenticacion_es_rechazado(self):
        response = self.client.get('/api/solicitudes/')

        self.assertIn(response.status_code, (401, 403))

    def test_login_y_logout_invalidan_la_sesion(self):
        response = self.client.post('/api/auth/login/', {
            'username': self.user.username,
            'password': 'Usuario123!',
        }, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/solicitudes/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/api/auth/logout/', format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/solicitudes/')
        self.assertIn(response.status_code, (401, 403))

    def test_escritura_sin_csrf_es_rechazada(self):
        csrf_client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(csrf_client.login(
            username=self.user.username,
            password='Usuario123!',
        ))

        response = csrf_client.post('/api/solicitudes/', {
            'titulo': 'Sin CSRF',
            'descripcion': 'Debe rechazarse.',
            'categoria': 'Software',
        }, format='json')

        self.assertEqual(response.status_code, 403)
