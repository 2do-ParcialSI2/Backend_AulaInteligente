# AulaVirtual Backend

## Descripción
Este proyecto es el backend de un sistema de Aula Virtual desarrollado en **Python 3.11+** usando **Django** y **Django REST Framework**. Incluye gestión de usuarios, roles, permisos, autenticación JWT, documentación interactiva con Swagger y configuración segura mediante variables de entorno.

---

## Flujo de uso inicial

### 1. Clona el repositorio y entra al directorio del proyecto
```bash
# Clona el repositorio
git clone <url-del-repo>
cd <carpeta-del-proyecto>
```

### 2. Crea y activa un entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate  # En Linux/Mac
.venv\Scripts\activate   # En Windows
```

### 3. Instala las dependencias necesarias
```bash
pip install -r requirements.txt
```
Si no existe un `requirements.txt`, instala manualmente:
```bash
pip install django djangorestframework djangorestframework-simplejwt drf-yasg psycopg2-binary python-dotenv
```

### 4. Crea el archivo `.env` en la raíz del proyecto
Ejemplo de contenido:
```
SECRET_KEY=tu_clave_secreta
DEBUG=True
DB_NAME=Backend_AulaVirtual
DB_USER=postgres
DB_PASSWORD=Admin
DB_HOST=localhost
DB_PORT=5432
```

### 5. Realiza las migraciones y ejecuta el servidor
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## Creación del primer usuario ADMINISTRADOR
1. Accede a la documentación Swagger en:
   - [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
2. Busca el endpoint `POST /api/crear-admin/`.
3. Haz clic en **Try it out** e ingresa los datos del admin:
   ```json
   {
     "correo": "admin@ejemplo.com",
     "name": "Administrador",
     "password": "TuContraseñaSegura"
   }
   ```
4. Ejecuta la petición. Si todo está bien, verás un mensaje de éxito.

---

## Login y uso del token en Swagger
1. Ve al endpoint `POST /api/login/` en Swagger.
2. Ingresa el correo y contraseña del usuario.
3. Copia el valor del campo `token` que recibes en la respuesta.
4. Haz clic en el botón **Authorize** en la parte superior de Swagger.
5. Pega el token así:
   ```
   Bearer <tu_token>
   ```
6. Ahora puedes probar todos los endpoints protegidos.

---

## Cambiar valores de la base de datos
Edita el archivo `.env` y cambia los valores de:
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

---

## Rutas importantes
- **Swagger:** [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **Redoc:** [http://localhost:8000/redoc/](http://localhost:8000/redoc/)
- **Admin Django:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## Dependencias principales
- Python 3.11+
- Django
- djangorestframework
- djangorestframework-simplejwt
- drf-yasg
- psycopg2-binary
- python-dotenv

---

## Otras funcionalidades implementadas
- Gestión de usuarios, roles y permisos.
- Borrado lógico de usuarios (campo `activo`).
- Modelos extendidos: Estudiante, Docente, Padre/Tutor.
- Autenticación JWT (token válido por 2 horas).
- Configuración segura con variables de entorno.
- Documentación interactiva con Swagger y Redoc.

---

## Notas
- El primer usuario administrador solo puede crearse si no existe otro admin.
- Todos los endpoints protegidos requieren autenticación JWT.
- Más adelante puedes restringir el acceso a endpoints según roles/permisos.

---

¿Dudas o sugerencias? ¡Revisa el código o contacta al desarrollador! 