# Sistema de Gestión de Solicitudes de Soporte Técnico

API RESTful desarrollada con Python, Django y Django REST Framework para registrar,
consultar, actualizar y eliminar solicitudes de soporte técnico. La autenticación se
realiza mediante sesiones de Django y los permisos se aplican según el perfil del
usuario.

## 1. Requisitos previos

- Python 3.10 o superior.
- PowerShell, Visual Studio Code o una terminal equivalente.
- Postman (opcional, para pruebas manuales).

## 2. Instalación y ejecución

Desde la raíz del proyecto:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

La API queda disponible en `http://127.0.0.1:8000/`.

Para crear los usuarios de prueba solicitados, ejecutar:

```powershell
python manage.py shell
```

Luego pegar el siguiente código en el shell:

```python
from django.contrib.auth.models import User

# Administrador
if not User.objects.filter(username='admin_soporte').exists():
    User.objects.create_superuser(
        'admin_soporte',
        'admin@inacap.cl',
        'Admin123*',
    )

# Usuario normal 1
if not User.objects.filter(username='juan_perez').exists():
    User.objects.create_user(
        'juan_perez',
        'juan@inacap.cl',
        'User123*',
    )

# Usuario normal 2, utilizado para probar el aislamiento de solicitudes
if not User.objects.filter(username='maria_lopez').exists():
    User.objects.create_user(
        'maria_lopez',
        'maria@inacap.cl',
        'User123*',
    )

print('Usuarios de prueba creados exitosamente.')
exit()
```

El panel administrativo está disponible en `http://127.0.0.1:8000/admin/`.

## 3. Usuarios y perfiles

La API usa el modelo de usuarios incorporado de Django:

- **Usuario normal:** crea solicitudes, consulta solo las propias y puede modificar
  título, descripción y categoría. No puede cambiar el estado ni eliminar.
- **Administrador:** usuario con `is_staff=True`; puede consultar todas las
  solicitudes, modificar cualquier campo y eliminar registros.

Usuarios de prueba:

| Usuario         | Correo            | Contraseña  | Perfil         |
| --------------- | ----------------- | ----------- | -------------- |
| `admin_soporte` | `admin@inacap.cl` | `Admin123*` | Administrador  |
| `juan_perez`    | `juan@inacap.cl`  | `User123*`  | Usuario normal |
| `maria_lopez`   | `maria@inacap.cl` | `User123*`  | Usuario normal |

`juan_perez` y `maria_lopez` permiten verificar que cada usuario solo pueda
consultar y modificar sus propias solicitudes. Estas credenciales son únicamente
para desarrollo y evaluación local; no deben reutilizarse en producción.

## 4. Endpoints

La URL base es `http://127.0.0.1:8000/api/`.

| Método | Endpoint             | Descripción                                |
| ------ | -------------------- | ------------------------------------------ |
| GET    | `/auth/csrf/`        | Obtiene la cookie CSRF                     |
| POST   | `/auth/login/`       | Inicia sesión                              |
| POST   | `/auth/logout/`      | Cierra sesión                              |
| GET    | `/solicitudes/`      | Lista solicitudes visibles para el usuario |
| POST   | `/solicitudes/`      | Crea una solicitud                         |
| GET    | `/solicitudes/{id}/` | Consulta una solicitud                     |
| PUT    | `/solicitudes/{id}/` | Actualiza todos los campos permitidos      |
| PATCH  | `/solicitudes/{id}/` | Actualiza campos específicos               |
| DELETE | `/solicitudes/{id}/` | Elimina una solicitud; solo administrador  |

Los campos `id`, `fecha_creacion` y `usuario` son asignados o protegidos por el
servidor. El estado inicial es `Pendiente`. Las categorías permitidas son
`Hardware`, `Software` y `Redes`; los estados permitidos son `Pendiente`,
`En Proceso` y `Resuelto`.

## 5. Sesión y CSRF

1. Ejecutar `GET /api/auth/csrf/` y conservar la cookie `csrftoken`.
2. Ejecutar `POST /api/auth/login/` con:

```json
{
  "username": "usuario",
  "password": "contraseña"
}
```

3. Conservar la cookie `sessionid`.
4. Para `POST`, `PUT`, `PATCH` y `DELETE`, enviar el valor de `csrftoken` también
   en el encabezado `X-CSRFToken`.

Las operaciones protegidas sin una sesión válida o sin un token CSRF válido deben
ser rechazadas.

## 6. Ejemplo de creación

```http
POST /api/solicitudes/
Content-Type: application/json
X-CSRFToken: <token-csrf>
```

```json
{
  "titulo": "No hay conexión a Internet",
  "descripcion": "El equipo no puede conectarse a la red corporativa.",
  "categoria": "Redes"
}
```

La respuesta esperada es `201 Created` e incluye el propietario asignado por el
servidor y el estado `Pendiente`.

## 7. Pruebas automatizadas

Ejecutar:

```powershell
python manage.py test
```

Las pruebas cubren creación, aislamiento por propietario, permisos de usuario
normal y administrador, validación de datos, autenticación, logout y CSRF.

## 8. Pruebas manuales en Postman

La colección lista para importar está disponible en
[Soporte_Tecnico_API.postman_collection.json](C:/WorkSpace/back-end/backend-soporte/Soporte_Tecnico_API.postman_collection.json).

### Configuración inicial

- **Base URL:** `http://127.0.0.1:8000/api`
- **Cookies:** Postman debe conservar automáticamente las cookies `csrftoken` y
  `sessionid`.
- **Headers para peticiones POST, PUT, PATCH y DELETE:**
  - `Content-Type: application/json`
  - `X-CSRFToken: <valor-de-la-cookie-csrftoken>`

### Variables de entorno

```text
base_url = http://127.0.0.1:8000/api
usuario_normal = juan_perez
clave_usuario_normal = User123*
usuario_admin = admin_soporte
clave_usuario_admin = Admin123*
csrf_token =
solicitud_id =
solicitud_ajena_id =
```

### Paso previo A: obtener la cookie CSRF

- **Método:** `GET`
- **URL:** `{{base_url}}/auth/csrf/`
- **Headers:** ninguno
- **Resultado esperado:** `200 OK`
- **Efecto:** Postman recibe y conserva la cookie `csrftoken`.

### Paso previo B: iniciar sesión como usuario normal

- **Método:** `POST`
- **URL:** `{{base_url}}/auth/login/`
- **Headers:**
  - `Content-Type: application/json`
  - `X-CSRFToken: {{csrf_token}}`
- **Body — raw JSON:**

```json
{
  "username": "juan_perez",
  "password": "User123*"
}
```

- **Resultado esperado:** `200 OK`
- **Efecto:** Postman conserva la cookie `sessionid`.

### Preparar una solicitud ajena

Para comprobar el aislamiento entre usuarios:

1. Cerrar la sesión de `juan_perez`.
2. Iniciar sesión con `maria_lopez` y crear una solicitud.
3. Guardar el `id` de esa solicitud en `solicitud_ajena_id`.
4. Volver a iniciar sesión con `juan_perez`.
5. Ejecutar la solicitud **03 - Usuario consulta solicitud ajena** de la colección.

El resultado esperado es `404 Not Found`, porque el queryset del usuario normal
solo contiene sus propias solicitudes.

### Paso previo C: iniciar sesión como administrador

Para probar operaciones administrativas, repetir el flujo anterior usando:

```json
{
  "username": "admin_soporte",
  "password": "Admin123*"
}
```

### Solicitudes funcionales

- [ ] Obtener CSRF: `GET {{base_url}}/auth/csrf/`
- [ ] Login de usuario normal: `POST {{base_url}}/auth/login/`
- [ ] Login de administrador: `POST {{base_url}}/auth/login/`
- [ ] Crear solicitud: `POST {{base_url}}/solicitudes/`
- [ ] Listar solicitudes: `GET {{base_url}}/solicitudes/`
- [ ] Consultar solicitud: `GET {{base_url}}/solicitudes/{{solicitud_id}}/`
- [x] Actualizar con PUT: `PUT {{base_url}}/solicitudes/{{solicitud_id}}/`
- [ ] Actualizar parcialmente con PATCH:
  `PATCH {{base_url}}/solicitudes/{{solicitud_id}}/`
- [ ] Rechazar cambio de estado de usuario normal.
- [ ] Cambiar estado como administrador.
- [ ] Rechazar eliminación de usuario normal.
- [ ] Eliminar como administrador.
- [ ] Logout: `POST {{base_url}}/auth/logout/`
- [ ] Confirmar que una sesión cerrada ya no permite consultar solicitudes.
- [ ] Confirmar que una escritura sin CSRF devuelve `403 Forbidden`.

La colección contiene scripts de validación de estado HTTP y guarda
automáticamente `csrf_token` al obtener la cookie CSRF y `solicitud_id` al crear
una solicitud.

### Ejemplo: crear una solicitud

- **Método:** `POST`
- **URL:** `{{base_url}}/solicitudes/`
- **Headers:**
  - `Content-Type: application/json`
  - `X-CSRFToken: {{csrf_token}}`
- **Body — raw JSON:**

```json
{
  "titulo": "No hay conexión a Internet",
  "descripcion": "El equipo no puede conectarse a la red corporativa.",
  "categoria": "Redes"
}
```

- **Resultado esperado:** `201 Created`.
- Guardar el valor `id` de la respuesta en la variable `solicitud_id`.

> Si Postman no conserva las cookies automáticamente, abrir el administrador de
> cookies y verificar que `csrftoken` y `sessionid` pertenecen a
> `127.0.0.1`.

## 9. Registro de uso de inteligencia artificial

Esta sección documenta el requisito de uso de IA de la evaluación y las
recomendaciones de seguridad aplicadas al proyecto.

### Herramienta utilizada

```text
Nombre de la herramienta: gemini
Fecha: 18/10/2026
```

### Consulta realizada

```text
¿Cuáles son las vulnerabilidades más críticas al implementar SessionAuthentication en Django REST Framework para un sistema multi-usuario/multi-rol y qué controles de seguridad deben aplicarse en validación de datos, control de acceso a objetos (IDOR) y protección contra CSRF?
```

### Recomendaciones seleccionadas

1. **Recomendación 1:** Mitigación de Insecure Direct Object References (IDOR) a nivel de Base de Datos.
   - Riesgo identificado: Si la verificación de propiedad solo se realiza en el serializador o en la vista individual (has_object_permission), los usuarios estándar podrían inferir identificadores existentes mediante ataques de fuerza bruta o recibir errores ambiguos.
   - Implementación técnica: Se sobrescribió el método get_queryset() en SolicitudViewSet:

     def get_queryset(self):
     user = self.request.user
     if user.is_staff:
     return Solicitud.objects.all().order_by('-fecha_creacion')
     return Solicitud.objects.filter(usuario=user).order_by('-fecha_creacion')

2. **Recomendación 2:** Blindaje contra CSRF y Control Estricto de Modificación de Estado.
   - Riesgo identificado: SessionAuthentication utiliza cookies de navegador para autenticar peticiones, haciéndola vulnerable a ataques de falsificación de petición en sitios cruzados (CSRF). Adicionalmente, usuarios estándar con acceso    de edición a sus tickets podrían elevar sus privilegios modificando arbitrariamente el estado de la solicitud a "Resuelto".
   - Implementación técnica:
     Se implementó un endpoint dedicado @ensure_csrf_cookie (/api/auth/csrf/) que obliga a que toda petición de escritura requiera la cabecera HTTP X-CSRFToken validada por el middleware de Django.

     En SolicitudSerializer.update(), se agregó una validación contextual que bloquea cualquier cambio en el campo estado a usuarios que no posean el atributo is_staff:

     def update(self, instance, validated_data):
     user = self.context['request'].user
     if not user.is_staff and 'estado' in validated_data:
     if validated_data['estado'] != instance.estado:
     raise serializers.ValidationError({"estado": "No tienes permisos para modificar el estado de la solicitud."})
     return super().update(instance, validated_data)

### Evidencia técnica

Las recomendaciones fueron verificadas de la siguiente manera:

- **Aislamiento contra IDOR:** `SolicitudViewSet.get_queryset()` devuelve todas
  las solicitudes únicamente cuando `request.user.is_staff` es verdadero. Para
  usuarios normales devuelve solo `Solicitud.objects.filter(usuario=user)`.
  Además, `IsOwnerOrAdmin.has_object_permission()` valida la propiedad del
  objeto en las operaciones individuales. Esto se comprueba con
  `test_usuario_solo_consulta_sus_solicitudes` y
  `test_usuario_no_consulta_solicitud_ajena` en
  [soporte/tests.py](C:/WorkSpace/back-end/backend-soporte/soporte/tests.py).

- **Protección CSRF:** `SessionAuthentication` utiliza la sesión y el
  middleware `CsrfViewMiddleware` rechaza las escrituras sin un token válido.
  El endpoint `/api/auth/csrf/` establece la cookie mediante
  `ensure_csrf_cookie`. Esto se comprueba con
  `test_escritura_sin_csrf_es_rechazada` y con los encabezados
  `X-CSRFToken` documentados en la colección Postman.

- **Control de estado:** `SolicitudSerializer.update()` impide que un usuario
  normal modifique `estado`, mientras que un administrador sí puede hacerlo.
  Esto se comprueba con `test_usuario_no_puede_cambiar_estado` y
  `test_administrador_puede_cambiar_estado`.

- **Protección de campos automáticos:** `id`, `usuario` y `fecha_creacion` son
  de solo lectura en el serializer y el usuario se asigna en
  `SolicitudViewSet.perform_create()`. Esto se comprueba con
  `test_put_actualiza_campos_permitidos_y_protege_campos_automaticos`.

La evidencia automatizada se ejecuta con:

```powershell
python manage.py test
```

Resultado validado: **12 pruebas ejecutadas correctamente**.

## 10. Estructura principal

```text
core/
  settings.py
  urls.py
soporte/
  models.py
  serializers.py
  permissions.py
  views.py
  urls.py
  tests.py
db.sqlite3
manage.py
requirements.txt
README.md
```
