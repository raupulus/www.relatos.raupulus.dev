#!/usr/bin/env python3
"""
Sincroniza M0014-odomankoma en la web relatos.raupulus.dev:
1. Copia y convierte portada, avatares y 5 escenas a WebP (q85).
2. Lee el relato de M0014-odomankoma.md.
3. Actualiza mitologia.json en la raíz, data/ y public/data/.
"""

import json
import subprocess
import os
from pathlib import Path

RELATOS_DIR = Path("/Users/fryntiz/Library/CloudStorage/GoogleDrive-raupulus@gmail.com/Mi unidad/ia/Relatos")
WEB_DIR = Path("/Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev")
M0014_DIR = RELATOS_DIR / "Historias Mitológicas" / "africa" / "akan" / "abosom" / "M0014-odomankoma"

# Rutas web
PUB_IMAGES = WEB_DIR / "public" / "assets" / "images"
(PUB_IMAGES / "portadas").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "avatars").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "escenas").mkdir(parents=True, exist_ok=True)

# 1. Convertir y copiar portada 16:9 a WebP (q85)
src_portada = M0014_DIR / "youtube" / "portada-es-ES.jpg"
dst_portada = PUB_IMAGES / "portadas" / "M0014-odomankoma.webp"
subprocess.run([
    "cwebp", "-q", "85", str(src_portada), "-o", str(dst_portada)
], check=True)
print(f"✅ Portada WebP: {dst_portada}")

# 2. Convertir y copiar avatares a WebP (q85)
src_cabeza = M0014_DIR / "avatars" / "personaje-01-odomankoma-cabeza.png"
dst_cabeza = PUB_IMAGES / "avatars" / "personaje-01-odomankoma-cabeza.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cabeza), "-o", str(dst_cabeza)], check=True)

src_cuerpo = M0014_DIR / "avatars" / "personaje-01-odomankoma-cuerpo.png"
dst_cuerpo = PUB_IMAGES / "avatars" / "personaje-01-odomankoma-cuerpo.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cuerpo), "-o", str(dst_cuerpo)], check=True)
print(f"✅ Avatares WebP listos.")

# 3. Convertir y copiar 5 escenas clave a WebP (q85)
escenas_map = [
    ("005-dedos-luminosos-modelando-firmamento.png", "M0014-005-dedos-luminosos-modelando-firmamento.webp", "Los dedos luminosos de Odomankoma despidiendo chispas de luz al modelar la bóveda celeste y separar las tinieblas primordiales."),
    ("010-emanacion-de-los-espiritus-abosom.png", "M0014-010-emanacion-de-los-espiritus-abosom.webp", "Emanación de los espíritus tutelares abosom desde el hálito creador, poblando ríos sagrados, ceibas milenarias y montañas."),
    ("014-moldeando-primeros-mortales-arcilla-roja.png", "M0014-014-moldeando-primeros-mortales-arcilla-roja.webp", "El demiurgo Borebore modelando pacientemente a los primeros seres humanos con la arcilla roja de la tierra fértil."),
    ("021-creacion-de-owuo-muerte-primordial.png", "M0014-021-creacion-de-owuo-muerte-primordial.webp", "La concepción de Owuo, la Muerte primordial, fuerza cósmica creada para impedir el estancamiento eterno y asegurar la renovación viva."),
    ("029-maestro-nana-kwame-tocando-atumpan.png", "M0014-029-maestro-nana-kwame-tocando-atumpan.webp", "El maestro percusionista Nana Kwame Ampofo haciendo resonar los sagrados tambores atumpan con los proverbios del Creador.")
]

inline_scenes = []
for src_f, dst_f, pie in escenas_map:
    s_path = M0014_DIR / "escenas" / src_f
    d_path = PUB_IMAGES / "escenas" / dst_f
    subprocess.run(["cwebp", "-q", "85", str(s_path), "-o", str(d_path)], check=True)
    inline_scenes.append({
        "archivo": f"assets/images/escenas/{dst_f}",
        "pie": pie
    })
print(f"✅ 5 escenas clave WebP listas.")

# 4. Extraer texto del relato de M0014-odomankoma.md
relato_md = M0014_DIR / "M0014-odomankoma.md"
relato_txt = relato_md.read_text(encoding="utf-8")
parts = relato_txt.split("## Relato")
narrative_text = parts[1].strip() if len(parts) > 1 else ""

# 5. Construir objeto M0014
m0014 = {
    "id": "M0014",
    "slug": "odomankoma",
    "nombre": "Odomankoma",
    "epiteto": "El Arquitecto Cósmico y el Creador Infinito",
    "titulo_completo": "Odomankoma: El Arquitecto Cósmico y el Creador Infinito ⚡ Deidades y Espíritus (Mitología Ashanti y Akan)",
    "region": "africa",
    "region_nombre": "África",
    "tradicion": "akan",
    "tradicion_nombre": "Mitología Akan",
    "grupo": "abosom",
    "grupo_nombre": "Deidades y Espíritus",
    "estado": "estreno",
    "publicado": False,
    "palabras": 857,
    "duracion_video": "05:17",
    "duracion_audio": "05:17",
    "duracion_short": "00:49",
    "sinopsis": "En la teología y cosmogonía de los pueblos akan y ashanti de Ghana y Costa de Marfil, Odomankoma es el demiurgo primordial, el arquitecto infinito y el hacedor supremo (Borebore) que modeló la materia del universo a partir del caos inicial. Venerado en los proverbios milenarios de los tambores sagrados atumpan, esculpió el firmamento, trazó los ríos sagrados y moldeó a los primeros seres humanos con la arcilla de la tierra. Pero en el misterio más hondo del pensamiento akan, Odomankoma también creó a la Muerte (Owuo) para asegurar la renovación del mundo, disolviendo voluntariamente su aliento visible en el tejido cósmico para fundirse para siempre con el corazón infinito de su propia creación.",
    "youtube_id": "EzWz2WFlIzo",
    "youtube_short_id": "YTSfnhSAdNI",
    "youtube_watch_url": "https://www.youtube.com/watch?v=EzWz2WFlIzo",
    "youtube_short_url": "https://www.youtube.com/shorts/YTSfnhSAdNI",
    "portada": "assets/images/portadas/M0014-odomankoma.webp",
    "pagina_url": "mitologia/M0014-odomankoma.html",
    "personajes": [
        {
            "nombre": "Odomankoma (Borebore)",
            "rol": "El Arquitecto Infinito y Escultor Cósmico",
            "rasgos": "Deidad creadora monumental de 55 años de edad aparente, porte mayestático de patriarca y sabio artífice africano. Posee una piel de ébano oscuro lustroso recorrida por finos trazos y relieves fosforescentes dorados que emulan las constelaciones y los símbolos Adinkra de la eternidad. Sus manos terminan en yemas luminosas que despiden chispas de luz al modelar la materia. Viste una toga imperial kente en oro resplandeciente, azul cobalto y carmesí sobre el hombro izquierdo, y empuña una azuela de escultor (osese) de oro macizo labrada con glifos solares.",
            "avatar_cabeza": "assets/images/avatars/personaje-01-odomankoma-cabeza.webp",
            "avatar_cuerpo": "assets/images/avatars/personaje-01-odomankoma-cuerpo.webp"
        },
        {
            "nombre": "Nana Kwame Ampofo",
            "rol": "Maestro Percusionista y Guardián del Tambor Atumpan",
            "rasgos": "Sabio orador y maestro percusionista de 52 años, de complexión atlética y mirada serena imbuida de memoria ancestral. Viste paños tradicionales oscuros de algodón kuntunkuni ceñidos a la cintura y brazaletes de cuero consagrado con cuentas de latón. Es el custodio de la poesía de tambor que recita las alabanzas eternas de Odomankoma."
        },
        {
            "nombre": "Owuo",
            "rol": "La Muerte Primordial y el Ciclo de la Renovación",
            "rasgos": "Personificación mítica de la Muerte en el folclore akan, figura espectral y solemne envuelta en ropajes de bruma grisácea y polvo de ceniza sagrada. Su presencia no es la de un demonio vengativo, sino la fuerza inexorable del cosmos creada por Odomankoma para disolver las formas agotadas y permitir que la vida renazca sin cesar."
        }
    ],
    "escenas_clave": inline_scenes,
    "capitulos": [
        {
            "tiempo": "00:00",
            "segundos": 0,
            "titulo": "I. El Despertar del Gran Escultor",
            "resumen": "La deidad primordial surge del silencio abisal para concebir el orden del universo."
        },
        {
            "tiempo": "01:10",
            "segundos": 70,
            "titulo": "II. La Talla del Mundo y los Abosom",
            "resumen": "Con su azuela dorada osese, Odomankoma labra el firmamento, los ríos sagrados y emanan los espíritus tutelares abosom."
        },
        {
            "tiempo": "02:18",
            "segundos": 138,
            "titulo": "III. La Creación de la Humanidad",
            "resumen": "El modelado paciente de los primeros seres humanos con la arcilla roja de la tierra fértil antes de recibir el soplo vital del kra."
        },
        {
            "tiempo": "03:22",
            "segundos": 202,
            "titulo": "IV. El Misterio de Owuo y la Disolución Cósmica",
            "resumen": "La creación de la Muerte para impedir el estancamiento eterno y la disolución voluntaria del artífice en su propia obra."
        },
        {
            "tiempo": "04:22",
            "segundos": 262,
            "titulo": "V. El Eco Eterno del Atumpan",
            "resumen": "La memoria viva en los tambores parlantes ashanti y en los taburetes sesedro como santuarios del espíritu creador."
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

    # Filtrar si ya existía M0014 y anteponer (orden descendente)
    data = [item for item in data if item.get("id") != "M0014"]
    data.insert(0, m0014)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Actualizado: {json_file}")

print("🎉 M0014 (Odomankoma) sincronizado con éxito para la web.")
