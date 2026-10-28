#!/usr/bin/env python3
"""
Sincroniza M0008-bosomtwe en la web relatos.raupulus.dev:
1. Copia y convierte portada, avatares y 5 escenas a WebP (q85).
2. Lee el relato de M0008-bosomtwe.md.
3. Actualiza mitologia.json en la raíz y en data/.
"""

import json
import subprocess
import os
from pathlib import Path

RELATOS_DIR = Path("/Users/fryntiz/Library/CloudStorage/GoogleDrive-raupulus@gmail.com/Mi unidad/ia/Relatos")
WEB_DIR = Path("/Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev")
M0008_DIR = RELATOS_DIR / "Historias Mitológicas" / "africa" / "akan" / "abosom" / "M0008-bosomtwe"

# Rutas web
PUB_IMAGES = WEB_DIR / "public" / "assets" / "images"
(PUB_IMAGES / "portadas").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "avatars").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "escenas").mkdir(parents=True, exist_ok=True)

# 1. Convertir y copiar portada 16:9 a WebP (q85)
src_portada = M0008_DIR / "youtube" / "portada-es-ES.jpg"
dst_portada = PUB_IMAGES / "portadas" / "M0008-bosomtwe.webp"
subprocess.run([
    "cwebp", "-q", "85", str(src_portada), "-o", str(dst_portada)
], check=True)
print(f"✅ Portada WebP: {dst_portada}")

# 2. Convertir y copiar avatares a WebP (q85)
src_cabeza = M0008_DIR / "avatars" / "personaje-01-bosomtwe-cabeza.png"
dst_cabeza = PUB_IMAGES / "avatars" / "personaje-01-bosomtwe-cabeza.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cabeza), "-o", str(dst_cabeza)], check=True)

src_cuerpo = M0008_DIR / "avatars" / "personaje-01-bosomtwe-cuerpo.png"
dst_cuerpo = PUB_IMAGES / "avatars" / "personaje-01-bosomtwe-cuerpo.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cuerpo), "-o", str(dst_cuerpo)], check=True)
print(f"✅ Avatares WebP listos.")

# 3. Convertir y copiar 5 escenas clave a WebP (q85)
escenas_map = [
    ("002-selva-montañosa-reino-ashanti-ghana.png", "M0008-002-selva-montañosa-reino-ashanti-ghana.webp", "La selva montañosa del reino ashanti donde reposa la cuenca sagrada del lago Bosumtwi."),
    ("005-nacimiento-nana-bosomtwe-aguas-profundas.png", "M0008-005-nacimiento-nana-bosomtwe-aguas-profundas.webp", "Nana Bosomtwe emergiendo de las aguas profundas del cráter meteórico como espíritu soberano de la caldera."),
    ("018-pescadores-navegan-en-planchas-padua.png", "M0008-018-pescadores-navegan-en-planchas-padua.webp", "Pescadores ashanti navegando sobre planchas tradicionales padua sin tocar el agua con remos de metal."),
    ("026-emergencia-de-bosomtwe-entre-la-espuma.png", "M0008-026-emergencia-de-bosomtwe-entre-la-espuma.webp", "La revelación del dios Bosomtwe ante el cazador Akora Bompe tras la persecución del antílope sagrado."),
    ("031-lavatorio-de-manos-y-despedida-de-bosomtwe.png", "M0008-031-lavatorio-de-manos-y-despedida-de-bosomtwe.webp", "El lavatorio ritual de manos de las almas que se despiden de la tierra terrenal antes de cruzar hacia Asamando.")
]

inline_scenes = []
for src_f, dst_f, pie in escenas_map:
    s_path = M0008_DIR / "escenas" / src_f
    d_path = PUB_IMAGES / "escenas" / dst_f
    subprocess.run(["cwebp", "-q", "85", str(s_path), "-o", str(d_path)], check=True)
    inline_scenes.append({
        "archivo": f"assets/images/escenas/{dst_f}",
        "pie": pie
    })
print(f"✅ 5 escenas clave WebP listas.")

# 4. Extraer texto del relato de M0008-bosomtwe.md
relato_md = M0008_DIR / "M0008-bosomtwe.md"
relato_txt = relato_md.read_text(encoding="utf-8")
parts = relato_txt.split("## Relato")
narrative_text = parts[1].strip() if len(parts) > 1 else ""

# 5. Construir objeto M0008
m0008 = {
    "id": "M0008",
    "slug": "bosomtwe",
    "nombre": "Bosomtwe",
    "epiteto": "El Guardián del Cráter Sagrado",
    "titulo_completo": "Bosomtwe: El Guardián del Cráter Sagrado ⚡ Espíritus Abosom (África)",
    "region": "africa",
    "region_nombre": "África",
    "tradicion": "akan",
    "tradicion_nombre": "Mitología Akan",
    "grupo": "abosom",
    "grupo_nombre": "Espíritus Abosom",
    "estado": "estreno",
    "publicado": False,
    "palabras": 864,
    "duracion_video": "05:28",
    "duracion_audio": "05:28",
    "duracion_short": "00:53",
    "sinopsis": "En el corazón boscoso del imperio ashanti reposa el lago Bosumtwi, un ojo de agua cristalina nacido del impacto de una estrella cósmica hace un millón de años. Venerado por la tradición akan como el umbral supremo donde las almas de los difuntos se despiden de la tierra, el lago está protegido por Bosomtwe, el espíritu abosom del cráter sagrado. Descubre la leyenda del dios antílope, las leyes milenarias que prohíben tocar sus aguas con canoas o remos de hierro, y el pacto ancestral que vincula a pescadores y espíritus con el espejo eterno de Ghana.",
    "youtube_id": "aAmE_7bcmcI",
    "youtube_short_id": "GuI5QjQEUHE",
    "youtube_watch_url": "https://www.youtube.com/watch?v=aAmE_7bcmcI",
    "youtube_short_url": "https://www.youtube.com/shorts/GuI5QjQEUHE",
    "portada": "assets/images/portadas/M0008-bosomtwe.webp",
    "pagina_url": "mitologia/M0008-bosomtwe.html",
    "personajes": [
        {
            "nombre": "Bosomtwe",
            "rol": "Espíritu Abosom del Cráter Sagrado y Custodio del Umbral de las Almas",
            "rasgos": "Divinidad akan de 30 años de porte majestuoso, torso atlético esculpido, piel de bronce y ébano pulido con reflejos húmedos, mirada serena con destellos verde esmeralda, corona sagrada de nenúfares blancos y juncos, líneas ceremoniales de arcilla blanca hyire y faldellín tradicional kente ashanti azul zafiro y verde musgo.",
            "avatar_cabeza": "assets/images/avatars/personaje-01-bosomtwe-cabeza.webp",
            "avatar_cuerpo": "assets/images/avatars/personaje-01-bosomtwe-cuerpo.webp"
        }
    ],
    "escenas_clave": inline_scenes,
    "capitulos": [
        {
            "tiempo": "00:00",
            "segundos": 0,
            "titulo": "I. El Cráter Sagrado y el Espejo de las Almas",
            "resumen": "En el corazón del reino ashanti reposa el lago Bosumtwi, un cráter meteórico de aguas puras donde mora Nana Bosomtwe, el espíritu de las profundidades."
        },
        {
            "tiempo": "01:10",
            "segundos": 70,
            "titulo": "II. El Tabú Sagrado del Metal y las Planchas Padua",
            "resumen": "Las comunidades ribereñas respetan el tabú akyiwadde que prohíbe el hierro en el agua, navegando únicamente sobre planchas de madera padua impulsadas a mano."
        },
        {
            "tiempo": "02:15",
            "segundos": 135,
            "titulo": "III. El Juicio de las Profundidades y la Ira del Abosom",
            "resumen": "Quien transgrede las leyes sagradas desata remolinos violentos; cada cierto tiempo el lago exhala gases sulfurosos (bosome twe apu) bendiciendo con pesca abundante."
        },
        {
            "tiempo": "03:20",
            "segundos": 200,
            "titulo": "IV. El Tránsito de las Almas hacia Asamando",
            "resumen": "La leyenda del cazador Akora Bompe y el antílope herido otwe que condujo al descubrimiento del manantial primordial que se ensanchó en el lago sagrado."
        },
        {
            "tiempo": "04:37",
            "segundos": 277,
            "titulo": "V. La Eterna Alianza del Lago y los Hombres",
            "resumen": "Las almas kra acuden al lago para lavar sus manos y despedirse del dios antes de marchar a Asamando, sellando la comunión eterna entre la tierra y el firmamento."
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

    # Filtrar si ya existía M0008 y anteponer
    data = [item for item in data if item.get("id") != "M0008"]
    data.insert(0, m0008)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Actualizado: {json_file}")

print("🎉 M0008 (Bosomtwe) sincronizado con éxito para la web.")
