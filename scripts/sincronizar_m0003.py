#!/usr/bin/env python3
"""
Sincroniza M0003-ammon-libico en la web relatos.raupulus.dev:
1. Copia y convierte portada, avatares y 5 escenas a WebP (q85).
2. Lee el relato de M0003-ammon-libico.md.
3. Actualiza mitologia.json en la raíz y en data/.
"""

import json
import subprocess
import os
from pathlib import Path

RELATOS_DIR = Path("/Users/fryntiz/Library/CloudStorage/GoogleDrive-raupulus@gmail.com/Mi unidad/ia/Relatos")
WEB_DIR = Path("/Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev")
M0003_DIR = RELATOS_DIR / "Historias Mitológicas" / "africa" / "bereber" / "dioses" / "M0003-ammon-libico"

# Rutas web
PUB_IMAGES = WEB_DIR / "public" / "assets" / "images"
(PUB_IMAGES / "portadas").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "avatars").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "escenas").mkdir(parents=True, exist_ok=True)

# 1. Convertir y copiar portada 16:9 a WebP (q85)
src_portada = M0003_DIR / "youtube" / "portada-es-ES.jpg"
dst_portada = PUB_IMAGES / "portadas" / "M0003-ammon-libico.webp"
subprocess.run([
    "cwebp", "-q", "85", str(src_portada), "-o", str(dst_portada)
], check=True)
print(f"✅ Portada WebP: {dst_portada}")

# 2. Convertir y copiar avatares a WebP (q85)
src_cabeza = M0003_DIR / "avatars" / "personaje-01-ammon-libico-cabeza.png"
dst_cabeza = PUB_IMAGES / "avatars" / "personaje-01-ammon-libico-cabeza.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cabeza), "-o", str(dst_cabeza)], check=True)

src_cuerpo = M0003_DIR / "avatars" / "personaje-01-ammon-libico-cuerpo.png"
dst_cuerpo = PUB_IMAGES / "avatars" / "personaje-01-ammon-libico-cuerpo.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cuerpo), "-o", str(dst_cuerpo)], check=True)
print(f"✅ Avatares WebP listos.")

# 3. Convertir y copiar 5 escenas clave a WebP (q85)
escenas_map = [
    ("006-manifestacion-ammon-anciano-cuernos.png", "M0003-006-manifestacion-ammon.webp", "Manifestación de Ammon líbico como anciano sagrado con cuernos espiralados de carnero."),
    ("009-fuente-del-sol-manantial-sagrado.png", "M0003-009-fuente-del-sol.webp", "La legendaria Fuente del Sol en el oasis de Siwa, manantial termal de aguas cristalinas."),
    ("020-ejercito-cambises-tragado-arenas.png", "M0003-020-ejercito-cambises-tragado.webp", "El ejército persa de Cambises sepultado por la descomunal tempestad de arena en Siwa."),
    ("028-sacerdote-oraculo-saludo-hijo-zeus.png", "M0003-028-sacerdote-oraculo-alejandro.webp", "El sacerdote de Aghurmi saludando a Alejandro Magno como hijo predilecto de Ammon."),
    ("035-manto-de-arena-sabiduria-oraculo.png", "M0003-035-manto-arena-oraculo.webp", "El silencio eterno del desierto cubriendo las ruinas milenarias del oráculo de Siwa.")
]

inline_scenes = []
for src_f, dst_f, pie in escenas_map:
    s_path = M0003_DIR / "escenas" / src_f
    d_path = PUB_IMAGES / "escenas" / dst_f
    subprocess.run(["cwebp", "-q", "85", str(s_path), "-o", str(d_path)], check=True)
    inline_scenes.append({
        "archivo": f"assets/images/escenas/{dst_f}",
        "pie": pie
    })
print(f"✅ 5 escenas clave WebP listas.")

# 4. Extraer texto del relato de M0003-ammon-libico.md
relato_md = M0003_DIR / "M0003-ammon-libico.md"
relato_txt = relato_md.read_text(encoding="utf-8")
parts = relato_txt.split("## Relato")
narrative_text = parts[1].strip() if len(parts) > 1 else ""

# 5. Construir objeto M0003
m0003 = {
    "id": "M0003",
    "slug": "ammon-libico",
    "nombre": "Ammon líbico",
    "epiteto": "El Señor del Oráculo de Siwa",
    "titulo_completo": "Ammon líbico: El Señor del Oráculo de Siwa ⚡ Dioses Bereberes (África)",
    "region": "africa",
    "region_nombre": "África",
    "tradicion": "bereber",
    "tradicion_nombre": "Mitología Bereber",
    "grupo": "dioses",
    "grupo_nombre": "Dioses Bereberes",
    "estado": "estreno",
    "publicado": False,
    "palabras": 882,
    "duracion_video": "05:31",
    "duracion_audio": "05:31",
    "duracion_short": "00:48",
    "sinopsis": "En las profundidades del desierto del Sahara, en el remoto oasis de Siwa rodeado por un mar de dunas infinitas, reinaba Ammon líbico: la majestuosa divinidad bereber con cuernos de carnero sagrado que gobernaba los manantiales de agua dulce y las profecías del desierto. Venerado por caravanas nómadas y consultado por reyes legendarios, su santuario en lo alto de la roca de Aghurmi custodiaba la voz que reveló a Alejandro Magno su destino universal.",
    "youtube_id": "jY9VEzc-kHw",
    "youtube_short_id": "nr47XD42IS0",
    "youtube_watch_url": "https://www.youtube.com/watch?v=jY9VEzc-kHw",
    "youtube_short_url": "https://www.youtube.com/shorts/nr47XD42IS0",
    "portada": "assets/images/portadas/M0003-ammon-libico.webp",
    "pagina_url": "mitologia/M0003-ammon-libico.html",
    "personajes": [
        {
            "nombre": "Ammon líbico",
            "rol": "Dios Oracular del Desierto y los Manantiales",
            "rasgos": "Anciano majestuoso de porte recio y tez curtida, mirada de sabio milenario, barba espesa de hebras oscuras y plata, grandes cuernos enroscados de carnero sagrado con anillas de bronce, túnica sahariana cruda con fíbulas de bronce, manto índigo, báculo de acacia y copa de libaciones.",
            "avatar_cabeza": "assets/images/avatars/personaje-01-ammon-libico-cabeza.webp",
            "avatar_cuerpo": "assets/images/avatars/personaje-01-ammon-libico-cuerpo.webp"
        }
    ],
    "escenas_clave": inline_scenes,
    "capitulos": [
        {
            "tiempo": "00:00",
            "segundos": 0,
            "titulo": "I. El Oasis Sagrado de Siwa",
            "resumen": "En el confín del desierto sahariano, el oasis de Siwa emerge como refugio verde custodiado por Ammon líbico, el dios con cuernos de carnero sagrado."
        },
        {
            "tiempo": "01:09",
            "segundos": 69,
            "titulo": "II. La Fuente del Sol y las Caravanas",
            "resumen": "La bendición de las aguas termales y la voz oracular en Aghurmi guían a las caravanas nómadas y resuelven litigios sin derramar sangre."
        },
        {
            "tiempo": "02:12",
            "segundos": 132,
            "titulo": "III. El Ejército Perdido de Cambises",
            "resumen": "El rey persa Cambises envía cincuenta mil guerreros a destruir el santuario; Ammon desata el siroco abrasador y los sepulta para siempre."
        },
        {
            "tiempo": "03:17",
            "segundos": 197,
            "titulo": "IV. La Revelación de Alejandro Magno",
            "resumen": "Guiado por cuervos sagrados a través del desierto, el joven rey macedonio llega al oráculo y recibe la profecía de su soberanía universal."
        },
        {
            "tiempo": "04:38",
            "segundos": 278,
            "titulo": "V. El Eco Eterno de las Arenas",
            "resumen": "El ocaso del oráculo tras la caída de imperios y la memoria inmortal del dios carnero en las arenas y en su hijo, el dios toro Gurzil."
        }
    ],
    "texto_relato": narrative_text
}

# 6. Actualizar mitologia.json
db_paths = [
    WEB_DIR / "mitologia.json",
    WEB_DIR / "data" / "mitologia.json",
    WEB_DIR / "public" / "data" / "mitologia.json"
]

for p in db_paths:
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            items = json.load(f)
    else:
        items = []

    # Reemplazar o insertar M0003
    items = [it for it in items if it.get("id") != "M0003"]
    items.append(m0003)
    # Orden descendente por ID
    items = sorted(items, key=lambda x: str(x.get("id", "")), reverse=True)

    with open(p, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"✅ Base de datos actualizada en: {p}")

print("\n🚀 ¡M0003 sincronizado exitosamente con estado estreno y assets WebP!")
