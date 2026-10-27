#!/usr/bin/env python3
"""
Sincroniza M0005-asase-yaa en la web relatos.raupulus.dev:
1. Copia y convierte portada, avatares y 5 escenas a WebP (q85).
2. Lee el relato de M0005-asase-yaa.md.
3. Actualiza mitologia.json en la raíz y en data/.
"""

import json
import subprocess
import os
from pathlib import Path

RELATOS_DIR = Path("/Users/fryntiz/Library/CloudStorage/GoogleDrive-raupulus@gmail.com/Mi unidad/ia/Relatos")
WEB_DIR = Path("/Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev")
M0005_DIR = RELATOS_DIR / "Historias Mitológicas" / "africa" / "akan" / "abosom" / "M0005-asase-yaa"

# Rutas web
PUB_IMAGES = WEB_DIR / "public" / "assets" / "images"
(PUB_IMAGES / "portadas").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "avatars").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "escenas").mkdir(parents=True, exist_ok=True)

# 1. Convertir y copiar portada 16:9 a WebP (q85)
src_portada = M0005_DIR / "youtube" / "portada-es-ES.jpg"
dst_portada = PUB_IMAGES / "portadas" / "M0005-asase-yaa.webp"
subprocess.run([
    "cwebp", "-q", "85", str(src_portada), "-o", str(dst_portada)
], check=True)
print(f"✅ Portada WebP: {dst_portada}")

# 2. Convertir y copiar avatares a WebP (q85)
src_cabeza = M0005_DIR / "avatars" / "personaje-01-asase-yaa-cabeza.png"
dst_cabeza = PUB_IMAGES / "avatars" / "personaje-01-asase-yaa-cabeza.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cabeza), "-o", str(dst_cabeza)], check=True)

src_cuerpo = M0005_DIR / "avatars" / "personaje-01-asase-yaa-cuerpo.png"
dst_cuerpo = PUB_IMAGES / "avatars" / "personaje-01-asase-yaa-cuerpo.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cuerpo), "-o", str(dst_cuerpo)], check=True)
print(f"✅ Avatares WebP listos.")

# 3. Convertir y copiar 5 escenas clave a WebP (q85)
escenas_map = [
    ("003-nyame-y-asase-yaa-cielo-y-tierra.png", "M0005-003-nyame-y-asase-yaa-cielo-y-tierra.webp", "El firmamento de Nyame y la tierra fértil de Asase Yaa encontrándose en el horizonte místico."),
    ("004-matrona-venerable-tez-arcillosa.png", "M0005-004-matrona-venerable-tez-arcillosa.webp", "Asase Yaa, matrona venerable de tez arcillosa, trenzas con cuentas de barro y manto kente."),
    ("010-campesinos-ofrendan-primicias.png", "M0005-010-campesinos-ofrendan-primicias.webp", "Campesinos akan depositando ofrendas de primicias sobre la tierra sagrada en acción de gracias."),
    ("024-temblor-y-fractura-con-vapor-rojo.png", "M0005-024-temblor-y-fractura-con-vapor-rojo.webp", "La tierra partiéndose con estruendo telúrico y vapores bermellones ante la profanación del reposo sagrado."),
    ("031-ciclo-existencia-humana-y-retorno.png", "M0005-031-ciclo-existencia-humana-y-retorno.webp", "El ciclo sagrado de la existencia y el retorno de los antepasados asamanfo al seno eterno de la Madre Tierra.")
]

inline_scenes = []
for src_f, dst_f, pie in escenas_map:
    s_path = M0005_DIR / "escenas" / src_f
    d_path = PUB_IMAGES / "escenas" / dst_f
    subprocess.run(["cwebp", "-q", "85", str(s_path), "-o", str(d_path)], check=True)
    inline_scenes.append({
        "archivo": f"assets/images/escenas/{dst_f}",
        "pie": pie
    })
print(f"✅ 5 escenas clave WebP listas.")

# 4. Extraer texto del relato de M0005-asase-yaa.md
relato_md = M0005_DIR / "M0005-asase-yaa.md"
relato_txt = relato_md.read_text(encoding="utf-8")
parts = relato_txt.split("## Relato")
narrative_text = parts[1].strip() if len(parts) > 1 else ""

# 5. Construir objeto M0005
m0005 = {
    "id": "M0005",
    "slug": "asase-yaa",
    "nombre": "Asase Yaa",
    "epiteto": "Madre de la Tierra y la Verdad",
    "titulo_completo": "Asase Yaa: La Madre de la Tierra y la Verdad ⚡ Espíritus Abosom (África)",
    "region": "africa",
    "region_nombre": "África",
    "tradicion": "akan",
    "tradicion_nombre": "Mitología Akan",
    "grupo": "abosom",
    "grupo_nombre": "Espíritus Abosom",
    "estado": "estreno",
    "publicado": False,
    "palabras": 888,
    "duracion_video": "05:34",
    "duracion_audio": "05:34",
    "duracion_short": "00:50",
    "sinopsis": "En el corazón espiritual del pueblo akan de África occidental, Asase Yaa reina como la gran Madre Tierra: el seno fértil que nutre a los vivos y la morada eterna que acoge a los antepasados asamanfo. Consorte cósmica de Nyame, el dios supremo del cielo, ella encarna la justicia incorruptible, la verdad moral y el orden sagrado del universo. Cada jueves, la tierra reclama reposo absoluto: profanar su descanso despierta la sequía y el juicio de los ancestros.",
    "youtube_id": "hXRojVxzKRQ",
    "youtube_short_id": "SpUj3rAycIU",
    "youtube_watch_url": "https://www.youtube.com/watch?v=hXRojVxzKRQ",
    "youtube_short_url": "https://www.youtube.com/shorts/SpUj3rAycIU",
    "portada": "assets/images/portadas/M0005-asase-yaa.webp",
    "pagina_url": "mitologia/M0005-asase-yaa.html",
    "personajes": [
        {
            "nombre": "Asase Yaa",
            "rol": "Diosa Primordial de la Tierra, la Verdad y la Agricultura",
            "rasgos": "Matrona noble y venerable de etnia akan, tez de ébano profundo con cálidos matices de terracota, trenzas tradicionales con cuentas de arcilla y oro, vestida con manto kente bermellón y collar de cauris.",
            "avatar_cabeza": "assets/images/avatars/personaje-01-asase-yaa-cabeza.webp",
            "avatar_cuerpo": "assets/images/avatars/personaje-01-asase-yaa-cuerpo.webp"
        },
        {
            "nombre": "Kwabena",
            "rol": "Cazador y Agricultor Ashanti",
            "rasgos": "Joven fornido de piel oscura curtida por el sol africano, sayal corto de cuero de antílope y azadón de hierro, postrado en reverente sobrecogimiento.",
            "avatar_cabeza": "assets/images/avatars/personaje-01-asase-yaa-cabeza.webp",
            "avatar_cuerpo": "assets/images/avatars/personaje-01-asase-yaa-cuerpo.webp"
        }
    ],
    "escenas_clave": inline_scenes,
    "capitulos": [
        {
            "tiempo": "00:00",
            "segundos": 0,
            "titulo": "I. El Vientre Fértil y la Madre Silenciosa",
            "resumen": "En el corazón espiritual del pueblo akan, Asase Yaa reina como la gran Madre Tierra que nutre a los vivos y acoge a los antepasados."
        },
        {
            "tiempo": "01:05",
            "segundos": 65,
            "titulo": "II. El Matrimonio Cósmico y el Día Sagrado de la Tierra",
            "resumen": "Consorte cósmica de Nyame, dios supremo del cielo, ella exige el reposo sagrado de los jueves (Yawoada) sin azadones ni heridas sobre el suelo."
        },
        {
            "tiempo": "02:08",
            "segundos": 128,
            "titulo": "III. El Juicio Postmortem y los Antepasados Asamanfo",
            "resumen": "Diosa de la verdad moral y la justicia comunitaria; ante ella se jura descalzo y en su seno descansan las almas de los justos."
        },
        {
            "tiempo": "03:17",
            "segundos": 197,
            "titulo": "IV. La Maldición de la Codicia y la Profanación",
            "resumen": "Cuando la sangre inocente o la codicia humana mancillan la tierra, la sequía y la esterilidad azotan a las aldeas infractoras."
        },
        {
            "tiempo": "04:43",
            "segundos": 283,
            "titulo": "V. El Tabú Roto y la Verdad Incorruptible",
            "resumen": "El cazador Kwabena profana el bosque sagrado durante la sequía, y tras el juicio divino y la expiación, brota el manantial que salva al pueblo."
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

    # Filtrar si ya existe M0005
    data = [item for item in data if item.get("id") != "M0005"]
    # Insertar al principio para mantener orden descendente
    data.insert(0, m0005)

    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Guardado en {p}")

print("\n🎉 M0005-asase-yaa sincronizado exitosamente en la web!")
