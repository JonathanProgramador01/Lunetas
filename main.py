from flask import Flask, render_template, request, redirect, url_for

import os
import io
import json
import matplotlib.pyplot as plt
from datetime import datetime
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# Lista para almacenar usuarios (en una aplicación real usarías una base de datos)
usuarios = []


@app.route('/')
def index():
    return render_template('index.html', usuarios=usuarios)


@app.route('/guardar', methods=['POST'])
def guardar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        rojas = int(request.form['rojas'])
        azules = int(request.form['azules'])
        amarillas = int(request.form['amarillas'])
        verdes = int(request.form['verdes'])
        naranjas = int(request.form['naranjas'])
        favorita = request.form['favorita']

        total = rojas + azules + amarillas + verdes + naranjas

        usuario = {
            'nombre': nombre,
            'rojas': rojas,
            'azules': azules,
            'amarillas': amarillas,
            'verdes': verdes,
            'naranjas': naranjas,
            'total': total,
            'favorita': favorita
        }

        usuarios.append(usuario)

        mensaje = f"¡Datos guardados para {nombre}! Tienes {total} lunetas. Tu favorita es la {favorita}."
        return render_template('index.html', mensaje=mensaje, usuarios=usuarios)
    else:
        return redirect(url_for('index'))







@app.route('/reporte')
def reporte():
    if not usuarios:
        return "No hay datos aún."

    # Crear carpeta static si no existe
    os.makedirs("static", exist_ok=True)

    # 1. Cargar data.json
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    data_usuarios = data["usuarios"]
    data_totales = data["totales"]
    data_porcentajes = data["porcentajes"]

    # 2. Último usuario registrado
    usuario = usuarios[-1]

    # 3. Cálculos comparativos
    total_general = sum(u['total'] for u in usuarios)
    promedio_total = total_general / len(usuarios)
    comparacion_total = "mayor" if usuario['total'] > promedio_total else "menor"
    favorito_global = max(data_totales, key=lambda c: data_totales[c] if c != "total" else 0)

    # Ranking general
    ranking_all = sorted(data_usuarios, key=lambda x: x['total'], reverse=True)
    posicion_usuario = next((i+1 for i,u in enumerate(ranking_all) if u['nombre'].lower() == usuario['nombre'].lower()), None)

    # Top 3 colores del usuario
    colores_usuario = ["rojas", "azules", "amarillas", "verdes", "naranjas"]
    top_colores = sorted([(c, usuario[c]) for c in colores_usuario], key=lambda x: x[1], reverse=True)[:3]

    # ============================================================
    # 4. GRÁFICAS
    # ============================================================

    # Comparación usuario vs promedio
    colores_json = {"rojas": "rojo", "azules": "azul", "amarillas": "amarillo",
                    "verdes": "verde", "naranjas": "naranja"}

    valores_usuario = [usuario[c] for c in colores_usuario]
    valores_promedio = [data_totales[colores_json[c]] / len(data_usuarios) for c in colores_usuario]

    comparacion_path = os.path.join(os.getcwd(), "static", "comparacion.png")
    plt.figure(figsize=(8, 6))
    x = range(len(colores_usuario))
    plt.bar(x, valores_usuario, width=0.4, label=f"{usuario['nombre']}", align='center')
    plt.bar([i + 0.4 for i in x], valores_promedio, width=0.4, label="Promedio", align='center')
    plt.xticks([i + 0.2 for i in x], colores_usuario)
    plt.title("Comparación Usuario vs Promedio")
    plt.legend()
    plt.savefig(comparacion_path)
    plt.close()

    # Totales globales
    totales_path = os.path.join(os.getcwd(), "static", "totales_globales.png")
    plt.figure(figsize=(8, 6))
    colores_lista = ['green', 'yellow', 'red', 'orange', 'purple', 'blue']
    plt.bar([k for k in data_totales.keys() if k != "total"],
            [v for k, v in data_totales.items() if k != "total"],
            color=colores_lista)
    plt.title("Totales Globales (JSON)")
    plt.savefig(totales_path)
    plt.close()

    # Porcentajes globales
    porcentajes_path = os.path.join(os.getcwd(), "static", "porcentajes.png")
    plt.figure(figsize=(6, 6))
    plt.pie([int(v.replace('%', '')) for k, v in data_porcentajes.items() if k != "total"],
            labels=[k for k in data_porcentajes.keys() if k != "total"],
            autopct='%1.1f%%',
            colors=colores_lista)
    plt.title("Porcentajes Globales")
    plt.savefig(porcentajes_path)
    plt.close()

    # Ranking de usuarios
    ranking = sorted(data_usuarios, key=lambda x: x['total'], reverse=True)[:5]
    nombres = [u['nombre'] for u in ranking]
    totales = [u['total'] for u in ranking]

    ranking_path = os.path.join(os.getcwd(), "static", "ranking.png")
    plt.figure(figsize=(8, 6))
    plt.barh(nombres, totales, color="skyblue")
    plt.gca().invert_yaxis()
    plt.title("Top 5 Usuarios por Total de Lunetas")
    plt.savefig(ranking_path)
    plt.close()

    # ============================================================
    # 5. CREAR PDF
    # ============================================================
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Portada
    story.append(Paragraph("🍬 Reporte de Análisis de Lunetas", styles["Title"]))
    story.append(Spacer(1, 24))
    story.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 48))

    # Resumen usuario
    story.append(Paragraph("👤 Perfil del Usuario", styles["Heading2"]))
    story.append(Paragraph(f"<b>Nombre:</b> {usuario['nombre']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Total de lunetas:</b> {usuario['total']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Color favorito:</b> {usuario['favorita']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Posición en el ranking:</b> #{posicion_usuario} de {len(data_usuarios)}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Comparación
    story.append(Paragraph("📈 Comparación con los demás", styles["Heading2"]))
    story.append(Paragraph(
        f"El usuario tiene un total de <b>{usuario['total']}</b> lunetas, lo cual es "
        f"{comparacion_total} al promedio general de <b>{promedio_total:.2f}</b>.",
        styles["Normal"]
    ))
    if usuario['favorita'] == favorito_global:
        story.append(Paragraph(f"Tu color favorito coincide con el más popular: <b>{favorito_global}</b>. 🎉", styles["Normal"]))
    else:
        story.append(Paragraph(f"Tu color favorito es <b>{usuario['favorita']}</b>, mientras que el más popular es <b>{favorito_global}</b>.", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Top 3 colores
    story.append(Paragraph("🏅 Tus 3 colores más elegidos", styles["Heading2"]))
    for c, v in top_colores:
        story.append(Paragraph(f"{c.capitalize()}: {v}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Gráficas
    story.append(Paragraph("Comparación de colores:", styles["Heading2"]))
    story.append(Image(comparacion_path, width=400, height=250))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Totales globales (JSON):", styles["Heading2"]))
    story.append(Image(totales_path, width=400, height=250))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Porcentajes globales:", styles["Heading2"]))
    story.append(Image(porcentajes_path, width=400, height=250))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Ranking de usuarios:", styles["Heading2"]))
    story.append(Image(ranking_path, width=400, height=250))
    story.append(Spacer(1, 12))

    # Guardar PDF
    doc.build(story)
    buffer.seek(0)

    # Eliminar imágenes temporales
    for img in [comparacion_path, totales_path, porcentajes_path, ranking_path]:
        if os.path.exists(img):
            os.remove(img)

    return send_file(buffer, as_attachment=True,
                     download_name="reporte_lunetas.pdf",
                     mimetype="application/pdf")













if __name__ == '__main__':
    app.run(debug=True)