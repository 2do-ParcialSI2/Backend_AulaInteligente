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
python manage.py runserver 8001
```

**📝 Nota**: El servidor ejecuta en el puerto **8001**. El microservicio de predicción ML debe ejecutarse en el puerto **8000**.

---

## Creación del primer usuario ADMINISTRADOR
1. Accede a la documentación Swagger en:
   - [http://localhost:8001/swagger/](http://localhost:8001/swagger/)
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
- **Swagger:** [http://localhost:8001/swagger/](http://localhost:8001/swagger/)
- **Redoc:** [http://localhost:8001/redoc/](http://localhost:8001/redoc/)
- **Admin Django:** [http://localhost:8001/admin/](http://localhost:8001/admin/)

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
curl -X POST http://localhost:8001/api/materias/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {tu_token}" \
  -d '{"nombre": "Matemáticas", "descripcion": "Álgebra y geometría"}'

# 2. Crear curso
curl -X POST http://localhost:8001/api/cursos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {tu_token}" \
  -d '{"nombre": "5to A", "turno": "mañana"}'

# 3. Asignar materia con docente y horarios en una sola operación
curl -X PATCH http://localhost:8001/api/cursos/asignar-materias/1/ \
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
curl -X POST http://localhost:8001/api/horarios/ \
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
- [http://localhost:8001/swagger/](http://localhost:8001/swagger/)


GET    /api/cursos/trimestres/           # Listar todos
POST   /api/cursos/trimestres/           # Crear nuevo ✅
GET    /api/cursos/trimestres/{id}/      # Obtener uno
PUT    /api/cursos/trimestres/{id}/      # Actualizar completo
PATCH  /api/cursos/trimestres/{id}/      # Actualizar parcial
DELETE /api/cursos/trimestres/{id}/      # Eliminar

# Acciones personalizadas
GET    /api/cursos/trimestres/activo/            # Trimestre activo
PATCH  /api/cursos/trimestres/{id}/activar/     # Activar trimestre

POST /api/cursos/trimestres/
{
  "nombre": "1er Trimestre",
  "fecha_inicio": "2025-02-03", 
  "fecha_fin": "2025-05-05",
  "activo": true
}

// Respuesta:
{
  "id": 1,
  "nombre": "1er Trimestre",
  "fecha_inicio": "2025-02-03",
  "fecha_fin": "2025-05-05", 
  "activo": true
}

---

## 🤖 Predicción de Notas con Machine Learning

### 📊 Integración con Microservicio de ML

El sistema incluye un endpoint especializado que integra con un **microservicio de Machine Learning** para predecir la nota del tercer trimestre basándose en el rendimiento de los trimestres 1 y 2.

### 🎯 Endpoint de Predicción

```http
POST /api/seguimientos/predecir-nota/{estudiante_id}/{materia_curso_id}/
```

#### **Descripción:**
Este endpoint realiza todo el proceso de predicción automáticamente:
1. 📊 Obtiene los datos de seguimiento del estudiante para los trimestres 1 y 2
2. 🔄 Calcula los promedios específicos requeridos por el modelo ML
3. 🤖 Llama al microservicio de predicción en `http://localhost:8000/api/v1/predecir/`
4. ✅ Retorna la predicción formateada con contexto completo

#### **Ejemplo de uso:**
```bash
curl -X POST http://localhost:8001/api/seguimientos/predecir-nota/123/456/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {tu_token}"
```

#### **Respuesta exitosa:**
```json
{
  "success": true,
  "estudiante_id": 123,
  "materia_curso_id": 456,
  "prediccion": {
    "nota_estimada": 84.7,
    "clasificacion": "medio",
    "nivel_confianza": "alto",
    "confianza_valor": 3.2,
    "mensaje": "Buen rendimiento. Se estima una nota de 84.7 (rendimiento medio) con alta confianza."
  },
  "datos_utilizados": {
    "prom_tareas_t1": 85.0,
    "prom_examenes_t1": 78.0,
    "prom_part_t1": 92.0,
    "asistencia_t1": 95.0,
    "prom_tareas_t2": 87.0,
    "prom_examenes_t2": 82.0,
    "prom_part_t2": 88.0,
    "asistencia_t2": 93.0
  },
  "trimestres_utilizados": ["1er Trimestre", "2do Trimestre"]
}
```

### 📋 Prerrequisitos para la Predicción

Para que el endpoint funcione correctamente, el sistema debe tener:

1. **✅ Microservicio ML ejecutándose**: En `http://localhost:8000/api/v1/predecir/`
2. **✅ Al menos 2 trimestres**: Registrados en el sistema (ordenados por fecha de inicio)
3. **✅ Seguimientos completos**: El estudiante debe tener seguimiento en trimestres 1 y 2 para la materia específica
4. **✅ Datos de actividades**: Tareas, exámenes, participaciones y asistencias registradas

### 🔧 Datos que Calcula Automáticamente

El endpoint calcula automáticamente estos promedios específicos por trimestre:

| Campo | Descripción |
|-------|-------------|
| `prom_tareas_t1/t2` | Promedio de todas las tareas del trimestre |
| `prom_examenes_t1/t2` | Promedio de todos los exámenes del trimestre |
| `prom_part_t1/t2` | Promedio de todas las participaciones del trimestre |
| `asistencia_t1/t2` | Porcentaje de asistencia del trimestre |

### ⚠️ Manejo de Errores

#### **Errores comunes y respuestas:**

**🔍 Estudiante no encontrado:**
```json
{
  "success": false,
  "error": "No se encontró el estudiante con ID 123"
}
```

**📚 Materia-curso no encontrada:**
```json
{
  "success": false,
  "error": "No se encontró la materia-curso con ID 456"
}
```

**📅 Trimestres insuficientes:**
```json
{
  "success": false,
  "error": "Se necesitan al menos 2 trimestres registrados para hacer predicciones"
}
```

**📊 Seguimiento faltante:**
```json
{
  "success": false,
  "error": "No se encontró seguimiento del estudiante en 1er Trimestre"
}
```

**🔌 Microservicio no disponible:**
```json
{
  "success": false,
  "error": "No se puede conectar al microservicio de predicción. Verifique que esté ejecutándose en http://localhost:8000"
}
```

### 🚀 Integración Frontend

#### **JavaScript/React:**
```javascript
const predecirNota = async (estudianteId, materiaCursoId) => {
  try {
    const response = await fetch(
      `/api/seguimientos/predecir-nota/${estudianteId}/${materiaCursoId}/`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    const resultado = await response.json();
    
    if (resultado.success) {
      console.log('Predicción:', resultado.prediccion);
      console.log('Nota estimada:', resultado.prediccion.nota_estimada);
    } else {
      console.error('Error:', resultado.error);
    }
  } catch (error) {
    console.error('Error de conexión:', error);
  }
};
```

#### **Python/Django (desde otra vista):**
```python
import requests

def obtener_prediccion_estudiante(estudiante_id, materia_curso_id):
    try:
        response = requests.post(
            f'http://localhost:8001/api/seguimientos/predecir-nota/${estudiante_id}/${materia_curso_id}/',
            headers={'Authorization': f'Bearer ${token}'},
            timeout=15
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': str(e)}
```

### 📈 Casos de Uso

1. **📱 Dashboard de Estudiante**: Mostrar predicciones de todas sus materias
2. **👨‍🏫 Vista de Docente**: Identificar estudiantes en riesgo académico
3. **👨‍💼 Reportes Administrativos**: Estadísticas de rendimiento predecido por curso
4. **📧 Alertas Tempranas**: Notificaciones automáticas para estudiantes con predicciones bajas
5. **📊 Análisis de Tendencias**: Comparar predicciones vs notas reales para mejorar el modelo

### 🔗 Relacionado

- **Microservicio ML**: Documentación completa en el README del proyecto de predicción
- **Módulo Seguimiento**: Gestiona todas las actividades académicas del estudiante
- **API Swagger**: Documentación interactiva disponible en `/swagger/`

---

**💡 Nota**: Esta funcionalidad requiere que el microservicio de Machine Learning esté ejecutándose de forma independiente. Asegúrate de seguir las instrucciones de instalación y configuración del microservicio antes de usar este endpoint.