#!/usr/bin/env python3
"""
Sincroniza M0013-obayifo en la web relatos.raupulus.dev:
1. Copia y convierte portada, avatares y 5 escenas a WebP (q85).
2. Lee el relato de M0013-obayifo.md.
3. Actualiza mitologia.json en la raíz, data/ y public/data/.
"""

import json
import subprocess
import os
from pathlib import Path

RELATOS_DIR = Path("/Users/fryntiz/Library/CloudStorage/GoogleDrive-raupulus@gmail.com/Mi unidad/ia/Relatos")
WEB_DIR = Path("/Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev")
M0013_DIR = RELATOS_DIR / "Historias Mitológicas" / "africa" / "akan" / "abosom" / "M0013-obayifo"

# Rutas web
PUB_IMAGES = WEB_DIR / "public" / "assets" / "images"
(PUB_IMAGES / "portadas").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "avatars").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "escenas").mkdir(parents=True, exist_ok=True)

# 1. Convertir y copiar portada 16:9 a WebP (q85)
src_portada = M0013_DIR / "youtube" / "portada-es-ES.jpg"
dst_portada = PUB_IMAGES / "portadas" / "M0013-obayifo.webp"
subprocess.run([
    "cwebp", "-q", "85", str(src_portada), "-o", str(dst_portada)
], check=True)
print(f"✅ Portada WebP: {dst_portada}")

# 2. Convertir y copiar avatares a WebP (q85)
src_cabeza = M0013_DIR / "avatars" / "personaje-01-obayifo-cabeza.png"
dst_cabeza = PUB_IMAGES / "avatars" / "personaje-01-obayifo-cabeza.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cabeza), "-o", str(dst_cabeza)], check=True)

src_cuerpo = M0013_DIR / "avatars" / "personaje-01-obayifo-cuerpo.png"
dst_cuerpo = PUB_IMAGES / "avatars" / "personaje-01-obayifo-cuerpo.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cuerpo), "-o", str(dst_cuerpo)], check=True)
print(f"✅ Avatares WebP listos.")

# 3. Convertir y copiar 5 escenas clave a WebP (q85)
escenas_map = [
    ("005-fuego-prohibido-del-bayi-corazon.png", "M0013-005-fuego-prohibido-del-bayi-corazon.webp", "El fuego prohibido del bayi latiendo en el pecho de la bruja, magia oscura alimentada por la envidia y la sed de destrucción."),
    ("010-cuerpo-durmiente-y-alma-desprendida.png", "M0013-010-cuerpo-durmiente-y-alma-desprendida.webp", "El desprendimiento espiritual a medianoche: mientras el cuerpo físico yace dormido en la estera, el alma transmuta en una fiera alada."),
    ("013-lumbre-sulfurosa-axilas-y-boca.png", "M0013-013-lumbre-sulfurosa-axilas-y-boca.webp", "La temida fosforescencia sulfurosa y escarlata brotando intensamente de las axilas y boca entreabierta de la Obayifo en su vuelo nocturno."),
    ("024-penetracion-secreta-pimienta-y-sal.png", "M0013-024-penetracion-secreta-pimienta-y-sal.webp", "El sanador tradicional Kofi Mensah espolvoreando sal marina consagrada y pimienta roja molida sobre la estera de la bruja dormida."),
    ("026-aullido-desgarrador-desvanecimiento-en-humo.png", "M0013-026-aullido-desgarrador-desvanecimiento-en-humo.webp", "La criatura atrapada entre dos mundos y aullando en agonía al alba, disolviéndose en humo acre ante la mirada atónita de los ancianos.")
]

inline_scenes = []
for src_f, dst_f, pie in escenas_map:
    s_path = M0013_DIR / "escenas" / src_f
    d_path = PUB_IMAGES / "escenas" / dst_f
    subprocess.run(["cwebp", "-q", "85", str(s_path), "-o", str(d_path)], check=True)
    inline_scenes.append({
        "archivo": f"assets/images/escenas/{dst_f}",
        "pie": pie
    })
print(f"✅ 5 escenas clave WebP listas.")

# 4. Extraer texto del relato de M0013-obayifo.md
relato_md = M0013_DIR / "M0013-obayifo.md"
relato_txt = relato_md.read_text(encoding="utf-8")
parts = relato_txt.split("## Relato")
narrative_text = parts[1].strip() if len(parts) > 1 else ""

# 5. Construir objeto M0013
m0013 = {
    "id": "M0013",
    "slug": "obayifo",
    "nombre": "Obayifo",
    "epiteto": "El Vampiro Brujo de la Noche y Fuego de las Sombras",
    "titulo_completo": "Obayifo: El Vampiro Brujo de la Noche y Fuego de las Sombras ⚡ Deidades y Espíritus (Mitología Ashanti y Akan)",
    "region": "africa",
    "region_nombre": "África",
    "tradicion": "akan",
    "tradicion_nombre": "Mitología Akan",
    "grupo": "abosom",
    "grupo_nombre": "Deidades y Espíritus",
    "estado": "estreno",
    "publicado": False,
    "palabras": 842,
    "duracion_video": "05:06",
    "duracion_audio": "05:06",
    "duracion_short": "00:46",
    "sinopsis": "En el folclore y la mitología de los pueblos akan y ashanti de Ghana y Costa de Marfil, la Obayifo es la manifestación más temida de la brujería destructiva (bayi). Lejos de ocultarse en selvas remotas, camina de día como una vecina ordinaria en la propia aldea. A medianoche, su espíritu se desprende de la carne como una fiera alada que despide fuego sulfuroso por las axilas y boca, sobrevolando las chozas para succionar la energía vital (sunsum) de los recién nacidos y marchitar cosechas, hasta que el sabio sanador Kofi Mensah logra tenderle la legendaria trampa de sal marina y pimienta sagrada.",
    "youtube_id": "zeJ4eeaPtWc",
    "youtube_short_id": "zqt3eaUkF6w",
    "youtube_watch_url": "https://www.youtube.com/watch?v=zeJ4eeaPtWc",
    "youtube_short_url": "https://www.youtube.com/shorts/zqt3eaUkF6w",
    "portada": "assets/images/portadas/M0013-obayifo.webp",
    "pagina_url": "mitologia/M0013-obayifo.html",
    "personajes": [
        {
            "nombre": "Obayifo / Akua Mansa",
            "rol": "La Bruja Vampírica de la Noche",
            "rasgos": "Mujer de 58 años de fisonomía curtida por el sol ecuatorial, porte enjuto y mirada penetrante de fría intensidad. En su aspecto diurno viste pañuelo de cabeza sobrio y telas tradicionales descoloridas. De noche transmuta en una figura espectral alada con piel de ébano violáceo, ojos encendidos como brasas rojizas, garras curvadas y una fosforescencia sulfurosa y escarlata que mana de sus axilas y boca.",
            "avatar_cabeza": "assets/images/avatars/personaje-01-obayifo-cabeza.webp",
            "avatar_cuerpo": "assets/images/avatars/personaje-01-obayifo-cuerpo.webp"
        },
        {
            "nombre": "Kofi Mensah",
            "rol": "Sanador Tradicional y Cazador de Brujas (Odunsifo)",
            "rasgos": "Curandero y guardián espiritual de 42 años, de complexión atlética y mirada vigilante. Viste túnica de cazador batakari oscura con amuletos sagrados suman, cuernos de antílope tallados con hierbas medicinales y machete ceremonial consagrado para neutralizar las artes oscuras."
        },
        {
            "nombre": "Nana Yaa Pokua",
            "rol": "Madre Protectora del Linaje",
            "rasgos": "Joven madre ashanti de 24 años, de porte digno y rostro dulce ensombrecido por la angustia. Viste saya tradicional de algodón en tonos ocres y sostiene en brazos a su recién nacido envuelto en tela bendecida con conchas de cauri."
        }
    ],
    "escenas_clave": inline_scenes,
    "capitulos": [
        {
            "tiempo": "00:00",
            "segundos": 0,
            "titulo": "I. Apertura: El Vampiro de la Noche",
            "resumen": "La amenaza silenciosa y perversa del bayi que acecha las aldeas ashanti al caer el sol."
        },
        {
            "tiempo": "01:12",
            "segundos": 72,
            "titulo": "II. Metamorfosis: El Fuego Siniestro del Bayi",
            "resumen": "El espíritu corrompido se desprende del cuerpo durmiente y transmuta en una fiera alada que despide lumbre fosforescente por axilas y boca."
        },
        {
            "tiempo": "02:08",
            "segundos": 128,
            "titulo": "III. El Hambre Devoradora: Robo de Sangre y Cosechas",
            "resumen": "Filtrándose por las rendijas de paja, la criatura drena la energía vital (sunsum) de los recién nacidos y arruina las cosechas de ñame."
        },
        {
            "tiempo": "03:09",
            "segundos": 189,
            "titulo": "IV. El Enfrentamiento: La Trampa de Sal y Pimienta",
            "resumen": "El sanador Kofi Mensah cubre el cuerpo dormido de la bruja con sal consagrada y pimienta roja, impidiendo su reingreso espiritual al alba."
        },
        {
            "tiempo": "04:15",
            "segundos": 255,
            "titulo": "V. Legado y Vigilancia: La Moral Akan",
            "resumen": "Amuletos suman protectores y la lección ética de los ancianos: la verdadera oscuridad nace de la codicia y el rencor en el corazón humano."
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

    # Filtrar si ya existía M0013 y anteponer (orden descendente)
    data = [item for item in data if item.get("id") != "M0013"]
    data.insert(0, m0013)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Actualizado: {json_file}")

print("🎉 M0013 (Obayifo) sincronizado con éxito para la web.")
