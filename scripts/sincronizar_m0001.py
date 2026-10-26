#!/usr/bin/env python3
"""
Sincroniza M0001-amaunet en la web relatos.raupulus.dev:
1. Copia y convierte portada, avatares y 5 escenas a WebP (q85).
2. Lee el relato de M0001-amaunet.md.
3. Actualiza mitologia.json en la raíz y en data/.
"""

import json
import subprocess
import os
from pathlib import Path

RELATOS_DIR = Path("/Users/fryntiz/Library/CloudStorage/GoogleDrive-raupulus@gmail.com/Mi unidad/ia/Relatos")
WEB_DIR = Path("/Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev")
M0001_DIR = RELATOS_DIR / "Historias Mitológicas" / "africa" / "egipto" / "cosmogonia" / "M0001-amaunet"

# Rutas web
PUB_IMAGES = WEB_DIR / "public" / "assets" / "images"
(PUB_IMAGES / "portadas").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "avatars").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "escenas").mkdir(parents=True, exist_ok=True)

# 1. Convertir y copiar portada 16:9 a WebP (q85)
src_portada = M0001_DIR / "youtube" / "portada-es-ES.jpg"
dst_portada = PUB_IMAGES / "portadas" / "M0001-amaunet.webp"
subprocess.run([
    "cwebp", "-q", "85", str(src_portada), "-o", str(dst_portada)
], check=True)
print(f"✅ Portada WebP: {dst_portada}")

# 2. Convertir y copiar avatares a WebP (q85)
src_cabeza = M0001_DIR / "avatars" / "personaje-01-amaunet-cabeza.png"
dst_cabeza = PUB_IMAGES / "avatars" / "personaje-01-amaunet-cabeza.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cabeza), "-o", str(dst_cabeza)], check=True)

src_cuerpo = M0001_DIR / "avatars" / "personaje-01-amaunet-cuerpo.png"
dst_cuerpo = PUB_IMAGES / "avatars" / "personaje-01-amaunet-cuerpo.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cuerpo), "-o", str(dst_cuerpo)], check=True)
print(f"✅ Avatares WebP listos.")

# 3. Convertir y copiar 5 escenas clave a WebP (q85)
escenas_map = [
    ("004-ocho-divinidades-caos-amaunet.png", "M0001-004-ocho-divinidades.webp", "Las ocho fuerzas primordiales de la Ogdóada en las aguas negras del abismo de Hermópolis."),
    ("011-bajorrelieves-luxor-coronacion.png", "M0001-011-bajorrelieves-luxor.webp", "Amaunet extendiendo su manto protector sobre el faraón durante la coronación en Lúxor."),
    ("016-capuchon-cobra-tormenta-arena.png", "M0001-016-capuchon-cobra.webp", "El rostro sombrío de la señora del viento invisible con el capuchón de cobra desplegado."),
    ("023-primer-soplo-sagrado-amaunet.png", "M0001-023-primer-soplo.webp", "El primer soplo sagrado de Amaunet desgarrando la inmovilidad de las aguas primordiales."),
    ("027-nacimiento-loto-nino-solar.png", "M0001-027-loto-solar.webp", "El nacimiento del niño solar emergiendo del loto primordial sobre la Colina de las Llamas.")
]

inline_scenes = []
for src_f, dst_f, pie in escenas_map:
    s_path = M0001_DIR / "escenas" / src_f
    d_path = PUB_IMAGES / "escenas" / dst_f
    subprocess.run(["cwebp", "-q", "85", str(s_path), "-o", str(d_path)], check=True)
    inline_scenes.append({
        "archivo": f"assets/images/escenas/{dst_f}",
        "pie": pie
    })
print(f"✅ 5 escenas clave WebP listas.")

# 4. Extraer texto del relato de M0001-amaunet.md
relato_md = M0001_DIR / "M0001-amaunet.md"
relato_txt = relato_md.read_text(encoding="utf-8")
parts = relato_txt.split("## Relato")
narrative_text = parts[1].strip() if len(parts) > 1 else ""

# 5. Construir objeto M0001
m0001 = {
    "id": "M0001",
    "slug": "amaunet",
    "nombre": "Amaunet",
    "epiteto": "La Madre del Viento Invisible",
    "titulo_completo": "Amaunet: La Madre del Viento Invisible ⚡ Cosmogonía (Egipto)",
    "region": "africa",
    "region_nombre": "África",
    "tradicion": "egipto",
    "tradicion_nombre": "Mitología Egipcia",
    "grupo": "cosmogonia",
    "grupo_nombre": "Cosmogonía Egipcia",
    "estado": "publicado",
    "publicado": True,
    "palabras": 871,
    "duracion_video": "05:16",
    "duracion_audio": "05:16",
    "duracion_short": "00:47",
    "sinopsis": "Mucho antes de que existieran las arenas de Egipto o el fuego del sol de Ra, en el océano negro de Nun reinaba la Ogdóada de Hermópolis. Entre las ocho fuerzas primordiales se alzaba Amaunet, «La Oculta», la diosa cobra que custodiaba el aliento invisible capaz de agitar el abismo y alumbrar el loto de la creación.",
    "youtube_id": "Trx75TFfYYA",
    "youtube_short_id": "i7nThsRILoo",
    "youtube_watch_url": "https://www.youtube.com/watch?v=Trx75TFfYYA",
    "youtube_short_url": "https://www.youtube.com/shorts/i7nThsRILoo",
    "portada": "assets/images/portadas/M0001-amaunet.webp",
    "pagina_url": "mitologia/M0001-amaunet.html",
    "personajes": [
        {
            "nombre": "Amaunet",
            "rol": "Diosa Primordial de lo Oculto",
            "rasgos": "Cuerpo esbelto de mujer en lino blanco transparente, cabeza de cobra real con escamas verde esmeralda y oro, ojos de ámbar, diadema uraeus, collar usekh, cetro de papiro y anj dorado.",
            "avatar_cabeza": "assets/images/avatars/personaje-01-amaunet-cabeza.webp",
            "avatar_cuerpo": "assets/images/avatars/personaje-01-amaunet-cuerpo.webp"
        }
    ],
    "capitulos": [
        {"tiempo": "00:00", "segundos": 0, "titulo": "I. El Abismo de Hermópolis y el Nombre de «La Oculta»", "resumen": "El océano primordial Nun antes del tiempo y las ocho deidades de la Ogdóada."},
        {"tiempo": "01:10", "segundos": 70, "titulo": "II. El Aliento de la Vida y la Madre de los Faraones", "resumen": "Amaunet como soplo vital que recorre las aguas y ampara a los reyes en Lúxor."},
        {"tiempo": "02:15", "segundos": 135, "titulo": "III. La Sombra del Vacío y el Destierro en Tebas", "resumen": "El temor al vacío, la cabeza de cobra implacable y su sustitución política por la diosa Mut."},
        {"tiempo": "03:26", "segundos": 206, "titulo": "IV. El Primer Suspiro y el Nacimiento del Sol", "resumen": "Amaunet agita las aguas de Nun y hace emerger la Colina de las Llamas y el loto solar."},
        {"tiempo": "04:37", "segundos": 277, "titulo": "V. El Eco Eterno entre las Columnas de Lúxor", "resumen": "El retiro bajo Medinet Habu y el viento invisible que aún susurra en los templos del Nilo."}
    ],
    "texto_relato": narrative_text,
    "escenas_intercaladas": inline_scenes
}

# 6. Guardar en mitologia.json (raíz y data/)
mitologia = [m0001]
with open(WEB_DIR / "mitologia.json", "w", encoding="utf-8") as f:
    json.dump(mitologia, f, ensure_ascii=False, indent=2)

with open(WEB_DIR / "data" / "mitologia.json", "w", encoding="utf-8") as f:
    json.dump(mitologia, f, ensure_ascii=False, indent=2)

print("✅ mitologia.json actualizado con M0001-amaunet.")
