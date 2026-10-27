#!/usr/bin/env python3
"""
Sincroniza M0007-bia en la web relatos.raupulus.dev:
1. Copia y convierte portada, avatares y 5 escenas a WebP (q85).
2. Lee el relato de M0007-bia.md.
3. Actualiza mitologia.json en la raíz y en data/.
"""

import json
import subprocess
import os
from pathlib import Path

RELATOS_DIR = Path("/Users/fryntiz/Library/CloudStorage/GoogleDrive-raupulus@gmail.com/Mi unidad/ia/Relatos")
WEB_DIR = Path("/Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev")
M0007_DIR = RELATOS_DIR / "Historias Mitológicas" / "africa" / "akan" / "abosom" / "M0007-bia"

# Rutas web
PUB_IMAGES = WEB_DIR / "public" / "assets" / "images"
(PUB_IMAGES / "portadas").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "avatars").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "escenas").mkdir(parents=True, exist_ok=True)

# 1. Convertir y copiar portada 16:9 a WebP (q85)
src_portada = M0007_DIR / "youtube" / "portada-es-ES.jpg"
dst_portada = PUB_IMAGES / "portadas" / "M0007-bia.webp"
subprocess.run([
    "cwebp", "-q", "85", str(src_portada), "-o", str(dst_portada)
], check=True)
print(f"✅ Portada WebP: {dst_portada}")

# 2. Convertir y copiar avatares a WebP (q85)
src_cabeza = M0007_DIR / "avatars" / "personaje-01-bia-cabeza.png"
dst_cabeza = PUB_IMAGES / "avatars" / "personaje-01-bia-cabeza.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cabeza), "-o", str(dst_cabeza)], check=True)

src_cuerpo = M0007_DIR / "avatars" / "personaje-01-bia-cuerpo.png"
dst_cuerpo = PUB_IMAGES / "avatars" / "personaje-01-bia-cuerpo.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cuerpo), "-o", str(dst_cuerpo)], check=True)
print(f"✅ Avatares WebP listos.")

# 3. Convertir y copiar 5 escenas clave a WebP (q85)
escenas_map = [
    ("002-profundidades-boscosas-valle-rio-bia.png", "M0007-002-profundidades-boscosas-valle-rio-bia.webp", "Las profundidades boscosas donde las tierras altas de Ghana se funden con los valles vírgenes de Costa de Marfil y nace el río Bia."),
    ("004-bia-joven-guerrero-sacerdote-rio.png", "M0007-004-bia-joven-guerrero-sacerdote-rio.webp", "Bia manifestado como noble guerrero y sacerdote de porte atlético, piel de ébano y adornos ceremoniales de cauris y lianas de agua dulce."),
    ("011-refugio-fauna-elefantes-de-bosque-y-leopardos.png", "M0007-011-refugio-fauna-elefantes-de-bosque-y-leopardos.webp", "El dominio inviolable de Bia como refugio sagrado para los elefantes de bosque, leopardos y la biodiversidad salvaje."),
    ("025-tano-disfrazado-ante-nyame-robo-bendicion.png", "M0007-025-tano-disfrazado-ante-nyame-robo-bendicion.webp", "El engaño de Tano al alba ante su padre anciano Nyame para arrebatar la primogenitura y el corazón dorado de Ashanti."),
    ("033-florecer-vida-en-rincon-mas-salvaje.png", "M0007-033-florecer-vida-en-rincon-mas-salvaje.webp", "La dignidad inquebrantable de Bia haciendo florecer la vida y la pureza en el rincón más salvaje del mundo.")
]

inline_scenes = []
for src_f, dst_f, pie in escenas_map:
    s_path = M0007_DIR / "escenas" / src_f
    d_path = PUB_IMAGES / "escenas" / dst_f
    subprocess.run(["cwebp", "-q", "85", str(s_path), "-o", str(d_path)], check=True)
    inline_scenes.append({
        "archivo": f"assets/images/escenas/{dst_f}",
        "pie": pie
    })
print(f"✅ 5 escenas clave WebP listas.")

# 4. Extraer texto del relato de M0007-bia.md
relato_md = M0007_DIR / "M0007-bia.md"
relato_txt = relato_md.read_text(encoding="utf-8")
parts = relato_txt.split("## Relato")
narrative_text = parts[1].strip() if len(parts) > 1 else ""

# 5. Construir objeto M0007
m0007 = {
    "id": "M0007",
    "slug": "bia",
    "nombre": "Bia",
    "epiteto": "El Señor de las Aguas Indómitas",
    "titulo_completo": "Bia: El Señor de las Aguas Indómitas ⚡ Espíritus Abosom (África)",
    "region": "africa",
    "region_nombre": "África",
    "tradicion": "akan",
    "tradicion_nombre": "Mitología Akan",
    "grupo": "abosom",
    "grupo_nombre": "Espíritus Abosom",
    "estado": "estreno",
    "publicado": False,
    "palabras": 880,
    "duracion_video": "05:29",
    "duracion_audio": "05:29",
    "duracion_short": "00:50",
    "sinopsis": "En las densas selvas de la frontera entre Ghana y Costa de Marfil reina Bia, el espíritu abosom de las aguas salvajes y primogénito del dios supremo Nyame. Destinado a heredar el rico reino dorado de Ashanti pero despojado por la astucia de su hermano menor Tano, Bia convirtió su exilio en un santuario impenetrable de vida salvaje y dignidad inquebrantable. Descubre el mito épico del dios fluvial que domina las riadas, protege a los linajes ribereños y demuestra que el verdadero poder reside en la soberanía de la naturaleza virgen.",
    "youtube_id": "P-W4UUuX410",
    "youtube_short_id": "ADxkFEqQo60",
    "youtube_watch_url": "https://www.youtube.com/watch?v=P-W4UUuX410",
    "youtube_short_url": "https://www.youtube.com/shorts/ADxkFEqQo60",
    "portada": "assets/images/portadas/M0007-bia.webp",
    "pagina_url": "mitologia/M0007-bia.html",
    "personajes": [
        {
            "nombre": "Bia",
            "rol": "Espíritu Abosom Fluvial de las Corrientes Indómitas y Soberano de la Selva",
            "rasgos": "Joven guerrero y sacerdote akan de 28 años, físico hercúleo y atlético, piel de ébano oscuro pulido con reflejos húmedos, adornado con sartas de cauris, piedras de río, amuletos de latón, lianas de agua dulce y faldellín kente tradicional.",
            "avatar_cabeza": "assets/images/avatars/personaje-01-bia-cabeza.webp",
            "avatar_cuerpo": "assets/images/avatars/personaje-01-bia-cuerpo.webp"
        }
    ],
    "escenas_clave": inline_scenes,
    "capitulos": [
        {
            "tiempo": "00:00",
            "segundos": 0,
            "titulo": "I. Las Aguas Sagradas de la Selva Virgen",
            "resumen": "En las profundidades boscosas entre Ghana y Costa de Marfil, nace Bia, el primogénito de Nyame y Asase Yaa, señor de las corrientes indómitas y protector del río sagrado."
        },
        {
            "tiempo": "01:10",
            "segundos": 70,
            "titulo": "II. La Arteria Nutricia y el Refugio de la Vida",
            "resumen": "Las aguas de Bia alimentan cosechas fértiles de ñame y plátano, y ofrecen un refugio inviolable para los elefantes de bosque, leopardos y comunidades ribereñas."
        },
        {
            "tiempo": "02:13",
            "segundos": 133,
            "titulo": "III. La Cólera Fluvial y el Juicio de la Verdad",
            "resumen": "Bia castiga con crecidas colosales y torrentes bermellón a quienes talan árboles sagrados, contaminan los manantiales o juran en falso ante sus aguas."
        },
        {
            "tiempo": "03:17",
            "segundos": 197,
            "titulo": "IV. La Disputa de la Primogenitura con Tano",
            "resumen": "El hermano menor Tano engaña al anciano Nyame al alba con pieles aromáticas y roba la bendición de Ashanti; Bia acepta el destierro con serenidad majestuosa sin odio fratricida."
        },
        {
            "tiempo": "04:42",
            "segundos": 282,
            "titulo": "V. El Santuario Invencible de la Naturaleza",
            "resumen": "Bia transforma su exilio en la gran Reserva de la Biosfera de Bia, demostrando que la verdadera nobleza reside en hacer florecer la vida en el corazón salvaje de la creación."
        }
    ],
    "texto_relato": narrative_text
}

# 6. Actualizar mitologia.json (en raíz y en data/)
mitologia_root = WEB_DIR / "mitologia.json"
mitologia_data = WEB_DIR / "data" / "mitologia.json"

for json_file in [mitologia_root, mitologia_data]:
    if json_file.exists():
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    # Filtrar si ya existía M0007 y anteponer
    data = [item for item in data if item.get("id") != "M0007"]
    data.insert(0, m0007)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Actualizado: {json_file}")

print("🎉 M0007 (Bia) sincronizado con éxito para la web.")
