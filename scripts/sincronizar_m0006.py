#!/usr/bin/env python3
"""
Sincroniza M0006-asuo-gyebi en la web relatos.raupulus.dev:
1. Copia y convierte portada, avatares y 5 escenas a WebP (q85).
2. Lee el relato de M0006-asuo-gyebi.md.
3. Actualiza mitologia.json en la raíz y en data/.
"""

import json
import subprocess
import os
from pathlib import Path

RELATOS_DIR = Path("/Users/fryntiz/Library/CloudStorage/GoogleDrive-raupulus@gmail.com/Mi unidad/ia/Relatos")
WEB_DIR = Path("/Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev")
M0006_DIR = RELATOS_DIR / "Historias Mitológicas" / "africa" / "akan" / "abosom" / "M0006-asuo-gyebi"

# Rutas web
PUB_IMAGES = WEB_DIR / "public" / "assets" / "images"
(PUB_IMAGES / "portadas").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "avatars").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "escenas").mkdir(parents=True, exist_ok=True)

# 1. Convertir y copiar portada 16:9 a WebP (q85)
src_portada = M0006_DIR / "youtube" / "portada-es-ES.jpg"
dst_portada = PUB_IMAGES / "portadas" / "M0006-asuo-gyebi.webp"
subprocess.run([
    "cwebp", "-q", "85", str(src_portada), "-o", str(dst_portada)
], check=True)
print(f"✅ Portada WebP: {dst_portada}")

# 2. Convertir y copiar avatares a WebP (q85)
src_cabeza = M0006_DIR / "avatars" / "personaje-01-asuo-gyebi-cabeza.png"
dst_cabeza = PUB_IMAGES / "avatars" / "personaje-01-asuo-gyebi-cabeza.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cabeza), "-o", str(dst_cabeza)], check=True)

src_cuerpo = M0006_DIR / "avatars" / "personaje-01-asuo-gyebi-cuerpo.png"
dst_cuerpo = PUB_IMAGES / "avatars" / "personaje-01-asuo-gyebi-cuerpo.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cuerpo), "-o", str(dst_cuerpo)], check=True)
print(f"✅ Avatares WebP listos.")

# 3. Convertir y copiar 5 escenas clave a WebP (q85)
escenas_map = [
    ("002-tierras-altas-ghana-sabana-y-selva.png", "M0006-002-tierras-altas-ghana-sabana-y-selva.webp", "Las tierras altas de Ghana donde la sabana rojiza se funde con la selva ecuatorial y nacen las aguas sagradas."),
    ("005-guerrero-sacerdote-arcilla-blanca-hyire.png", "M0006-005-guerrero-sacerdote-arcilla-blanca-hyire.webp", "Nana Asuo Gyebi manifestado como noble sacerdote-guerrero con trazos rituales de arcilla blanca hyire."),
    ("016-trueno-y-relampago-del-dios.png", "M0006-016-trueno-y-relampago-del-dios.webp", "El trueno justiciero y el relámpago azulado que rasga el firmamento contra los hechiceros oscuros obayifo."),
    ("026-golpe-de-baston-y-tromba-purificadora.png", "M0006-026-golpe-de-baston-y-tromba-purificadora.webp", "El golpe de bastón de ceiba sobre el lecho rocoso desatando la tromba de agua purificadora que salvó a Larteh."),
    ("033-corriente-eterna-de-justicia-y-sanacion.png", "M0006-033-corriente-eterna-de-justicia-y-sanacion.webp", "La corriente eterna de justicia y sanación espiritual de Asuo Gyebi fluyendo a través de los siglos y océanos.")
]

inline_scenes = []
for src_f, dst_f, pie in escenas_map:
    s_path = M0006_DIR / "escenas" / src_f
    d_path = PUB_IMAGES / "escenas" / dst_f
    subprocess.run(["cwebp", "-q", "85", str(s_path), "-o", str(d_path)], check=True)
    inline_scenes.append({
        "archivo": f"assets/images/escenas/{dst_f}",
        "pie": pie
    })
print(f"✅ 5 escenas clave WebP listas.")

# 4. Extraer texto del relato de M0006-asuo-gyebi.md
relato_md = M0006_DIR / "M0006-asuo-gyebi.md"
relato_txt = relato_md.read_text(encoding="utf-8")
parts = relato_txt.split("## Relato")
narrative_text = parts[1].strip() if len(parts) > 1 else ""

# 5. Construir objeto M0006
m0006 = {
    "id": "M0006",
    "slug": "asuo-gyebi",
    "nombre": "Asuo Gyebi",
    "epiteto": "El Guardián Sanador de las Aguas y el Trueno Protector",
    "titulo_completo": "Asuo Gyebi: El Guardián Sanador de las Aguas ⚡ Espíritus Abosom (África)",
    "region": "africa",
    "region_nombre": "África",
    "tradicion": "akan",
    "tradicion_nombre": "Mitología Akan",
    "grupo": "abosom",
    "grupo_nombre": "Espíritus Abosom",
    "estado": "estreno",
    "publicado": False,
    "palabras": 857,
    "duracion_video": "05:22",
    "duracion_audio": "05:22",
    "duracion_short": "00:49",
    "sinopsis": "En las tierras altas de Ghana y las colinas de Larteh Akwapim rige Asuo Gyebi, la divinidad abosom de las aguas medicinales y el trueno que purifica el alma. Venerado como el médico supremo capaz de sanar fiebres mortales con arcilla blanca hyire y proteger la maternidad, este dios fluvial encarna una justicia implacable contra la hechicería oscura de los obayifo. Un relato épico de sanación, relámpagos protectores y dignidad ancestral.",
    "youtube_id": "HEVVF6iPx1o",
    "youtube_short_id": "b6uvggq9v88",
    "youtube_watch_url": "https://www.youtube.com/watch?v=HEVVF6iPx1o",
    "youtube_short_url": "https://www.youtube.com/shorts/b6uvggq9v88",
    "portada": "assets/images/portadas/M0006-asuo-gyebi.webp",
    "pagina_url": "mitologia/M0006-asuo-gyebi.html",
    "personajes": [
        {
            "nombre": "Asuo Gyebi",
            "rol": "Dios Abosom Fluvial de la Sanación, las Aguas Medicinales y el Trueno Justiciero",
            "rasgos": "Noble sacerdote-guerrero de 48 años de etnia akan, tez de ébano profundo, cabello y barba canosos, trazos de arcilla blanca ritual hyire, manto kente terroso, bastón curativo de ceiba con chispas de relámpago azul y calabaza medicinal kora.",
            "avatar_cabeza": "assets/images/avatars/personaje-01-asuo-gyebi-cabeza.webp",
            "avatar_cuerpo": "assets/images/avatars/personaje-01-asuo-gyebi-cuerpo.webp"
        }
    ],
    "escenas_clave": inline_scenes,
    "capitulos": [
        {
            "tiempo": "00:00",
            "segundos": 0,
            "titulo": "I. El Aliento Vivo de los Abosom",
            "resumen": "En las tierras altas de Ghana, de la garganta de manantiales ancestrales brotó Asuo Gyebi, señor fluvial y médico invisible de la humanidad bajo el mandato de Nyame."
        },
        {
            "tiempo": "01:12",
            "segundos": 72,
            "titulo": "II. El Médico Invisible y la Bendición del Río",
            "resumen": "Las aguas sanadoras curan fiebres con la arcilla blanca hyire; los sacerdotes okomfo y los tambores fontomfrom invocan su bendición sobre la maternidad y las cosechas."
        },
        {
            "tiempo": "02:16",
            "segundos": 136,
            "titulo": "III. El Trueno Justiciero contra los Hechiceros Obayifo",
            "resumen": "Asociado al rayo y la tormenta, el dios castiga con implacable severidad los juramentos quebrados y persigue a los brujos obayifo que acechan en las sombras."
        },
        {
            "tiempo": "03:20",
            "segundos": 200,
            "titulo": "IV. La Pestilencia Espectral de Larteh y la Tromba Purificadora",
            "resumen": "Fetiches oscuros envenenan las nacientes de Larteh; el clamor del pueblo convoca a Asuo Gyebi, cuyo golpe de bastón de ceiba desata la tromba que salva a la región."
        },
        {
            "tiempo": "04:32",
            "segundos": 272,
            "titulo": "V. La Memoria Invicta a través del Océano",
            "resumen": "Durante la trata transatlántica, la memoria del dios del río cruzó los mares hasta América, erigiéndose en bastión de resistencia espiritual y dignidad indestructible."
        }
    ],
    "texto_relato": narrative_text
}

# 6. Actualizar mitologia.json
for p in [
    WEB_DIR / "mitologia.json",
    WEB_DIR / "data" / "mitologia.json",
    WEB_DIR / "public" / "data" / "mitologia.json"
]:
    data = []
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []

    # Filtrar si ya existe M0006
    data = [item for item in data if item.get("id") != "M0006"]
    # Insertar al principio para mantener orden descendente
    data.insert(0, m0006)

    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Guardado en {p}")

print("\n🎉 M0006-asuo-gyebi sincronizado exitosamente en la web!")
