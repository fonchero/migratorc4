# 🛠️ Migrador de Proyectos Fuse 2 a Quarkus 4

Este repositorio contiene un conjunto de scripts en Python que automatizan la migración de proyectos Java basados en Apache Camel 2 (Fuse 2) hacia una arquitectura moderna con **Quarkus 4** y **Camel 4**.

---

## 📦 Estructura General del Proceso

El sistema permite:

1. **Migrar un proyecto individual** → `migrar_proyecto_completo.py`
2. **Migrar todos los proyectos de una carpeta** → `migrar_todos_los_proyectos.py`

---

## ▶️ Requisitos

- Python 3.8 o superior
- Maven instalado
- Git (opcional pero recomendado)
- Proyecto Fuse 2 con estructura válida (`pom.xml`, `src/main/java`, `blueprint.xml`, etc.)
- Archivo `pom_template.xml` ya adaptado a Quarkus 4
- Archivo `application-global.properties` con configuraciones heredadas

---

## 🚀 Comando para Migrar Todos los Proyectos

```bash
python migrar_todos_los_proyectos.py <carpeta_IN> <carpeta_OUT> <pom_template.xml> <application-global.properties> <formatear(1|0)> <compilar(1|0)>
