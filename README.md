# 🍬 Analizador de Lunetas

Este proyecto es una aplicación en **Flask** que permite registrar usuarios con sus preferencias de lunetas (dulces de colores), almacenar la información en memoria y en un archivo `data.json`, y generar un **reporte PDF profesional** con análisis comparativos.

## ✨ Funcionalidades

- Registro de usuarios con:
  - Cantidad de lunetas por color (rojas, azules, amarillas, verdes, naranjas).
  - Color favorito.
- Análisis automático en PDF que incluye:
  - Perfil del usuario registrado.
  - Comparación con los promedios globales.
  - Ranking de usuarios (Top 5).
  - Totales y porcentajes globales desde `data.json`.
  - **Gráficas generadas automáticamente** (con Matplotlib):
    - Comparación usuario vs promedio.
    - Totales globales.
    - Porcentajes globales.
    - Ranking de usuarios.
- Exportación de reportes en **PDF** listos para descarga.

## 🛠️ Tecnologías utilizadas

- [Python 3.10+](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/)
- [Matplotlib](https://matplotlib.org/) (para gráficas)
- [ReportLab](https://www.reportlab.com/) (para generar el PDF)

## 📂 Estructura del proyecto

