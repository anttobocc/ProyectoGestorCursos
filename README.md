# 📚 Proyecto Gestor de Cursos

## 📖 Descripción

**Proyecto Gestor de Cursos** es una aplicación web desarrollada para facilitar la gestión académica de **cursos, estudiantes, profesores y entregables**.

El sistema permite administrar la información mediante operaciones **CRUD**, realizar búsquedas, registrar y modificar datos, gestionar entregables y asociarlos con los estudiantes correspondientes.

El proyecto fue desarrollado utilizando **Python y Django**, con **SQLite** como base de datos y **HTML, CSS y Bootstrap** para la interfaz. También se utilizaron formularios y migraciones de Django para la gestión y validación de los datos.

El desarrollo y control de versiones se realizó mediante **Visual Studio Code y Git/GitHub**, permitiendo registrar los avances y cambios realizados durante las distintas etapas del proyecto.

---

## 👩‍💻 Integrantes

- **Antonella Boccalandro**
- **Candela Mimbi Cáceres**

---

## 🛠️ Tecnologías utilizadas

### 💻 Lenguajes y Frameworks

- **Python**
- **Django**
- **HTML5**
- **CSS3**

### 🗄️ Base de datos

- **SQLite**

### 🎨 Interfaz

- **Bootstrap**

### 🔧 Herramientas de desarrollo

- **Visual Studio Code**
- **Git**
- **GitHub**

---

## ⚙️ Funcionalidades principales

- 📚 Gestión de cursos
- 👩‍🎓 Gestión de estudiantes
- 👨‍🏫 Gestión de profesores
- 📋 Gestión de entregables
- ➕ Registro de información
- ✏️ Modificación de datos
- 🗑️ Eliminación de registros
- 🔎 Búsqueda de cursos
- 🔗 Asociación de entregables con estudiantes
- ✅ Validación de datos mediante formularios
- 🗃️ Gestión de cambios mediante migraciones de Django

---

## 🚀 Objetivo del proyecto

El objetivo del proyecto es desarrollar una aplicación web que permita **centralizar y facilitar la gestión de información académica**, utilizando herramientas y tecnologías estudiadas durante la formación en Desarrollo de Software.

---

## 📂 Estructura del proyecto

La versión actual del proyecto se encuentra organizada utilizando **Django**, separando la configuración del proyecto de la aplicación encargada de las funcionalidades principales.

---

## 📌 Estado del proyecto

**En desarrollo.**

El proyecto continúa siendo actualizado mediante Git y GitHub, registrando los avances y modificaciones realizados durante las diferentes etapas.

Historial y organización del trabajo

A continuación se deja constancia de la evolución del proyecto y de una situación ocurrida durante la integración del trabajo de los integrantes del equipo.

1. Creación del repositorio y primera entrega — 13/06/2026

Se creó el repositorio ProyectoGestorCursos y se realizó la primera entrega del proyecto Django.

La estructura inicial desarrollada fue:

config/
cursos/
manage.py

Esta primera versión incluía las funcionalidades iniciales para la gestión de Cursos, Estudiantes, Profesores y Entregables.

2. Incorporación de un proyecto desarrollado de forma independiente — 06/07/2026

Posteriormente, una integrante del equipo incorporó al repositorio una nueva estructura de proyecto Django creada de manera independiente, en lugar de continuar trabajando sobre los archivos y la estructura que ya se encontraban en el repositorio.

La nueva estructura incorporada fue:

Proyecto1/
myApp/
manage.py

Esto puede comprobarse directamente en el commit correspondiente al 06/07/2026, donde aparecen archivos nuevos de Django como "Proyecto1/settings.py", "Proyecto1/urls.py", "Proyecto1/wsgi.py", "myApp/models.py", "myApp/views.py", "myApp/urls.py" y las distintas plantillas.

Es importante aclarar que esta nueva estructura no consistió en modificaciones de los archivos originales "config/" y "cursos/", sino en la creación e incorporación de otra estructura de proyecto ("Proyecto1/" y "myApp/").

Además, el historial de Git muestra que ambas estructuras no provenían de una misma línea de commits, lo que explica la coexistencia de ambos proyectos dentro del repositorio.

3. Problema generado durante la sincronización local

Al realizar posteriormente un "git pull" para sincronizar el repositorio, los cambios incorporados hicieron que en el entorno local coexistieran las dos estructuras de proyecto.

Como consecuencia, en el entorno de desarrollo local llegaron a aparecer simultáneamente:

config/
cursos/

y

Proyecto1/
myApp/

Esto generó confusión sobre cuál era la estructura que debía utilizarse para continuar el desarrollo.

4. Reorganización y continuidad del proyecto

Para evitar continuar trabajando con dos proyectos Django diferentes, se revisó el historial de Git y se identificó cuál de las estructuras había continuado recibiendo modificaciones.

A partir de esa revisión se decidió continuar el desarrollo sobre:

Proyecto1/
myApp/

La estructura original "config/" y "cursos/" corresponde a la primera etapa del proyecto y se conserva en el historial como parte de la evolución del repositorio.

5. Desarrollo posterior

Sobre la estructura "Proyecto1/myApp" se continuó trabajando en las funcionalidades del sistema, incluyendo:

- CRUD de cursos.
- CRUD de estudiantes.
- CRUD de profesores.
- Gestión de entregables.
- Formularios de creación y edición.
- Eliminación de registros.
- Búsqueda de cursos.
- Asociación de estudiantes con entregables.
- Validaciones.
- Migraciones de la base de datos.
- Mejoras de interfaz y navegación.

Los cambios realizados pueden verificarse mediante los commits correspondientes del repositorio.

6. Situación actual

Actualmente el desarrollo continúa sobre la estructura:

Proyecto1/
myApp/

La aclaración de las dos estructuras se deja documentada para mantener la trazabilidad del proyecto y explicar por qué durante una etapa intermedia coexistieron dos proyectos Django dentro del repositorio y del entorno local.

El historial de commits permanece disponible para verificar cronológicamente las distintas entregas, incorporaciones y modificaciones realizadas durante el desarrollo.
