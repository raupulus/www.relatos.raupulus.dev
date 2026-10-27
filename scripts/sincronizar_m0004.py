#!/usr/bin/env python3
"""
Sincroniza M0004-anansi en la web relatos.raupulus.dev:
1. Copia y convierte portada, avatares y 5 escenas a WebP (q85).
2. Lee el relato de M0004-anansi.md.
3. Actualiza mitologia.json en la raíz y en data/.
"""

import json
import subprocess
import os
from pathlib import Path

RELATOS_DIR = Path("/Users/fryntiz/Library/CloudStorage/GoogleDrive-raupulus@gmail.com/Mi unidad/ia/Relatos")
WEB_DIR = Path("/Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev")
M0004_DIR = RELATOS_DIR / "Historias Mitológicas" / "africa" / "akan" / "abosom" / "M0004-anansi"

# Rutas web
PUB_IMAGES = WEB_DIR / "public" / "assets" / "images"
(PUB_IMAGES / "portadas").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "avatars").mkdir(parents=True, exist_ok=True)
(PUB_IMAGES / "escenas").mkdir(parents=True, exist_ok=True)

# 1. Convertir y copiar portada 16:9 a WebP (q85)
src_portada = M0004_DIR / "youtube" / "portada-es-ES.jpg"
dst_portada = PUB_IMAGES / "portadas" / "M0004-anansi.webp"
subprocess.run([
    "cwebp", "-q", "85", str(src_portada), "-o", str(dst_portada)
], check=True)
print(f"✅ Portada WebP: {dst_portada}")

# 2. Convertir y copiar avatares a WebP (q85)
src_cabeza = M0004_DIR / "avatars" / "personaje-01-anansi-cabeza.png"
dst_cabeza = PUB_IMAGES / "avatars" / "personaje-01-anansi-cabeza.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cabeza), "-o", str(dst_cabeza)], check=True)

src_cuerpo = M0004_DIR / "avatars" / "personaje-01-anansi-cuerpo.png"
dst_cuerpo = PUB_IMAGES / "avatars" / "personaje-01-anansi-cuerpo.webp"
subprocess.run(["cwebp", "-q", "85", str(src_cuerpo), "-o", str(dst_cuerpo)], check=True)
print(f"✅ Avatares WebP listos.")

# 3. Convertir y copiar 5 escenas clave a WebP (q85)
escenas_map = [
    ("003-kwaku-anansi-arana-cosmica.png", "M0004-003-kwaku-anansi-arana-cosmica.webp", "Kwaku Anansi, la gran araña cósmica y espíritu del ingenio en la tradición Akan."),
    ("009-ascenso-al-cielo-hilo-seda.png", "M0004-009-ascenso-al-cielo-hilo-seda.webp", "Anansi ascendiendo por un hilo de seda plateada hacia la corte celeste del dios Nyame."),
    ("020-nyame-exige-cuatro-tributos.png", "M0004-020-nyame-exige-cuatro-tributos.webp", "El dios supremo Nyame exigiendo la captura de las cuatro bestias imposibles a cambio de los relatos."),
    ("023-trampa-de-la-vara-y-la-piton.png", "M0004-023-trampa-de-la-vara-y-la-piton.webp", "La trampa de la vara de palma y la captura con astucia de la serpiente pitón Onini."),
    ("027-calabaza-rota-sabiduria-esparcida.png", "M0004-027-calabaza-rota-sabiduria-esparcida.webp", "La calabaza quebrándose en las ramas del baobab, esparciendo la sabiduría cósmica entre toda la humanidad.")
]

inline_scenes = []
for src_f, dst_f, pie in escenas_map:
    s_path = M0004_DIR / "escenas" / src_f
    d_path = PUB_IMAGES / "escenas" / dst_f
    subprocess.run(["cwebp", "-q", "85", str(s_path), "-o", str(d_path)], check=True)
    inline_scenes.append({
        "archivo": f"assets/images/escenas/{dst_f}",
        "pie": pie
    })
print(f"✅ 5 escenas clave WebP listas.")

# 4. Extraer texto del relato de M0004-anansi.md
relato_md = M0004_DIR / "M0004-anansi.md"
relato_txt = relato_md.read_text(encoding="utf-8")
parts = relato_txt.split("## Relato")
narrative_text = parts[1].strip() if len(parts) > 1 else ""

# 5. Construir objeto M0004
m0004 = {
    "id": "M0004",
    "slug": "anansi",
    "nombre": "Anansi",
    "epiteto": "El Señor de Todas las Historias",
    "titulo_completo": "Anansi: El Señor de Todas las Historias ⚡ Espíritus Abosom (África)",
    "region": "africa",
    "region_nombre": "África",
    "tradicion": "akan",
    "tradicion_nombre": "Mitología Akan",
    "grupo": "abosom",
    "grupo_nombre": "Espíritus Abosom",
    "estado": "estreno",
    "publicado": False,
    "palabras": 889,
    "duracion_video": "05:20",
    "duracion_audio": "05:20",
    "duracion_short": "00:46",
    "sinopsis": "En las profundidades de las selvas de África occidental, la tradición oral del pueblo akan celebra a Kwaku Anansi: la legendaria araña cósmica y el trickster más célebre de la mitología universal. Mediador entre los espíritus abosom y los mortales, Anansi empleó su infinita astucia para arrebatar las historias al dios supremo del cielo, convirtiéndose en el protector de los desvalidos y en el gran maestro del ingenio frente a la fuerza bruta.",
    "youtube_id": "2E3uBcV42Gg",
    "youtube_short_id": "Od8wjMbhxD0",
    "youtube_watch_url": "https://www.youtube.com/watch?v=2E3uBcV42Gg",
    "youtube_short_url": "https://www.youtube.com/shorts/Od8wjMbhxD0",
    "portada": "assets/images/portadas/M0004-anansi.webp",
    "pagina_url": "mitologia/M0004-anansi.html",
    "personajes": [
        {
            "nombre": "Kwaku Anansi",
            "rol": "Espíritu Tejedor y Trickster de la Sabiduría",
            "rasgos": "Anciano akan enjuto de porte ágil y piel ébano profunda, cabello y barba corta entrecana, mirada vivaz, manto índigo tradicional sobre un hombro con símbolos adinkra y collar de cauris.",
            "avatar_cabeza": "assets/images/avatars/personaje-01-anansi-cabeza.webp",
            "avatar_cuerpo": "assets/images/avatars/personaje-01-anansi-cuerpo.webp"
        }
    ],
    "escenas_clave": inline_scenes,
    "capitulos": [
        {
            "tiempo": "00:00",
            "segundos": 0,
            "titulo": "I. La Gran Araña y el Reino de los Abosom",
            "resumen": "En el corazón de las selvas africanas, el pueblo akan venera a Kwaku Anansi, mediador entre las divinidades abosom y los mortales."
        },
        {
            "tiempo": "01:08",
            "segundos": 68,
            "titulo": "II. El Ascenso al Cielo y el Regalo de los Relatos",
            "resumen": "Anansi asciende por un hilo de seda ante Nyame, obtiene el cofre sagrado de las historias y regala la sabiduría y la memoria oral a los pueblos."
        },
        {
            "tiempo": "02:09",
            "segundos": 129,
            "titulo": "III. El Reverso Sombrío: Vanidad y Engaño",
            "resumen": "La ambición y el egoísmo de la araña trickster conducen a trampas despiadadas y a lecciones morales que alertan contra la gula y la soberbia."
        },
        {
            "tiempo": "03:07",
            "segundos": 187,
            "titulo": "IV. El Precio de Nyame y las Cuatro Bestias",
            "resumen": "Para ganar los relatos, Anansi captura con ingenio sin derramar sangre al leopardo Osebo, las avispas Mmoboro, la pitón Onini y el espíritu Mmoatia."
        },
        {
            "tiempo": "04:31",
            "segundos": 271,
            "titulo": "V. La Calabaza de Sabiduría y el Legado Inmortal",
            "resumen": "La calabaza de sabiduría se quiebra en el baobab esparciéndose por el mundo, y el mito viaja a través del Atlántico como símbolo eterno de resistencia."
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

    # Reemplazar o insertar M0004
    items = [it for it in items if it.get("id") != "M0004"]
    items.append(m0004)
    # Orden descendente por ID
    items = sorted(items, key=lambda x: str(x.get("id", "")), reverse=True)

    with open(p, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"✅ Base de datos actualizada en: {p}")

print("\n🚀 ¡M0004 sincronizado exitosamente con estado estreno y assets WebP!")
