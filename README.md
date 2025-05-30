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

## Estructura de modelos y relaciones

- **Usuario**: Modelo principal, contiene los datos generales y los roles.
- **Docente, Estudiante, PadreTutor**: Modelos relacionados con Usuario mediante un campo OneToOne. Cada uno tiene atributos propios.
    - Ejemplo: Docente tiene `especialidad`, Estudiante tiene `direccion`, `fecha_nacimiento`, y un campo `padre_tutor` que es ForeignKey a PadreTutor.

### Relaciones
- Un **Usuario** puede tener un perfil de Docente, Estudiante o PadreTutor (o ninguno).
- Un **PadreTutor** puede estar relacionado con varios Estudiantes (relación uno a muchos).
- Para asignar un padre a un estudiante, se usa el campo `padre_tutor_id` con el ID del modelo PadreTutor.

---

## 🎓 Flujo de Creación de Cursos y Materias

### Estructura de Relaciones Académicas

El sistema maneja una relación **muchos a muchos** entre Cursos y Materias a través de una tabla intermedia llamada `MateriaCurso`, que incluye información del docente asignado:

- **Curso**: Contiene información básica del curso (nombre, turno)
- **Materia**: Contiene información de la materia (nombre, descripción)
- **MateriaCurso**: Tabla intermedia que relaciona curso + materia + docente
- **Horario**: Se relaciona con MateriaCurso para definir horarios específicos

### Flujo Completo de Creación (en orden)

#### **Paso 1: Crear Materias**
```http
POST /api/materias/
Content-Type: application/json

{
  "nombre": "Matemáticas",
  "descripcion": "Curso básico de matemáticas para secundaria"
}
```

```http
POST /api/materias/
Content-Type: application/json

{
  "nombre": "Historia",
  "descripcion": "Historia universal y nacional"
}
```

#### **Paso 2: Crear Docentes (si no existen)**
```http
POST /api/docentes/
Content-Type: application/json

{
  "email": "profesor.matematicas@colegio.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "genero": "M",
  "password": "password123",
  "especialidad": "Matemáticas"
}
```

#### **Paso 3: Crear Cursos**
```http
POST /api/cursos/
Content-Type: application/json

{
  "nombre": "5to A",
  "turno": "mañana"
}
```

```http
POST /api/cursos/
Content-Type: application/json

{
  "nombre": "3ro B",
  "turno": "tarde"
}
```

#### **Paso 4: Asignar Materias con Docentes y Horarios a Cursos**
```http
PATCH /api/cursos/asignar-materias/{curso_id}/
Content-Type: application/json

{
  "asignaciones": [
    {
      "materia_id": 1,
      "docente_id": 2,
      "horarios_ids": [1, 2]
    }
  ]
}
```

**Nota**: Este endpoint **AGREGA** nuevas asignaciones sin eliminar las existentes.

#### **Paso 4b: Agregar Más Materias al Mismo Curso**
```http
PATCH /api/cursos/asignar-materias/{curso_id}/
Content-Type: application/json

{
  "asignaciones": [
    {
      "materia_id": 3,
      "docente_id": 4,
      "horarios_ids": [3, 4]
    }
  ]
}
```

#### **Paso 4c: Ver Asignaciones del Curso**
```http
GET /api/cursos/asignar-materias/{curso_id}/
```

#### **Paso 4d: Eliminar Asignación Específica**
```http
DELETE /api/cursos/{curso_id}/eliminar-materia/{materia_id}/
```

#### **Paso 5: Crear Estudiante y Asignar a Curso (SIMPLIFICADO)**
```http
POST /api/estudiantes/
Content-Type: application/json

{
  "email": "estudiante@example.com",
  "first_name": "Sofia",
  "last_name": "Melgar",
  "genero": "F",
  "password": "some123",
  "direccion": "av. la florida",
  "fecha_nacimiento": "2011-05-29",
  "padre_tutor_id": 5,
  "curso_id": 1
}
```

**Nota**: Ya **NO** requiere el objeto completo del curso, solo el `curso_id`.

#### **Paso 6: Ver Horarios de un Docente**
```http
GET /api/docentes/{docente_id}/horarios/
```

**Respuesta:**
```json
{
  "docente": "Juan Pérez", 
  "total_horarios": 2,
  "horarios": [
    {
      "horario_id": 1,
      "nombre": "Matemáticas Básica",
      "dia_semana": "Lunes",
      "hora_inicio": "08:00:00",
      "hora_fin": "09:30:00",
      "materia": "Matemáticas",
      "curso": "5to A - mañana"
    }
  ]
}
```

### Endpoints Disponibles para Cursos y Materias

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/cursos/` | Listar todos los cursos |
| POST | `/api/cursos/` | Crear un nuevo curso |
| GET | `/api/cursos/{id}/` | Obtener curso específico |
| PUT/PATCH | `/api/cursos/{id}/` | Actualizar curso |
| DELETE | `/api/cursos/{id}/` | Eliminar curso |
| GET | `/api/cursos/turnos/` | Obtener opciones de turnos |
| GET | `/api/cursos/con-materias/{id}` | Ver curso con sus materias |
| GET | `/api/cursos/asignar-materias/{id}/` | Ver asignaciones de materias-docentes |
| PATCH | `/api/cursos/asignar-materias/{id}/` | Asignar/actualizar materias con docentes |
| GET | `/api/materias/` | Listar todas las materias |
| POST | `/api/materias/` | Crear una nueva materia |
| GET | `/api/horarios/` | Listar todos los horarios |
| POST | `/api/horarios/` | Crear un nuevo horario |

### Validaciones Importantes

- **Relación única curso-turno**: Un curso con el mismo nombre puede existir en diferentes turnos (ej: "1ro A" mañana y "1ro A" tarde)
- **Relación única materia-curso**: Un curso no puede tener la misma materia asignada dos veces
- **Docente requerido**: Toda asignación materia-curso debe tener un docente
- **Turnos válidos**: Solo se permiten los turnos: "mañana", "tarde", "noche"
- **Validación integrada de horarios**: Al asignar materias con horarios, el sistema valida automáticamente:
  - No hay choques entre horarios nuevos y existentes
  - No hay solapamiento dentro de la misma asignación
  - Los horarios tienen hora_inicio < hora_fin
- **Actualizaciones inteligentes**: El sistema preserva asignaciones y horarios existentes que no cambien
- **Transaccionalidad**: Todo se ejecuta en una transacción atómica (todo o nada)

### Validaciones de Horarios

El sistema incluye validaciones automáticas integradas para evitar conflictos:

#### **Ejemplo de asignación con validación automática:**
```http
PATCH /api/cursos/asignar-materias/1/
Content-Type: application/json

{
  "asignaciones": [
    {
      "materia_id": 1,
      "docente_id": 2,
      "horarios": [
        {
          "dia_semana": "Lunes",
          "hora_inicio": "08:00",
          "hora_fin": "09:30"
        },
        {
          "dia_semana": "Lunes",
          "hora_inicio": "09:00",
          "hora_fin": "10:30"
        }
      ]
    }
  ]
}
```

**Error esperado (solapamiento):**
```json
{
  "asignaciones": [
    {
      "horarios": [
        "Horarios solapados para Lunes: 08:00:00-09:30:00 y 09:00:00-10:30:00"
      ]
    }
  ]
}
```

#### **Ejemplo de choque con horarios existentes:**
Si ya existe Matemáticas de 08:00-09:30 los Lunes:
```http
PATCH /api/cursos/asignar-materias/1/
Content-Type: application/json

{
  "asignaciones": [
    {
      "materia_id": 2,
      "docente_id": 3,
      "horarios": [
        {
          "dia_semana": "Lunes",
          "hora_inicio": "08:30",
          "hora_fin": "10:00"
        }
      ]
    }
  ]
}
```

**Error esperado:**
```json
{
  "non_field_errors": [
    "Choque de horarios detectado en Lunes: 'Matemáticas' (08:00:00-09:30:00) vs 'Historia' (08:30:00-10:00:00)"
  ]
}
```

#### **Ejemplos de cursos válidos en diferentes turnos:**
```json
// ✅ Permitido
{"nombre": "1ro A", "turno": "mañana"}
{"nombre": "1ro A", "turno": "tarde"}
{"nombre": "1ro A", "turno": "noche"}

// ❌ Error - duplicado en mismo turno
{"nombre": "1ro A", "turno": "mañana"}  // Ya existe
```

### Ejemplo de Uso Completo

```bash
# 1. Crear materias
curl -X POST http://localhost:8000/api/materias/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {tu_token}" \
  -d '{"nombre": "Matemáticas", "descripcion": "Álgebra y geometría"}'

# 2. Crear curso
curl -X POST http://localhost:8000/api/cursos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {tu_token}" \
  -d '{"nombre": "5to A", "turno": "mañana"}'

# 3. Asignar materia con docente y horarios en una sola operación
curl -X PATCH http://localhost:8000/api/cursos/asignar-materias/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {tu_token}" \
  -d '{
    "asignaciones": [
      {
        "materia_id": 1, 
        "docente_id": 2,
        "horarios": [
          {
            "dia_semana": "Lunes",
            "hora_inicio": "08:00",
            "hora_fin": "09:30"
          },
          {
            "dia_semana": "Miércoles",
            "hora_inicio": "10:00",
            "hora_fin": "11:30"
          }
        ]
      }
    ]
  }'

# 4. Agregar horario adicional (opcional)
curl -X POST http://localhost:8000/api/horarios/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {tu_token}" \
  -d '{"materia_curso": 1, "dia_semana": "Viernes", "hora_inicio": "08:00", "hora_fin": "09:30"}'
```

---

## Endpoints principales

### Usuarios generales
- **POST /api/usuarios/**: Crea un usuario general (no asigna datos propios de docente, estudiante o padre/tutor).
- **GET /api/usuarios/**: Lista todos los usuarios generales.

### Docentes
- **POST /api/docentes/**: Crea un usuario y un perfil de docente (requiere datos de usuario y `especialidad`).
- **GET /api/docentes/**: Lista todos los docentes con todos los datos del usuario y del docente.

### Estudiantes
- **POST /api/estudiantes/**: Crea un usuario y un perfil de estudiante (requiere datos de usuario, `direccion`, `fecha_nacimiento` y opcionalmente `padre_tutor_id`).
- **GET /api/estudiantes/**: Lista todos los estudiantes con todos los datos del usuario y del estudiante, incluyendo información del padre/tutor si está asignado.

### Padres/Tutores
- **POST /api/padres-tutores/**: Crea un usuario y un perfil de padre/tutor (requiere datos de usuario, `parentesco`, `telefono`).
- **GET /api/padres-tutores/**: Lista todos los padres/tutores con todos los datos del usuario y del padre/tutor.

---

## Ejemplo de relación estudiante-padre

Para asignar un padre/tutor a un estudiante, usa el campo `padre_tutor_id` con el ID del modelo PadreTutor:

```json
{
    "email": "estudiante@example.com",
    "first_name": "Ana",
    "last_name": "López",
    "genero": "F",
    "activo": true,
    "password": "123456",
    "direccion": "Calle 123",
    "fecha_nacimiento": "2005-05-10",
    "padre_tutor_id": 5
}
```

Donde `5` es el ID del padre/tutor (no el ID del usuario).

---

## Resumen de endpoints

| Endpoint                        | Descripción                                      |
|---------------------------------|--------------------------------------------------|
| POST /api/usuarios/             | Crear usuario general                            |
| POST /api/docentes/             | Crear usuario + perfil docente                   |
| POST /api/estudiantes/          | Crear usuario + perfil estudiante                |
| POST /api/padres-tutores/       | Crear usuario + perfil padre/tutor               |
| GET /api/docentes/              | Listar docentes (datos completos)                |
| GET /api/estudiantes/           | Listar estudiantes (datos completos)             |
| GET /api/padres-tutores/        | Listar padres/tutores (datos completos)          |

---

Para más detalles, revisa la documentación Swagger en:
- [http://localhost:8000/swagger/](http://localhost:8000/swagger/)