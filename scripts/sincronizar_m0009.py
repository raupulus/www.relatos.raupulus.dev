#!/usr/bin/env python3
"""
Sincroniza M0009-kra en la web relatos.raupulus.dev:
1. Copia y convierte portada, avatares y 5 escenas a WebP (q85).
2. Lee el relato de M0009-kra.md.
3. Actualiza mitologia.json en la raíz y en data/.
"""

import json
import subprocess
import os
from pathlib import Path

RELATOS_DIR = Path("/Users/fryntiz/Library/CloudStorage/GoogleDrive-raupulus@gmail.com/Mi unidad/ia/Relatos")
WEB_DIR = Path("/Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev")
M0009_DIR = RELATOS_DIR / "Historias Mitológicas" / "africa" / "akan" / "abosom" / "M0009-kra"

# Rutas web
PUB_IMAGES = WEB_DIR / "public" / "assets" / "images"
(PUB_IMAGES / "portadas").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "avatars").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "escenas").mkdir(parents=True, exist_ok=True)

# 1. Convertir y copiar portada 16:9 a WebP (q85)
src_portada = M0009_DIR / "youtube" / "portada-es-ES.jpg"
dst_portada = PUB_IMAGES / "portadas" / "M0009-kra.webp"
subprocess.run([
    "cwebp", "-q", "85", str(src_portada), "-o", str(dst_portada)
], check=True)
print(f"✅ Portada WebP: {dst_portada}")

# 2. Convertir y copiar avatares a WebP (q85)
src_cabeza = M0009_DIR / "avatars" / "personaje-01-kra-cabeza.png"
dst_cabeza = PUB_IMAGES / "avatars" / "personaje-01-kra-cabeza.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cabeza), "-o", str(dst_cabeza)], check=True)

src_cuerpo = M0009_DIR / "avatars" / "personaje-01-kra-cuerpo.png"
dst_cuerpo = PUB_IMAGES / "avatars" / "personaje-01-kra-cuerpo.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cuerpo), "-o", str(dst_cuerpo)], check=True)
print(f"✅ Avatares WebP listos.")

# 3. Convertir y copiar 5 escenas clave a WebP (q85)
escenas_map = [
    ("003-kra-silueta-ante-trono-aureo.png", "M0009-003-kra-silueta-ante-trono-aureo.webp", "Kra, la chispa divina del alma, postrándose ante el trono áureo del Creador Nyame en la corte celestial."),
    ("008-mogya-sangre-nutricia-materna.png", "M0009-008-mogya-sangre-nutricia-materna.webp", "La madre ashanti acunando a su recién nacido, encarnando el linaje materno y la sangre nutricia mogya."),
    ("018-acecho-de-la-temible-obayifo.png", "M0009-018-acecho-de-la-temible-obayifo.webp", "El acecho de la temible criatura vampírica Obayifo en la espesura del bosque tropical acechando a las almas desprotegidas."),
    ("021-sacerdote-okrafo-lavatorio-de-alma.png", "M0009-021-sacerdote-okrafo-lavatorio-de-alma.webp", "El sacerdote okrafo con el disco de oro akrafokonmu oficiando el rito milenario de purificación del Kradware."),
    ("026-kra-ante-el-abosom-bosomtwe.png", "M0009-026-kra-ante-el-abosom-bosomtwe.webp", "El encuentro sagrado en la orilla de Lake Bosumtwi donde el alma purifica sus manos ante el dios lacustre Bosomtwe antes del ascenso final.")
]

inline_scenes = []
for src_f, dst_f, pie in escenas_map:
    s_path = M0009_DIR / "escenas" / src_f
    d_path = PUB_IMAGES / "escenas" / dst_f
    subprocess.run(["cwebp", "-q", "85", str(s_path), "-o", str(d_path)], check=True)
    inline_scenes.append({
        "archivo": f"assets/images/escenas/{dst_f}",
        "pie": pie
    })
print(f"✅ 5 escenas clave WebP listas.")

# 4. Extraer texto del relato de M0009-kra.md
relato_md = M0009_DIR / "M0009-kra.md"
relato_txt = relato_md.read_text(encoding="utf-8")
parts = relato_txt.split("## Relato")
narrative_text = parts[1].strip() if len(parts) > 1 else ""

# 5. Construir objeto M0009
m0009 = {
    "id": "M0009",
    "slug": "kra",
    "nombre": "Kra",
    "epiteto": "La Chispa Divina del Alma",
    "titulo_completo": "Kra: La Chispa Divina del Alma ⚡ Espíritus Abosom (África)",
    "region": "africa",
    "region_nombre": "África",
    "tradicion": "akan",
    "tradicion_nombre": "Mitología Akan",
    "grupo": "abosom",
    "grupo_nombre": "Espíritus Abosom",
    "estado": "estreno",
    "publicado": False,
    "palabras": 898,
    "duracion_video": "05:08",
    "duracion_audio": "05:08",
    "duracion_short": "00:53",
    "sinopsis": "En la teología mística del pueblo akan de Ghana y Costa de Marfil, la vida humana no es un simple cuerpo mortal, sino una arquitectura sagrada iluminada por el Kra: la chispa divina y aliento inmortal emanado directamente del Dios del Cielo, Nyame. Antes de nacer, cada alma comparece ante el trono del Creador para sellar su destino irrevocable (nkrabea) y consagrarse al día sagrado de la semana en que descendió a la tierra. Descubre la batalla espiritual junto a la sangre materna (mogya) y el espíritu paterno (ntoro), las asechanzas de la bruja devoradora Obayifo, el ancestral rito purificador del Kradware y el viaje supremo hacia las aguas del lago Bosumtwi donde el alma emprende su retorno a la eternidad.",
    "youtube_id": "6TRzhHRU8PY",
    "youtube_short_id": "jm6RfhFVxq0",
    "youtube_watch_url": "https://www.youtube.com/watch?v=6TRzhHRU8PY",
    "youtube_short_url": "https://www.youtube.com/shorts/jm6RfhFVxq0",
    "portada": "assets/images/portadas/M0009-kra.webp",
    "pagina_url": "mitologia/M0009-kra.html",
    "personajes": [
        {
            "nombre": "Kra",
            "rol": "La Chispa Divina del Alma y Custodio del Destino Humano",
            "rasgos": "Personificación celestial de 25 años de etnia akan, porte noble y radiante, piel de ébano lustroso que emite un sutil fulgor áureo interior, ojos con destellos dorados y ambarinos de infinita sabiduría, finos trazos ceremoniales de arcilla blanca hyire en frente y sienes, disco pectoral de oro macizo cincelado akrafokonmu sobre el pecho, y túnica ceremonial blanca inmaculada con bordados en hilo de oro.",
            "avatar_cabeza": "assets/images/avatars/personaje-01-kra-cabeza.webp",
            "avatar_cuerpo": "assets/images/avatars/personaje-01-kra-cuerpo.webp"
        }
    ],
    "escenas_clave": inline_scenes,
    "capitulos": [
        {
            "tiempo": "00:00",
            "segundos": 0,
            "titulo": "I. El Encuentro Celestial y el Nkrabea",
            "resumen": "Antes de nacer, el Kra comparece ante el trono áureo de Nyame para recibir su carácter, talentos y destino irrevocable (nkrabea)."
        },
        {
            "tiempo": "01:05",
            "segundos": 65,
            "titulo": "II. La Cuádruple Naturaleza y los Nombres Sagrados",
            "resumen": "La arquitectura cósmica del ser humano en la tradición akan: la sangre materna mogya, el espíritu paterno ntoro, la sombra sunsum y los nombres consagrados krada."
        },
        {
            "tiempo": "02:23",
            "segundos": 143,
            "titulo": "III. Las Sombras del Obayifo y el Kradware",
            "resumen": "El debilitamiento del alma por la culpa moral, el asedio de la bruja Obayifo y la restauración sagrada mediante el lavatorio ritual del Kradware oficiado por los sacerdotes okrafo."
        },
        {
            "tiempo": "03:30",
            "segundos": 210,
            "titulo": "IV. El Último Viaje y el Espejo de Bosumtwi",
            "resumen": "Al agotarse los días terrenales, el alma emprende su viaje final hacia el lago Bosumtwi para lavar sus manos y despedirse del mundo material ante el abosom lacustre."
        },
        {
            "tiempo": "04:21",
            "segundos": 261,
            "titulo": "V. El Retorno al Seno de Nyame",
            "resumen": "El ascenso del Kra purificado de regreso al firmamento para rendir testimonio ante Dios y reintegrarse a la luz eterna cósmica."
        }
    ],
    "texto_relato": narrative_text
}

# 6. Actualizar mitologia.json (en raíz, data/ y public/data/)
mitologia_root = WEB_DIR / "mitologia.json"
mitologia_data = WEB_DIR / "data" / "mitologia.json"
mitologia_pub = WEB_DIR / "public" / "data" / "mitologia.json"

for json_file in [mitologia_root, mitologia_data, mitologia_pub]:
    if json_file.exists():
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    # Filtrar si ya existía M0009 y anteponer
    data = [item for item in data if item.get("id") != "M0009"]
    data.insert(0, m0009)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Actualizado: {json_file}")

print("🎉 M0009 (Kra) sincronizado con éxito para la web.")
