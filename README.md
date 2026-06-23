# Sistema Integrado de Monitoreo de Salud Poblacional (NHANES)

Este proyecto consiste en una solución tecnológica *end-to-end* diseñada para integrar, procesar, disponibilizar y visualizar indicadores analíticos de salud pública basados en los estudios nacionales del **NHANES (CDC)**, cumpliendo con los estándares de arquitectura de software y ciencia de datos de la industria.

## 📐 Arquitectura Técnica de la Solución

El sistema se encuentra completamente desacoplado en componentes modulares independientes, orquestados mediante microservicios:

1. **Pipeline ETL (`/etl`):** Módulo encargado de extraer datos de tres fuentes distintas:
   * **Archivos:** Datasets demográficos y antropométricos oficiales del NHANES en formato SAS Transport (.XPT).
   * **API REST:** Consumo de personal médico simulado desde un servicio externo JSON.
   * **Base de Datos SQL:** Catálogo local estructurado en SQLite con las métricas oficiales de IMC parametrizadas por la Organización Mundial de la Salud (OMS).
2. **API Interna de Datos (`/api`):** Backend desarrollado en **FastAPI** que expone el modelo relacional procesado en endpoints optimizados y documentados dinámicamente bajo el estándar OpenAPI (Swagger).
3. **Visualización Interactiva (`/dashboards`):** Frontend interactivo desarrollado en **Streamlit** estructurado por perfiles de audiencia para la toma de decisiones.

---

## 👥 Vistas Orientadas a Audiencias (Valor de Negocio)

Para maximizar el impacto de la herramienta, el dashboard implementa tres vistas de acceso exclusivas:

* **Vista Ejecutiva (Dirección Médica):** Despliega KPIs agregados de alto nivel (Totales ponderados, promedios de edad, IMC global y gráficos analíticos interactivos de distribución epidemiológica de la OMS) diseñados para planificación macro y toma de decisiones presupuestarias.
* **Vista Operativa (Gestión de Pacientes):** Motor de búsqueda dinámico con filtros transaccionales en tiempo real por género y diagnóstico nutricional, permitiendo a los médicos coordinadores auditar el padrón poblacional y segmentar subgrupos de riesgo de manera ágil.
* **Vista Técnica (Administración TI):** Monitor del estado de salud de la infraestructura de datos (Healthcheck), documentación viva del esquema de los endpoints y logs del estado de consistencia del pipeline.

---

## 🐳 Guía de Despliegue con Docker

La solución está completamente contenedorizada, eliminando el problema de "funciona en mi máquina" y asegurando portabilidad absoluta.

### Requisitos Previos
* Docker Desktop instalado y en ejecución.
* Git instalado.

### Instrucciones de Arranque
1. Clone el repositorio localmente.
2. Asegúrese de que el pipeline ETL haya generado la base de datos y archivos procesados (se incluyen scripts automatizados).
3. En la raíz del proyecto, ejecute el comando de orquestación de Docker Compose:
   ```bash
   docker-compose up --build -d