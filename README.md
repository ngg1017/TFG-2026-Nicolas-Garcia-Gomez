Plataforma de Análisis y Monitorización de Indicadores Clínicos (URCCPQ - HUBU)

Este proyecto nace con el objetivo de automatizar el cálculo de indicadores de calidad asistencial y seguridad del paciente en la Unidad de Reanimación y Cuidados Críticos Postquirúrgicos del Hospital Universitario de Burgos (HUBU).

Desarrollada desde la perspectiva de la Ingeniería de la Salud, esta herramienta transforma un proceso que tradicionalmente requería horas de cálculos médicos manuales en un análisis web instantáneo, seguro y auditable, permitiendo al personal facultativo dedicar su tiempo a la práctica clínica.

Características Principales

    Automatización Estadística: Cálculo automático de variables críticas a partir de registros médicos seudonimizados.

    Privacidad "Zero-Disk" (Cumplimiento LOPD): Procesamiento de archivos locales y bases de datos directamente en memoria RAM (vía buffers y Pandas), garantizando la destrucción de la información mediante el Garbage Collector al finalizar la sesión.

    Despliegue Local Seguro: Orquestación mediante contenedores Docker para funcionar exclusivamente en la intranet hospitalaria, bloqueando la salida de datos a servidores externos o nubes públicas.

    Persistencia Robusta: Integración nativa con bases de datos relacionales para mantener y auditar el histórico clínico de la unidad.

    Versatilidad de Hardware: Soporte diseñado tanto para equipos de escritorio hospitalarios como para uso en terminales autónomos portátiles (arquitectura Raspberry Pi).

Stack Tecnológico

    Lenguaje: Python 3

    Framework Full-Stack: Reflex (FastAPI + WebSockets + React)

    Procesamiento de Datos: Pandas

    Base de Datos & ORM: PostgreSQL (v15+) y SQLModel

    Despliegue e Infraestructura: Docker y Docker Compose

*** Proyecto desarrollado como Trabajo de Fin de Grado en Ingeniería de la Salud.
