#!/usr/bin/env python3
"""
Raupulus Tales — scripts/build_site.py
Generador estático y sincronizador oficial para la web (relatos.raupulus.dev).

Funciones principales:
1. Sincroniza historias desde el origen canónico (Historias/NNNN-slug/) hacia data/relatos.json.
2. Optimiza y copia portadas (16:9 WebP) y láminas de avatar a assets/images/.
3. Limpia marcas de tiempo y capítulos (eliminando cualquier referencia técnica como video1.mp4).
4. Genera index.html con catálogo reactivo (Alpine.js), filtros temáticos, buscador y visor multimedia.
5. Genera páginas estáticas independientes en relatos/NNNN-slug.html con metadatos SEO y Schema.org.
6. Genera sitemap.xml y robots.txt.
7. Precompila Tailwind CSS (assets/css/tailwind.css) para que el repositorio sea 100% autónomo.
"""

import os
import glob
import re
import json
import shutil
import subprocess
from datetime import datetime
from PIL import Image

SITE_URL = "https://relatos.raupulus.dev"
YT_CHANNEL = "https://www.youtube.com/@raupulus"
YT_SUBSCRIBE = "https://www.youtube.com/@raupulus?sub_confirmation=1"
PUBLIC_EMAIL = "public@raupulus.dev"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORIAS_SRC_DEFAULT = os.environ.get("RELATOS_SRC_DIR", "")

DATA_DIR = os.path.join(BASE_DIR, "data")
RELATOS_DIR = os.path.join(BASE_DIR, "relatos")
PORTADAS_DIR = os.path.join(BASE_DIR, "assets", "images", "portadas")
AVATARS_DIR = os.path.join(BASE_DIR, "assets", "images", "avatars")
DATA_FILE = os.path.join(DATA_DIR, "relatos.json")


def clean_narrative_text(txt):
    """Limpia y da formato HTML ligero a los párrafos del relato."""
    paragraphs = txt.strip().split("\n\n")
    html_out = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p == "* * *":
            html_out.append('<div class="scene-divider my-8 text-center text-damask font-serif tracking-widest text-lg font-bold select-none">* * *</div>')
        elif p.startswith("—") or p.startswith("- "):
            clean_p = p.lstrip("- ")
            html_out.append(f'<p class="mb-5 leading-relaxed text-text-main text-base sm:text-lg pl-3 border-l border-damask/40 font-serif">{clean_p}</p>')
        elif p.startswith("«") and p.endswith("»"):
            html_out.append(f'<blockquote class="my-6 pl-4 border-l-2 border-crimson italic text-text-muted text-base sm:text-lg font-serif">{p}</blockquote>')
        else:
            html_out.append(f'<p class="mb-5 leading-relaxed text-text-main text-base sm:text-lg font-serif">{p}</p>')
    return "\n".join(html_out)


def clean_chapter_title(title):
    """Elimina menciones técnicas a archivos o clips de apertura."""
    t = re.sub(r'\s*\((?:Clip|Clips) de apertura\)', '', title, flags=re.I)
    t = re.sub(r'\s*\(video\d+\.mp4\)', '', t, flags=re.I)
    t = re.sub(r'\s*\(Planos[^\)]*\)', '', t, flags=re.I)
    return t.strip()


def get_category_info(genres):
    """Asigna la categoría principal y nombre legible."""
    g_str = ' '.join(genres).lower()
    if 'terror' in g_str or 'monstruo' in g_str:
        return 'terror', 'Terror'
    if 'ciencia ficción' in g_str or 'scifi' in g_str:
        return 'scifi', 'Ciencia Ficción'
    if 'histórico' in g_str or 'historico' in g_str:
        return 'historico', 'Histórico'
    if 'comedia' in g_str or 'drama' in g_str:
        if 'misterio' in g_str:
            return 'misterio', 'Misterio'
        return 'drama', 'Drama'
    if 'misterio' in g_str:
        return 'misterio', 'Misterio'
    return 'suspense', 'Suspense'


CHAPTER_SUMMARIES = {
    "0001": {
        0: "Apertura en la noche de Cuenca; la llegada al portal bajo la niebla y el silencio gélido de la judería.",
        20: "La primera noche de guardia de Yolanda, el despertar de Amparo y la misteriosa figura frente a la puerta.",
        176: "La visita de Julián, las estrictas instrucciones sobre la medicación y la obsesión por el cojín bordado.",
        379: "El hombre que vigila en el banco de la plaza, la carta interceptada y el hallazgo del fármaco oculto.",
        574: "El descubrimiento en el cuarto de costura: la partida de defunción de 1958 y el recuerdo lúcido de Amparo.",
        786: "La verdad al descubierto: el engaño deliberado y la manipulación sistemática de la memoria materna.",
        1010: "El momento de la verdad en la madrugada: los golpes en el portal y el reencuentro en la nieve.",
        1236: "La confrontación decisiva: la llegada furiosa de Julián y la lealtad protectora entre madre e hijo."
    },
    "0002": {
        0: "Turno nocturno en la sede corporativa de Perdura y la supervisión técnica de conciencias digitales.",
        20: "La llamada semanal de Olga Prieto y el descubrimiento de una anomalía en las respuestas del difunto Fernando.",
        235: "La llegada de un ticket urgente para eliminar recuerdos clave y el dilema ético ante el encubrimiento.",
        361: "La auditoría profunda de las finanzas y el hallazgo de cláusulas testamentarias alteradas.",
        495: "El descubrimiento de las manipulaciones en los registros policiales y las denuncias silenciadas.",
        611: "El cara a cara digital con la réplica sintética, la coacción de la gerencia y la ejecución del borrado definitivo."
    },
    "0003": {
        0: "La rutina matinal en la vieja estación de Valladolid y el eco de los trenes en la niebla castellana.",
        10: "La llegada del anciano Anselmo con un boleto amarillento de 1967 custodiado durante décadas.",
        138: "Las prisas del nuevo jefe por vaciar el archivo subterráneo y la negativa de Lucía a destruir el pasado.",
        268: "El descenso a los sótanos húmedos y el rastreo de la pista de la maleta de cartón olvidada.",
        394: "El recuerdo de una huida inconclusa y las razones que separaron a dos personas en el andén 3.",
        554: "La apertura del equipaje y el rescate de las cartas y recuerdos que cambiaron una vida entera.",
        702: "La entrega oficial en ventanilla y la reconciliación con el tiempo bajo el gran reloj de la estación."
    },
    "0004": {
        0: "Dos hermanos distanciados durante quince años cruzan el país con la urna en el asiento y el calor asfixiante.",
        147: "Un control de tráfico en la carretera y las verdaderas intenciones sobre el destino final de las cenizas.",
        337: "La parada nocturna en un hostal de León, el reproche acumulado y la carta con la inicial prohibida.",
        489: "La lectura de las últimas voluntades y la revelación sobre los silencios que rompieron a la familia.",
        622: "La llegada al puerto asturiano de Luarca y la sorpresa que aguardaba frente a las lanchas pesqueras.",
        757: "El adiós frente al oleaje del Cantábrico y la reconciliación sellada en el camino de regreso."
    },
    "0005": {
        0: "Madrid de posguerra; en la penumbra de un taller clandestino en la calle del Pez se recibe un encargo límite.",
        138: "Las herramientas de precisión, el olor a ácido y el pacto de salvamento con la red clandestina.",
        276: "La entrega furtiva entre las lápidas de la Almudena y las sospechas sobre la identidad del fugitivo.",
        414: "El detalle imperceptible en el sello oficial que solo un maestro artesano falsificador puede advertir.",
        552: "La confrontación en la trastienda: el choque entre el deber moral, la sangre y el precio de la libertad.",
        690: "La quema de las matrices comprometedoras en la estufa y el nacimiento de una nueva identidad."
    },
    "0006": {
        0: "La noche gélida de carnaval en Chipiona y la atmósfera inquietante tras el bullicio de las comparsas.",
        20: "Rubén descansa en la soledad de la plazoleta y sufre un desmayo repentino tras un roce siniestro.",
        278: "El despertar al alba frente al espejo del baño y el hallazgo de ocho grapas quirúrgicas en la espalda.",
        379: "La revisión de las grabaciones de seguridad del muelle y la filmación de figuras disfrazadas en la bajamar.",
        478: "La búsqueda de pistas en las naves abandonadas y el olor a salmuera y formol en las conserveras.",
        590: "El descenso a los canales subterráneos de desagüe y el horror oculto bajo el casco urbano.",
        740: "La emboscada final entre compuertas industriales y el tambor lejano de los carnavales en la noche."
    },
    "0007": {
        0: "Una joven se instala en un piso barato del centro de Madrid y recibe un sobre que anticipa sus pasos.",
        145: "Los detalles descritos en las cartas comienzan a cumplirse con perturbadora y milimétrica exactitud.",
        281: "Las confesiones de la vecina sobre la anterior habitante del piso y una tragedia nunca esclarecida.",
        428: "El rastreo en la hemeroteca municipal de 1989 y la fotografía del carné idéntica al presente.",
        564: "La vigilia a oscuras en el pasillo a medianoche y el intento de comunicarse a través del portal temporal.",
        734: "La conclusión del ciclo cronológico y la carta que aguarda bajo la puerta a la siguiente moradora."
    },
    "0008": {
        0: "El pesquero El Rocío de la Mar llega a puerto destrozado por fuerzas desconocidas en alta mar.",
        145: "Daniel investiga las dentelladas en el casco y observa anomalías inquietantes en las corrientes costeras.",
        290: "Los viejos marineros de la taberna recuerdan la leyenda sobre la criatura que duerme en la fosa.",
        435: "La marea baja revela una masa colosal aproximándose hacia los corrales de piedra frente al faro.",
        580: "La defensa desesperada desde el rompeolas con focos halógenos y bengalas sobre el leviatán marino.",
        725: "El alba silenciosa en la orilla, la retirada del monstruo y la advertencia de que el océano nunca olvida."
    },
    "0009": {
        0: "El aviso en las frecuencias de radio y la movilización inmediata de los preparacionistas en la sierra.",
        150: "Los ingenieros de la red eléctrica en La Moraleja luchan por frenar el desequilibrio de la frecuencia nacional.",
        295: "La histeria colectiva empuja a los grupos armados a sabotear las infraestructuras que creían vulnerables.",
        440: "El puenteo forzado de la subestación provoca exactamente el desplome general que todos temían.",
        585: "El colapso en cascada de las centrales y la fractura eléctrica con la red del resto de Europa.",
        730: "El silencio absoluto sobre la sierra nevada y la grabación en cinta magnética que atestigua la profecía cumplida."
    },
    "0010": {
        0: "En una comarca rural aislada, los rumores sobre un contagio empujan a los vecinos a medidas extremas.",
        120: "La doctora Carvajal en el hospital comarcal intenta calmar el pánico colectivo frente a un brote estacional.",
        250: "La desconfianza hacia las instituciones sanitarias desemboca en el asalto nocturno al banco de medicinas.",
        375: "Los búnkeres clandestinos reparten fórmulas caseras que desatan una intoxicación real y devastadora.",
        500: "La alerta sanitaria desbordada y la constatación de que el miedo fue más letal que el propio virus.",
        625: "El colapso de los refugios, el vademécum de la verdad y la lección grabada para el futuro."
    }
}


def sync_assets_and_data(src_dir=HISTORIAS_SRC_DEFAULT):
    """Extrae datos de historias, convierte portadas/avatares a WebP y genera data/relatos.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PORTADAS_DIR, exist_ok=True)
    os.makedirs(AVATARS_DIR, exist_ok=True)

    if not os.path.exists(src_dir):
        print(f"Directorio fuente {src_dir} no accesible, usando data/relatos.json existente...")
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    story_dirs = sorted([d for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d)) and re.match(r'^\d{4}-', d)])
    relatos = []

    for sdir in story_dirs:
        sp = os.path.join(src_dir, sdir)
        num_id = sdir[:4]
        slug = sdir[5:]

        # Archivo maestro
        mdfiles = glob.glob(os.path.join(sp, f"{num_id}*.md"))
        if not mdfiles:
            continue
        with open(mdfiles[0], 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Frontmatter y cuerpo
        fm = {}
        body = raw_content
        if raw_content.startswith('---'):
            parts = raw_content.split('---', 2)
            if len(parts) >= 3:
                for line in parts[1].splitlines():
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fm[k.strip()] = v.strip().strip('"').strip("'")
                body = parts[2]

        # Título
        t_m = re.search(r'^#\s+(.+)$', body, re.M)
        titulo = t_m.group(1).strip() if t_m else fm.get('titulo', slug.replace('-', ' ').title())

        # Descripción
        desc_m = re.search(r'## Descripción\s*\n+([\s\S]*?)(?=\n## |\n---|\Z)', body)
        sinopsis = desc_m.group(1).strip() if desc_m else fm.get('sinopsis', '')
        sinopsis = re.sub(r'\s+', ' ', sinopsis)

        # Géneros y categoría principal
        m_gen = re.search(r'g[eé]nero:\s*\[?([^\]\n]+)\]?', raw_content, re.I)
        raw_genres = [g.strip().strip('"').strip("'") for g in m_gen.group(1).split(',')] if m_gen else ['Suspense']
        categoria, categoria_nombre = get_category_info(raw_genres)
        generos = [g.title() for g in raw_genres]

        # Personajes
        characters = []
        chars_m = re.search(r'## Personajes\s*\n+([\s\S]*?)(?=\n---|\n## Relato|\Z)', body)
        if chars_m:
            char_blocks = re.findall(r'###\s+([^\n]+)\s*\n+([\s\S]*?)(?=\n###|\Z)', chars_m.group(1))
            for cidx, (cname, cinfo) in enumerate(char_blocks, start=1):
                cname = cname.strip()
                rol, rasgos, motivacion, conflicto = '', '', '', ''
                for line in cinfo.splitlines():
                    if '**Rol:**' in line: rol = line.split('**Rol:**', 1)[1].strip()
                    elif '**Rasgos:**' in line: rasgos = line.split('**Rasgos:**', 1)[1].strip()
                    elif '**Motivación:**' in line: motivacion = line.split('**Motivación:**', 1)[1].strip()
                    elif '**Conflicto:**' in line: conflicto = line.split('**Conflicto:**', 1)[1].strip()

                # Buscar avatar local si existe
                c_slug = cname.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n')
                c_words = [w for w in re.findall(r'\b[a-z]{3,}\b', c_slug) if w not in ('don','dona','senor','senora')]
                avatar_cabeza = None
                avatar_cuerpo = None

                # Comprobar en avatars_out
                for av_file in os.listdir(AVATARS_DIR) if os.path.exists(AVATARS_DIR) else []:
                    if av_file.startswith(num_id):
                        if any(w in av_file for w in c_words):
                            if 'cabeza' in av_file:
                                avatar_cabeza = f"assets/images/avatars/{av_file}"
                            elif 'cuerpo' in av_file:
                                avatar_cuerpo = f"assets/images/avatars/{av_file}"

                characters.append({
                    "id": f"{num_id}-p{cidx}",
                    "nombre": cname,
                    "rol": rol,
                    "rasgos": rasgos,
                    "motivacion": motivacion,
                    "conflicto": conflicto,
                    "avatar_cabeza": avatar_cabeza,
                    "avatar_cuerpo": avatar_cuerpo
                })

        # Relato
        relato_m = re.search(r'## Relato\s*\n+([\s\S]*)$', body)
        relato_raw = relato_m.group(1).strip() if relato_m else ''
        palabras = len(re.findall(r'\b\w+\b', relato_raw))
        lectura_min = max(1, round(palabras / 220))

        # YouTube ID
        yt_id = None
        yt_file = os.path.join(sp, 'youtube', 'youtube.md')
        if os.path.exists(yt_file):
            with open(yt_file, 'r', encoding='utf-8') as yf:
                yc = yf.read()
                m_yt = re.search(r'Vídeo ID:[^\n`]*`?([a-zA-Z0-9_-]{11})`?', yc)
                if m_yt: yt_id = m_yt.group(1)
                else:
                    m_yt2 = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', yc)
                    if m_yt2: yt_id = m_yt2.group(1)

        # Portada WebP
        portada_webp = f"assets/images/portadas/{sdir}.webp"
        portada_src = os.path.join(sp, 'youtube', 'portada.jpg')
        if not os.path.exists(portada_src):
            portada_src = os.path.join(sp, 'youtube', 'portada-es-ES.jpg')
        if os.path.exists(portada_src):
            dest_portada = os.path.join(BASE_DIR, portada_webp)
            if not os.path.exists(dest_portada) or os.path.getmtime(portada_src) > os.path.getmtime(dest_portada):
                with Image.open(portada_src) as im:
                    im.save(dest_portada, 'WEBP', quality=85)

        # Avatares WebP
        avatars_src_dir = os.path.join(sp, 'avatars')
        if os.path.exists(avatars_src_dir):
            for af in glob.glob(os.path.join(avatars_src_dir, '*.png')):
                bname = os.path.splitext(os.path.basename(af))[0]
                dest_av = os.path.join(AVATARS_DIR, f"{num_id}-{bname}.webp")
                if not os.path.exists(dest_av) or os.path.getmtime(af) > os.path.getmtime(dest_av):
                    with Image.open(af) as im:
                        im.save(dest_av, 'WEBP', quality=85)

        # Capítulos y Storyboard
        mt_json = os.path.join(sp, 'storyboard', 'marcas_tiempo.json')
        chapters = []
        duracion_audio = "14:00"
        duracion_segundos = 840
        if os.path.exists(mt_json):
            with open(mt_json, 'r', encoding='utf-8') as jf:
                jdata = json.load(jf)
                duracion_audio = jdata.get('duracion_total_formato', '14:00')
                duracion_segundos = jdata.get('duracion_total_segundos', 840)
                sum_map = CHAPTER_SUMMARIES.get(num_id, {})
                for cap in jdata.get('capitulos_youtube', []):
                    c_sec = cap.get('segundos', 0)
                    c_time = cap.get('tiempo', '00:00')
                    c_title = clean_chapter_title(cap.get('titulo', ''))
                    # Resumen narrativo sin archivos técnicos
                    c_summary = sum_map.get(c_sec, f"Desarrollo dramático de la escena correspondiente a los acontecimientos de {c_time}.")
                    chapters.append({
                        "tiempo": c_time,
                        "segundos": c_sec,
                        "titulo": c_title,
                        "resumen": c_summary
                    })

        relato_entry = {
            "id": num_id,
            "slug": slug,
            "url_hash": f"#{num_id}-{slug}",
            "pagina_url": f"relatos/{num_id}-{slug}.html",
            "titulo": titulo,
            "sinopsis": sinopsis,
            "categoria": categoria,
            "categoria_nombre": categoria_nombre,
            "generos": generos,
            "palabras": palabras,
            "lectura_min": lectura_min,
            "duracion_audio": duracion_audio,
            "duracion_segundos": duracion_segundos,
            "youtube_id": yt_id,
            "youtube_url": f"https://www.youtube.com/watch?v={yt_id}" if yt_id else None,
            "portada": portada_webp,
            "personajes": characters,
            "capitulos": chapters,
            "relato_raw": relato_raw,
            "relato_html": clean_narrative_text(relato_raw),
            "locucion": {
                "es_ES": {"voz": "Álvaro (es-ES-AlvaroNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Voz máster y vídeo"},
                "es_LAT": {"voz": "Alonso (es-US-AlonsoNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Voz neutra latinoamericana"},
                "en_US": {"voz": "Christopher (en-US-ChristopherNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Narración internacional en inglés"}
            }
        }
        relatos.append(relato_entry)

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(relatos, f, ensure_ascii=False, indent=2)

    print(f"✅ Sincronizados {len(relatos)} relatos en {DATA_FILE}")
    return relatos


def generate_index_html(relatos):
    """Genera la página principal index.html completamente reactiva con Alpine.js."""
    target_file = os.path.join(BASE_DIR, "index.html")

    # Serializar relatos para Alpine.js de forma segura
    relatos_json_escaped = json.dumps(relatos, ensure_ascii=False).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', '&quot;')

    html = f"""<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Raupulus Tales — Historias y Ficción Multimedia</title>
  <meta name="description" content="Portal oficial de Raupulus Tales. Historias literarias completas, audiolibros multilingües, storyboards cinematográficos y vídeos 1080p.">
  <meta name="keywords" content="Raupulus, Relatos, Cuentos, Audiolibros, Ficción Sonora, Historias de Terror, Suspense, Ciencia Ficción, Storyboard">
  <meta name="author" content="Raupulus">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#941300">
  <link rel="canonical" href="{SITE_URL}/">

  <!-- Open Graph / Redes Sociales -->
  <meta property="og:site_name" content="Raupulus Tales">
  <meta property="og:locale" content="es_ES">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{SITE_URL}/">
  <meta property="og:title" content="Raupulus Tales — Historias y Ficción Multimedia">
  <meta property="og:description" content="Relatos literarios con audiolibros multilingües y producciones cinematográficas en vídeo 1080p.">
  <meta property="og:image" content="{SITE_URL}/assets/images/logo.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@raupulus">
  <meta name="twitter:creator" content="@raupulus">

  <!-- Iconos locales -->
  <link rel="icon" type="image/webp" href="assets/images/logo.webp">
  <link rel="apple-touch-icon" href="assets/images/logo.png">

  <!-- CSS local pretranspilado (Sin CDNs externos) -->
  <link rel="stylesheet" href="assets/css/tailwind.css">

  <!-- Alpine.js local -->
  <script defer src="assets/js/alpine.min.js"></script>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "Raupulus Tales",
    "url": "{SITE_URL}/",
    "description": "Portal oficial de ficción multimedia y relatos cinematográficos de Raupulus",
    "inLanguage": ["es-ES", "es-419", "en-US"],
    "publisher": {{
      "@type": "Organization",
      "name": "Raupulus",
      "logo": "{SITE_URL}/assets/images/logo.png"
    }}
  }}
  </script>
</head>
<body class="bg-obsidian text-text-main min-h-screen flex flex-col selection:bg-crimson selection:text-white"
      x-data="talesApp()"
      x-init="initApp()">

  <!-- Fondo ambiental cinemático -->
  <div class="fixed inset-0 pointer-events-none -z-10 overflow-hidden" aria-hidden="true">
    <div class="absolute -top-40 left-1/2 -translate-x-1/2 w-[850px] h-[550px] bg-gradient-to-b from-crimson/15 via-plum/10 to-transparent blur-3xl opacity-75"></div>
    <div class="absolute top-1/3 -right-48 w-[650px] h-[650px] bg-damask/10 blur-3xl rounded-full"></div>
    <div class="absolute bottom-10 -left-48 w-[550px] h-[550px] bg-plum/15 blur-3xl rounded-full"></div>
  </div>

  <!-- Header / Navbar Oficial -->
  <header class="sticky top-0 z-50 backdrop-blur-md bg-obsidian/90 border-b border-border-subtle transition-all">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      
      <!-- Brand & Logotipo -->
      <a href="#" class="flex items-center gap-3 group focus:outline-none focus-visible:ring-2 focus-visible:ring-crimson rounded-lg p-1" aria-label="Raupulus Tales - Inicio">
        <div class="relative w-10 h-10 rounded-full overflow-hidden border border-damask/50 group-hover:border-crimson transition-colors duration-300">
          <img src="assets/images/logo.webp" alt="Raupulus Logo" width="40" height="40" class="w-full h-full object-cover">
        </div>
        <div class="flex flex-col">
          <span class="font-bold text-lg text-text-bright tracking-wider group-hover:text-damask-light transition-colors">RAUPULUS</span>
          <span class="text-[10px] tracking-widest text-text-muted uppercase -mt-1 font-semibold">TALES • RELATOS</span>
        </div>
      </a>

      <!-- Navegación central -->
      <nav class="hidden md:flex items-center gap-6 text-sm font-medium">
        <a href="#catalogo" class="text-text-main hover:text-text-bright hover:underline underline-offset-4 decoration-crimson transition">Catálogo</a>
        <a href="#visor-relato" class="text-text-main hover:text-text-bright hover:underline underline-offset-4 decoration-crimson transition">Visor de Relato</a>
        <a href="#universo" class="text-text-main hover:text-text-bright hover:underline underline-offset-4 decoration-crimson transition">El Universo</a>
        
        <!-- Selector simulado de idioma de locución -->
        <div class="flex items-center gap-1 bg-obsidian-card border border-border-subtle rounded-md p-1 text-xs">
          <button @click="idiomaActivo = 'es-ES'" :class="idiomaActivo === 'es-ES' ? 'bg-crimson text-white font-bold' : 'text-text-muted hover:text-text-main'" class="px-2 py-0.5 rounded transition" title="Español de España">ES</button>
          <button @click="idiomaActivo = 'es-LAT'" :class="idiomaActivo === 'es-LAT' ? 'bg-crimson text-white font-bold' : 'text-text-muted hover:text-text-main'" class="px-2 py-0.5 rounded transition" title="Español Latinoamericano">LAT</button>
          <button @click="idiomaActivo = 'en-US'" :class="idiomaActivo === 'en-US' ? 'bg-crimson text-white font-bold' : 'text-text-muted hover:text-text-main'" class="px-2 py-0.5 rounded transition" title="Inglés Internacional">EN</button>
        </div>

        <!-- Botón Canal YouTube -->
        <a href="{YT_CHANNEL}" target="_blank" rel="noopener noreferrer" 
           class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-yt-red/90 hover:bg-yt-red text-white text-xs font-semibold tracking-wide transition shadow-sm hover:shadow-crimson/50">
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
          YouTube
        </a>
      </nav>

      <!-- Menú Hamburguesa Móvil -->
      <button @click="menuAbierto = !menuAbierto" class="md:hidden p-2 rounded-lg text-text-muted hover:text-text-bright hover:bg-obsidian-card" aria-label="Abrir menú">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
      </button>
    </div>

    <!-- Menú desplegable móvil -->
    <div x-show="menuAbierto" @click.away="menuAbierto = false" x-cloak class="md:hidden border-b border-border-subtle bg-obsidian-card px-4 py-4 space-y-3">
      <a href="#catalogo" @click="menuAbierto = false" class="block text-sm text-text-main hover:text-text-bright">Catálogo de Relatos</a>
      <a href="#visor-relato" @click="menuAbierto = false" class="block text-sm text-text-main hover:text-text-bright">Visor Multimedia</a>
      <a href="#universo" @click="menuAbierto = false" class="block text-sm text-text-main hover:text-text-bright">El Universo</a>
      <div class="pt-2 border-t border-border-subtle flex items-center justify-between">
        <span class="text-xs text-text-muted">Locución de estudio:</span>
        <div class="flex gap-1">
          <button @click="idiomaActivo = 'es-ES'" :class="idiomaActivo === 'es-ES' ? 'bg-crimson text-white' : 'text-text-muted'" class="px-2 py-1 text-xs rounded">ES</button>
          <button @click="idiomaActivo = 'es-LAT'" :class="idiomaActivo === 'es-LAT' ? 'bg-crimson text-white' : 'text-text-muted'" class="px-2 py-1 text-xs rounded">LAT</button>
          <button @click="idiomaActivo = 'en-US'" :class="idiomaActivo === 'en-US' ? 'bg-crimson text-white' : 'text-text-muted'" class="px-2 py-1 text-xs rounded">EN</button>
        </div>
      </div>
    </div>
  </header>

  <!-- Contenido Principal -->
  <main class="flex-1" id="main-content">

    <!-- Hero Section -->
    <section class="relative py-16 md:py-20 border-b border-border-subtle overflow-hidden">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
        
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-plum/40 border border-damask/40 text-xs font-semibold text-text-bright mb-6">
          <span class="w-2 h-2 rounded-full bg-crimson animate-pulse"></span>
          Ficción Multimedia • Audiolibros Calibrados • Escenas Full HD 1080p
        </div>

        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-text-bright tracking-tight max-w-4xl mx-auto">
          Historias que se leen, se escuchan y <span class="text-transparent bg-clip-text bg-gradient-to-r from-crimson via-damask to-damask-light">cobran vida</span>
        </h1>
        
        <p class="mt-6 text-base sm:text-lg text-text-muted max-w-2xl mx-auto leading-relaxed">
          Universo narrativo cinematográfico de Raupulus: relatos literarios profundos, biblias visuales de personajes y producciones en vídeo con locución multilingüe.
        </p>

        <!-- Accesos rápidos del Hero -->
        <div class="mt-8 flex flex-wrap items-center justify-center gap-4">
          <button @click="irAUltimoEstreno()" class="px-6 py-3 rounded-lg bg-crimson hover:bg-crimson-glow text-white font-semibold text-sm transition-all duration-200 glow-crimson flex items-center gap-2">
            <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            <span>Ver Último Estreno (<span x-text="relatos[0]?.titulo"></span>)</span>
          </button>
          <a href="#catalogo" class="px-6 py-3 rounded-lg bg-obsidian-card hover:bg-obsidian-elevated border border-border-subtle hover:border-damask text-text-main font-semibold text-sm transition-all duration-200">
            Explorar Catálogo Completo (<span x-text="relatos.length"></span>)
          </a>
        </div>
      </div>
    </section>

    <!-- Visor de Historia y Reproductor Multimedia -->
    <section id="visor-relato" class="py-14 md:py-16 bg-obsidian-card/70 border-b border-border-subtle scroll-mt-14">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <!-- Cabecera del Visor con Metadatos del Relato Activo -->
        <div class="flex flex-col sm:flex-row sm:items-end justify-between mb-6 gap-3">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider bg-crimson text-white" x-text="relatoActivo.id"></span>
              <span class="px-2.5 py-0.5 rounded text-xs font-semibold bg-plum/60 border border-damask/40 text-text-bright" x-text="relatoActivo.categoria_nombre"></span>
              <span class="text-xs text-text-muted">• <span x-text="relatoActivo.palabras"></span> palabras • ≈ <span x-text="relatoActivo.lectura_min"></span> min lectura</span>
            </div>
            <h2 class="text-2xl sm:text-3xl font-extrabold text-text-bright" x-text="relatoActivo.titulo"></h2>
          </div>

          <!-- Selector rápido de siguiente / anterior relato -->
          <div class="flex items-center gap-2 text-xs font-medium">
            <button @click="anteriorRelato()" class="px-3 py-1.5 rounded-lg bg-obsidian border border-border-subtle hover:border-damask text-text-muted hover:text-white transition flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
              Anterior
            </button>
            <button @click="siguienteRelato()" class="px-3 py-1.5 rounded-lg bg-obsidian border border-border-subtle hover:border-damask text-text-muted hover:text-white transition flex items-center gap-1">
              Siguiente
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
            </button>
          </div>
        </div>

        <!-- Marco del Visor / Reproductor -->
        <div class="rounded-2xl bg-obsidian border border-border-subtle overflow-hidden shadow-2xl">
          
          <!-- Contenedor de Vídeo 16:9 con Facade de Privacidad y Rendimiento -->
          <div class="relative aspect-video bg-black overflow-hidden border-b border-border-subtle flex items-center justify-center">
            
            <!-- Si tiene YouTube ID y el usuario aún no pulsó Play -->
            <template x-if="relatoActivo.youtube_id && !videoReproduciendo">
              <div class="relative w-full h-full cursor-pointer group" @click="reproducirVideo()">
                <img :src="relatoActivo.portada" :alt="'Portada del relato ' + relatoActivo.titulo" class="w-full h-full object-cover group-hover:scale-102 transition-transform duration-500">
                <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent flex flex-col items-center justify-center text-center p-4">
                  <!-- Botón Play de YouTube Oficial -->
                  <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-crimson/95 group-hover:bg-yt-red group-hover:scale-110 text-white flex items-center justify-center shadow-xl glow-crimson transition-all duration-300">
                    <svg class="w-8 h-8 sm:w-10 sm:h-10 translate-x-0.5 fill-current" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                  </div>
                  <div class="mt-4 font-bold text-sm sm:text-base text-white tracking-wide drop-shadow">Ver Producción Cinematográfica en YouTube (1080p)</div>
                  <div class="text-xs text-text-main/80 mt-1">Duración: <span x-text="relatoActivo.duracion_audio"></span> min • Locución oficial multilingüe</div>
                </div>
              </div>
            </template>

            <!-- Si el usuario pulsó Play: Iframe embebido con youtube-nocookie -->
            <template x-if="relatoActivo.youtube_id && videoReproduciendo">
              <iframe :src="'https://www.youtube-nocookie.com/embed/' + relatoActivo.youtube_id + '?autoplay=1&playsinline=1&rel=0&modestbranding=1'"
                      :title="'Vídeo oficial del relato ' + relatoActivo.titulo"
                      class="w-full h-full border-0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                      allowfullscreen></iframe>
            </template>

            <!-- Si aún no tiene YouTube ID (en producción) -->
            <template x-if="!relatoActivo.youtube_id">
              <div class="relative w-full h-full">
                <img :src="relatoActivo.portada" :alt="'Portada del relato ' + relatoActivo.titulo" class="w-full h-full object-cover opacity-60">
                <div class="absolute inset-0 bg-obsidian/75 backdrop-blur-sm flex flex-col items-center justify-center text-center p-6">
                  <div class="w-12 h-12 rounded-full bg-damask/40 text-text-bright flex items-center justify-center mb-3">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  </div>
                  <div class="text-base sm:text-lg font-bold text-white">Próximo Estreno Cinematográfico</div>
                  <p class="text-xs sm:text-sm text-text-muted mt-1 max-w-md">El vídeo Full HD 1080p y las locuciones de estudio están en fase final de producción y sincronización.</p>
                  <a href="{YT_CHANNEL}" target="_blank" rel="noopener noreferrer" class="mt-4 px-4 py-2 rounded-lg bg-yt-red text-white text-xs font-semibold hover:bg-red-700 transition flex items-center gap-2">
                    Suscribirse al Canal para el Estreno
                  </a>
                </div>
              </div>
            </template>

          </div>

          <!-- Barra de Acciones y Enlaces de YouTube -->
          <div class="px-5 py-3 bg-obsidian-elevated/90 border-b border-border-subtle flex flex-wrap items-center justify-between gap-3 text-xs">
            <div class="flex items-center gap-2 text-text-muted">
              <span>🎧 Locución activa:</span>
              <span class="font-semibold text-text-bright" x-text="idiomaActivo === 'es-ES' ? 'Álvaro (España)' : (idiomaActivo === 'es-LAT' ? 'Alonso (Latinoamérica)' : 'Christopher (Inglés)')"></span>
            </div>
            <div class="flex items-center gap-3">
              <template x-if="relatoActivo.youtube_url">
                <a :href="relatoActivo.youtube_url" target="_blank" rel="noopener noreferrer" class="text-yt-red hover:text-red-400 font-semibold flex items-center gap-1 transition">
                  <svg class="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
                  Abrir en YouTube
                </a>
              </template>
              <a :href="relatoActivo.pagina_url" class="text-damask-light hover:text-white font-semibold transition">
                Página Independiente ↗
              </a>
            </div>
          </div>

          <!-- Selector de Pestañas Interactivas (Alpine.js) -->
          <div class="flex border-b border-border-subtle bg-obsidian-elevated px-4 text-xs font-semibold overflow-x-auto">
            <button @click="vistaPestana = 'relato'" :class="vistaPestana === 'relato' ? 'text-white border-crimson bg-obsidian shadow-sm' : 'text-text-muted hover:text-text-main border-transparent'" class="px-5 py-3 border-b-2 transition whitespace-nowrap flex items-center gap-2">
              📖 Relato Literario
            </button>
            <button @click="vistaPestana = 'capitulos'" :class="vistaPestana === 'capitulos' ? 'text-white border-crimson bg-obsidian shadow-sm' : 'text-text-muted hover:text-text-main border-transparent'" class="px-5 py-3 border-b-2 transition whitespace-nowrap flex items-center gap-2">
              🎬 Capítulos & Storyboard
            </button>
            <button @click="vistaPestana = 'personajes'" :class="vistaPestana === 'personajes' ? 'text-white border-crimson bg-obsidian shadow-sm' : 'text-text-muted hover:text-text-main border-transparent'" class="px-5 py-3 border-b-2 transition whitespace-nowrap flex items-center gap-2">
              👤 Personajes & Biblia Visual (<span x-text="relatoActivo.personajes.length"></span>)
            </button>
            <button @click="vistaPestana = 'locucion'" :class="vistaPestana === 'locucion' ? 'text-white border-crimson bg-obsidian shadow-sm' : 'text-text-muted hover:text-text-main border-transparent'" class="px-5 py-3 border-b-2 transition whitespace-nowrap flex items-center gap-2">
              🎙️ Locución & Audios
            </button>
          </div>

          <!-- Paneles de Contenido -->
          <div class="p-6 md:p-10">

            <!-- Panel 1: Relato Literario Completo -->
            <div x-show="vistaPestana === 'relato'" x-cloak class="max-w-prose mx-auto">
              <!-- Sinopsis de entrada -->
              <div class="p-4 rounded-xl bg-obsidian-card border border-border-subtle mb-8 text-xs sm:text-sm text-text-muted italic leading-relaxed">
                <span class="font-bold text-damask-light not-italic block mb-1">Sinopsis:</span>
                <span x-text="relatoActivo.sinopsis"></span>
              </div>

              <!-- Texto del relato formateado -->
              <div class="prose prose-invert max-w-none text-text-main" x-html="relatoActivo.relato_html"></div>

              <div class="mt-10 pt-6 border-t border-border-subtle text-center text-xs text-text-muted">
                Fin del relato • <a href="#catalogo" class="text-damask-light hover:underline font-semibold">Volver al catálogo para elegir otra historia</a>
              </div>
            </div>

            <!-- Panel 2: Capítulos & Storyboard (100% libre de archivos técnicos o referencias video1) -->
            <div x-show="vistaPestana === 'capitulos'" x-cloak class="space-y-4">
              <div class="flex items-center justify-between border-b border-border-subtle pb-3">
                <div>
                  <h3 class="font-bold text-sm text-text-bright">Estructura Narrativa por Capítulos</h3>
                  <p class="text-xs text-text-muted">Marcas de tiempo calibradas para navegación y sincronización en YouTube</p>
                </div>
                <span class="text-xs font-mono text-damask-light font-bold" x-text="relatoActivo.duracion_audio"></span>
              </div>

              <div class="space-y-3">
                <template x-for="(cap, idx) in relatoActivo.capitulos" :key="idx">
                  <div class="p-4 rounded-xl bg-obsidian-elevated border border-border-subtle hover:border-damask/60 transition flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div class="flex items-start gap-3">
                      <span class="font-mono text-xs font-bold text-crimson px-2.5 py-1 rounded bg-obsidian border border-border-subtle whitespace-nowrap" x-text="cap.tiempo"></span>
                      <div>
                        <h4 class="text-sm font-bold text-text-bright" x-text="cap.titulo"></h4>
                        <p class="text-xs text-text-muted mt-1 leading-relaxed" x-text="cap.resumen"></p>
                      </div>
                    </div>
                    <template x-if="relatoActivo.youtube_url">
                      <a :href="relatoActivo.youtube_url + '&t=' + cap.segundos + 's'" target="_blank" rel="noopener noreferrer" class="text-[11px] font-semibold text-damask-light hover:text-white whitespace-nowrap transition flex items-center gap-1 self-end sm:self-auto">
                        Ver instante ↗
                      </a>
                    </template>
                  </div>
                </template>
              </div>
            </div>

            <!-- Panel 3: Personajes & Biblia Visual (Avatares y fichas inmutables) -->
            <div x-show="vistaPestana === 'personajes'" x-cloak class="space-y-6">
              <div class="border-b border-border-subtle pb-3">
                <h3 class="font-bold text-sm text-text-bright">Fichas de Consistencia de Personajes</h3>
                <p class="text-xs text-text-muted">Perfiles psicológicos, rasgos físicos inmutables y avatares de referencia visual.</p>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <template x-for="p in relatoActivo.personajes" :key="p.id">
                  <div class="rounded-xl bg-obsidian-elevated border border-border-subtle p-5 flex flex-col justify-between">
                    <div>
                      <!-- Avatares si existen -->
                      <div class="grid grid-cols-2 gap-2 mb-4" x-show="p.avatar_cabeza || p.avatar_cuerpo">
                        <template x-if="p.avatar_cabeza">
                          <div class="aspect-video rounded-lg overflow-hidden border border-border-subtle bg-black">
                            <img :src="p.avatar_cabeza" :alt="'Avatar cabeza: ' + p.nombre" class="w-full h-full object-cover">
                          </div>
                        </template>
                        <template x-if="p.avatar_cuerpo">
                          <div class="aspect-video rounded-lg overflow-hidden border border-border-subtle bg-black">
                            <img :src="p.avatar_cuerpo" :alt="'Avatar cuerpo: ' + p.nombre" class="w-full h-full object-cover">
                          </div>
                        </template>
                      </div>

                      <div class="flex items-center justify-between mb-2">
                        <h4 class="text-base font-bold text-text-bright" x-text="p.nombre"></h4>
                        <span class="text-xs px-2 py-0.5 rounded bg-plum/60 text-damask-light font-semibold" x-text="p.rol"></span>
                      </div>

                      <div class="space-y-2 text-xs text-text-muted">
                        <div><strong class="text-text-main">Rasgos:</strong> <span x-text="p.rasgos"></span></div>
                        <div x-show="p.motivacion"><strong class="text-text-main">Motivación:</strong> <span x-text="p.motivacion"></span></div>
                        <div x-show="p.conflicto"><strong class="text-text-main">Conflicto:</strong> <span x-text="p.conflicto"></span></div>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </div>

            <!-- Panel 4: Locución & Audios Oficiales -->
            <div x-show="vistaPestana === 'locucion'" x-cloak class="space-y-6">
              <div class="border-b border-border-subtle pb-3">
                <h3 class="font-bold text-sm text-text-bright">Trinidad de Voces de Estudio Calibradas</h3>
                <p class="text-xs text-text-muted">Tres pistas de audio masterizadas a 192 kbps (48 kHz) con duraciones milimétricamente igualadas.</p>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                
                <div class="p-4 rounded-xl bg-obsidian-elevated border border-border-subtle flex flex-col justify-between">
                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <span class="font-bold text-text-bright">🇪🇸 Español de España</span>
                      <span class="px-2 py-0.5 rounded bg-crimson text-white font-bold text-[10px]">Máster Vídeo</span>
                    </div>
                    <div class="text-text-main font-semibold">Voz: Álvaro Neural</div>
                    <p class="text-text-muted mt-2 leading-relaxed">Pista de referencia para el vídeo Full HD 1080p con movimiento Ken Burns.</p>
                  </div>
                  <div class="mt-4 pt-3 border-t border-border-subtle text-[11px] text-damask-light">Duración: <span x-text="relatoActivo.duracion_audio"></span></div>
                </div>

                <div class="p-4 rounded-xl bg-obsidian-elevated border border-border-subtle flex flex-col justify-between">
                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <span class="font-bold text-text-bright">🌎 Español Latinoamericano</span>
                      <span class="px-2 py-0.5 rounded bg-plum text-text-bright font-bold text-[10px]">YouTube Studio</span>
                    </div>
                    <div class="text-text-main font-semibold">Voz: Alonso Neural</div>
                    <p class="text-text-muted mt-2 leading-relaxed">Español neutro con tempo calibrado para reproducirse en sincronía perfecta con las escenas.</p>
                  </div>
                  <div class="mt-4 pt-3 border-t border-border-subtle text-[11px] text-damask-light">Duración calibrada a <span x-text="relatoActivo.duracion_audio"></span></div>
                </div>

                <div class="p-4 rounded-xl bg-obsidian-elevated border border-border-subtle flex flex-col justify-between">
                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <span class="font-bold text-text-bright">🇺🇸 Inglés Internacional</span>
                      <span class="px-2 py-0.5 rounded bg-plum text-text-bright font-bold text-[10px]">YouTube Studio</span>
                    </div>
                    <div class="text-text-main font-semibold">Voz: Christopher Neural</div>
                    <p class="text-text-muted mt-2 leading-relaxed">Adaptación íntegra al inglés para distribución internacional en YouTube Multi-audio.</p>
                  </div>
                  <div class="mt-4 pt-3 border-t border-border-subtle text-[11px] text-damask-light">Duración calibrada a <span x-text="relatoActivo.duracion_audio"></span></div>
                </div>

              </div>
            </div>

          </div>

        </div>

      </div>
    </section>

    <!-- Catálogo de Relatos Completo con Filtros Reactivos -->
    <section id="catalogo" class="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <!-- Cabecera de Sección y Controles -->
      <div class="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <span class="text-xs uppercase font-bold tracking-wider text-damask">Biblioteca Multimedia</span>
          <h2 class="text-2xl sm:text-3xl font-extrabold text-text-bright mt-1">Catálogo de Historias</h2>
          <p class="text-xs text-text-muted mt-1">Selecciona cualquier relato para abrirlo en el visor o consultar su ficha completa.</p>
        </div>

        <!-- Buscador reactivo -->
        <div class="w-full md:w-72">
          <label for="buscar-relato" class="sr-only">Buscar por título, temática o personaje</label>
          <div class="relative">
            <input type="text" id="buscar-relato" x-model="busqueda" placeholder="Buscar por título o palabra clave..." 
                   class="w-full px-4 py-2 pl-9 rounded-lg bg-obsidian-card border border-border-subtle text-xs text-text-main placeholder-text-muted focus:outline-none focus:border-damask focus:ring-1 focus:ring-crimson transition">
            <svg class="w-4 h-4 text-text-muted absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </div>
        </div>
      </div>

      <!-- Barra de Filtros Temáticos por Categoría -->
      <div class="flex flex-wrap items-center gap-2 mb-8 text-xs">
        <button @click="filtroCategoria = 'todos'" :class="filtroCategoria === 'todos' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="px-3.5 py-1.5 rounded-full border transition font-medium">Todos (<span x-text="relatos.length"></span>)</button>
        <button @click="filtroCategoria = 'suspense'" :class="filtroCategoria === 'suspense' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="px-3.5 py-1.5 rounded-full border transition font-medium">Suspense & Thriller</button>
        <button @click="filtroCategoria = 'scifi'" :class="filtroCategoria === 'scifi' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="px-3.5 py-1.5 rounded-full border transition font-medium">Ciencia Ficción</button>
        <button @click="filtroCategoria = 'terror'" :class="filtroCategoria === 'terror' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="px-3.5 py-1.5 rounded-full border transition font-medium">Terror</button>
        <button @click="filtroCategoria = 'drama'" :class="filtroCategoria === 'drama' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="px-3.5 py-1.5 rounded-full border transition font-medium">Drama</button>
        <button @click="filtroCategoria = 'misterio'" :class="filtroCategoria === 'misterio' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="px-3.5 py-1.5 rounded-full border transition font-medium">Misterio</button>
        <button @click="filtroCategoria = 'historico'" :class="filtroCategoria === 'historico' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="px-3.5 py-1.5 rounded-full border transition font-medium">Histórico</button>
      </div>

      <!-- Rejilla de Tarjetas -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <template x-for="r in relatosFiltrados" :key="r.id">
          <article class="group rounded-xl bg-obsidian-card border border-border-subtle hover:border-damask transition-all duration-300 overflow-hidden flex flex-col hover:-translate-y-1 hover:shadow-xl hover:shadow-crimson/10"
                   :class="relatoActivo.id === r.id ? 'ring-2 ring-crimson border-crimson' : ''">
            
            <!-- Portada 16:9 -->
            <div class="relative aspect-video bg-black overflow-hidden border-b border-border-subtle cursor-pointer" @click="seleccionarRelato(r.id)">
              <img :src="r.portada" :alt="'Portada de ' + r.titulo" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
              
              <!-- Badges de esquina -->
              <div class="absolute top-3 left-3 flex gap-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-crimson text-white" x-text="r.id"></span>
                <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-obsidian/85 text-text-bright backdrop-blur border border-border-subtle" x-text="r.categoria_nombre"></span>
              </div>

              <!-- Duración en minutos -->
              <div class="absolute bottom-3 right-3 flex items-center gap-1.5 bg-obsidian/90 backdrop-blur px-2 py-0.5 rounded text-[11px] text-text-bright font-mono border border-border-subtle">
                <svg class="w-3.5 h-3.5 text-crimson" fill="currentColor" viewBox="0 0 20 20"><path d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"/></svg>
                <span x-text="r.duracion_audio + ' min'"></span>
              </div>
            </div>

            <!-- Contenido de la Tarjeta -->
            <div class="p-5 flex-1 flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between text-xs text-text-muted mb-2">
                  <span>≈ <span x-text="r.palabras"></span> palabras</span>
                  <span class="text-damask-light font-medium">ES • LAT • EN</span>
                </div>
                <h3 class="text-lg font-bold text-text-bright group-hover:text-damask-light transition-colors leading-snug cursor-pointer" @click="seleccionarRelato(r.id)" x-text="r.titulo"></h3>
                <p class="mt-2 text-xs text-text-muted line-clamp-3 leading-relaxed" x-text="r.sinopsis"></p>
              </div>

              <!-- Botones de Acción -->
              <div class="mt-5 pt-4 border-t border-border-subtle flex items-center justify-between text-xs">
                <button @click="seleccionarRelato(r.id)" class="font-semibold text-crimson-glow group-hover:text-white flex items-center gap-1 transition">
                  <span>Ver en Visor</span>
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                </button>
                <a :href="r.pagina_url" class="text-text-muted hover:text-white transition font-medium">
                  Ficha completa →
                </a>
              </div>
            </div>
          </article>
        </template>
      </div>

      <!-- Si la búsqueda no arroja resultados -->
      <div x-show="relatosFiltrados.length === 0" x-cloak class="text-center py-12">
        <p class="text-sm text-text-muted">No se encontraron relatos para el filtro o término seleccionado.</p>
        <button @click="busqueda = ''; filtroCategoria = 'todos'" class="mt-3 text-xs text-crimson hover:underline font-semibold">Restablecer filtros</button>
      </div>

    </section>

    <!-- Sección El Universo Raupulus -->
    <section id="universo" class="py-16 bg-obsidian-card/40 border-t border-border-subtle">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-2xl mx-auto mb-12">
          <span class="text-xs uppercase font-bold tracking-wider text-damask">Pilares de Producción</span>
          <h2 class="text-2xl sm:text-3xl font-extrabold text-text-bright mt-1">El Universo de Raupulus Tales</h2>
          <p class="text-xs sm:text-sm text-text-muted mt-2">Cómo concebimos cada historia desde la idea original hasta el máster audiovisual.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-xs">
          
          <div class="p-6 rounded-xl bg-obsidian border border-border-subtle">
            <div class="w-10 h-10 rounded-lg bg-crimson/20 border border-crimson/50 text-crimson-glow flex items-center justify-center mb-4">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
            </div>
            <h3 class="text-sm font-bold text-text-bright mb-2">Narrativa Literaria con Alma</h3>
            <p class="text-text-muted leading-relaxed">
              Cada historia cuenta con una extensión de 1.600 a 2.400 palabras, estructurada para leerse con calma y disfrute literario o escucharse en voz alta con cadencia humana.
            </p>
          </div>

          <div class="p-6 rounded-xl bg-obsidian border border-border-subtle">
            <div class="w-10 h-10 rounded-lg bg-plum/50 border border-damask/50 text-damask-light flex items-center justify-center mb-4">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 100-6 3 3 0 000 6z"/></svg>
            </div>
            <h3 class="text-sm font-bold text-text-bright mb-2">Trinidad de Voces Multilingües</h3>
            <p class="text-text-muted leading-relaxed">
              Locución en estudio a 192 kbps: Álvaro (España), Alonso (Latinoamérica) y Christopher (Inglés), con tempo y duración calibrados exactamente al segundo.
            </p>
          </div>

          <div class="p-6 rounded-xl bg-obsidian border border-border-subtle">
            <div class="w-10 h-10 rounded-lg bg-damask/20 border border-damask/50 text-text-bright flex items-center justify-center mb-4">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
            </div>
            <h3 class="text-sm font-bold text-text-bright mb-2">Cinematografía y Consistencia</h3>
            <p class="text-text-muted leading-relaxed">
              Storyboards rigurosos, avatares anatómicos de referencia en 3 posiciones y vídeo a 1080p con grano analógico y movimiento de cámara Ken Burns.
            </p>
          </div>

        </div>
      </div>
    </section>

  </main>

  <!-- Footer Oficial -->
  <footer class="bg-obsidian border-t border-border-subtle py-12 text-xs text-text-muted">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
      
      <div class="flex items-center gap-3">
        <img src="assets/images/logo.webp" alt="Raupulus Logo" width="32" height="32" class="w-8 h-8 rounded-full border border-border-subtle">
        <div>
          <div class="font-bold text-text-bright">Raupulus Tales</div>
          <div class="text-[10px] text-text-muted">Ficción Multimedia & Storytelling Digital</div>
        </div>
      </div>

      <!-- Enlaces del Ecosistema -->
      <div class="flex flex-wrap items-center justify-center gap-6">
        <a href="https://raupulus.dev" target="_blank" rel="noopener noreferrer" class="hover:text-text-bright transition">raupulus.dev</a>
        <a href="https://music.raupulus.dev" target="_blank" rel="noopener noreferrer" class="hover:text-text-bright transition">music.raupulus.dev</a>
        <a href="{YT_CHANNEL}" target="_blank" rel="noopener noreferrer" class="hover:text-text-bright transition">YouTube Oficial</a>
        <a href="mailto:{PUBLIC_EMAIL}" class="hover:text-text-bright transition">{PUBLIC_EMAIL}</a>
      </div>

      <div class="text-center md:text-right text-[11px]">
        <span>© 2026 Raupulus Tales. Todos los derechos reservados.</span>
      </div>

    </div>
  </footer>

  <!-- Datos y Lógica Reactiva Alpine.js -->
  <script>
    function talesApp() {{
      const rawRelatos = {json.dumps(relatos, ensure_ascii=False)};

      return {{
        relatos: rawRelatos,
        filtroCategoria: 'todos',
        busqueda: '',
        idiomaActivo: 'es-ES',
        vistaPestana: 'relato',
        menuAbierto: false,
        videoReproduciendo: false,
        relatoActivo: rawRelatos[0] || {{}},

        initApp() {{
          // Comprobar hash en la URL para abrir relato concreto
          const hash = window.location.hash;
          if (hash) {{
            const found = this.relatos.find(r => r.url_hash === hash || ('#' + r.id) === hash || ('#' + r.slug) === hash);
            if (found) {{
              this.relatoActivo = found;
            }}
          }}
        }},

        get relatosFiltrados() {{
          return this.relatos.filter(r => {{
            // Filtro por categoría temática
            const coincideCat = (this.filtroCategoria === 'todos') ||
                                (r.categoria === this.filtroCategoria) ||
                                (r.generos && r.generos.some(g => g.toLowerCase().includes(this.filtroCategoria)));
            
            // Filtro por texto de búsqueda
            const query = this.busqueda.trim().toLowerCase();
            if (!query) return coincideCat;

            const coincideBusqueda = r.titulo.toLowerCase().includes(query) ||
                                     r.sinopsis.toLowerCase().includes(query) ||
                                     (r.personajes && r.personajes.some(p => p.nombre.toLowerCase().includes(query))) ||
                                     (r.generos && r.generos.some(g => g.toLowerCase().includes(query)));
            
            return coincideCat && coincideBusqueda;
          }});
        }},

        seleccionarRelato(id) {{
          const found = this.relatos.find(r => r.id === id);
          if (found) {{
            this.relatoActivo = found;
            this.videoReproduciendo = false;
            window.location.hash = found.id + '-' + found.slug;
            
            // Desplazar suavemente hacia el visor
            const el = document.getElementById('visor-relato');
            if (el) {{
              el.scrollIntoView({{ behavior: 'smooth' }});
            }}
          }}
        }},

        irAUltimoEstreno() {{
          if (this.relatos.length > 0) {{
            this.seleccionarRelato(this.relatos[0].id);
          }}
        }},

        siguienteRelato() {{
          const idx = this.relatos.findIndex(r => r.id === this.relatoActivo.id);
          if (idx !== -1 && idx < this.relatos.length - 1) {{
            this.seleccionarRelato(this.relatos[idx + 1].id);
          }} else {{
            this.seleccionarRelato(this.relatos[0].id);
          }}
        }},

        anteriorRelato() {{
          const idx = this.relatos.findIndex(r => r.id === this.relatoActivo.id);
          if (idx > 0) {{
            this.seleccionarRelato(this.relatos[idx - 1].id);
          }} else {{
            this.seleccionarRelato(this.relatos[this.relatos.length - 1].id);
          }}
        }},

        reproducirVideo() {{
          this.videoReproduciendo = true;
        }}
      }};
    }}
  </script>
</body>
</html>
"""
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ index.html generado con éxito ({os.path.getsize(target_file)} bytes)")


def generate_story_pages(relatos):
    """Genera las páginas estáticas independientes relatos/NNNN-slug.html para SEO y lectura directa."""
    for idx, r in enumerate(relatos):
        prev_r = relatos[idx - 1] if idx > 0 else relatos[-1]
        next_r = relatos[idx + 1] if idx < len(relatos) - 1 else relatos[0]
        page_file = os.path.join(BASE_DIR, "relatos", f"{r['id']}-{r['slug']}.html")

        # Capítulos HTML
        caps_html = []
        for c in r.get('capitulos', []):
            yt_link = f"<a href='{r['youtube_url']}&t={c['segundos']}s' target='_blank' rel='noopener noreferrer' class='text-[11px] text-damask-light hover:text-white'>Ver instante ↗</a>" if r.get('youtube_url') else ""
            caps_html.append(f"""
            <div class="p-4 rounded-xl bg-obsidian-elevated border border-border-subtle flex flex-col sm:flex-row sm:items-start justify-between gap-3">
              <div class="flex items-start gap-3">
                <span class="font-mono text-xs font-bold text-crimson px-2.5 py-1 rounded bg-obsidian border border-border-subtle">{c['tiempo']}</span>
                <div>
                  <h4 class="text-sm font-bold text-text-bright">{c['titulo']}</h4>
                  <p class="text-xs text-text-muted mt-1 leading-relaxed">{c['resumen']}</p>
                </div>
              </div>
              {yt_link}
            </div>
            """)
        caps_rendered = "\n".join(caps_html)

        # Personajes HTML
        chars_html = []
        for p in r.get('personajes', []):
            av_html = ""
            if p.get('avatar_cabeza') or p.get('avatar_cuerpo'):
                img1 = f"<div class='aspect-video rounded bg-black overflow-hidden border border-border-subtle'><img src='../{p['avatar_cabeza']}' alt='Avatar cabeza {p['nombre']}' class='w-full h-full object-cover'></div>" if p.get('avatar_cabeza') else ""
                img2 = f"<div class='aspect-video rounded bg-black overflow-hidden border border-border-subtle'><img src='../{p['avatar_cuerpo']}' alt='Avatar cuerpo {p['nombre']}' class='w-full h-full object-cover'></div>" if p.get('avatar_cuerpo') else ""
                av_html = f"<div class='grid grid-cols-2 gap-2 mb-3'>{img1}{img2}</div>"

            chars_html.append(f"""
            <div class="p-5 rounded-xl bg-obsidian-elevated border border-border-subtle flex flex-col justify-between">
              <div>
                {av_html}
                <div class="flex items-center justify-between mb-2">
                  <h4 class="text-base font-bold text-text-bright">{p['nombre']}</h4>
                  <span class="text-xs px-2 py-0.5 rounded bg-plum/60 text-damask-light font-semibold">{p['rol']}</span>
                </div>
                <div class="space-y-1.5 text-xs text-text-muted">
                  <div><strong class="text-text-main">Rasgos:</strong> {p['rasgos']}</div>
                  {f"<div><strong class='text-text-main'>Motivación:</strong> {p['motivacion']}</div>" if p.get('motivacion') else ""}
                  {f"<div><strong class='text-text-main'>Conflicto:</strong> {p['conflicto']}</div>" if p.get('conflicto') else ""}
                </div>
              </div>
            </div>
            """)
        chars_rendered = "\n".join(chars_html)

        # Video embed or poster
        if r.get('youtube_id'):
            video_block = f"""
            <div class="relative aspect-video bg-black overflow-hidden border-b border-border-subtle">
              <iframe src="https://www.youtube-nocookie.com/embed/{r['youtube_id']}?rel=0&modestbranding=1" 
                      title="{r['titulo']} — Raupulus Tales" 
                      class="w-full h-full border-0" 
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                      allowfullscreen></iframe>
            </div>
            """
        else:
            video_block = f"""
            <div class="relative aspect-video bg-black overflow-hidden border-b border-border-subtle">
              <img src="../{r['portada']}" alt="Portada de {r['titulo']}" class="w-full h-full object-cover opacity-75">
              <div class="absolute inset-0 bg-obsidian/75 flex flex-col items-center justify-center text-center p-6">
                <div class="text-lg font-bold text-white">Próximo Estreno Cinematográfico 1080p</div>
                <p class="text-xs text-text-muted mt-1">Vídeo Full HD y locuciones en proceso de sincronización.</p>
                <a href="{YT_CHANNEL}" target="_blank" rel="noopener noreferrer" class="mt-4 px-4 py-2 rounded-lg bg-yt-red text-white text-xs font-semibold hover:bg-red-700 transition">Suscribirse al canal</a>
              </div>
            </div>
            """

        page_html = f"""<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{r['titulo']} — Relato #{r['id']} | Raupulus Tales</title>
  <meta name="description" content="{r['sinopsis']}">
  <meta name="keywords" content="{r['titulo']}, Raupulus, Relatos, {', '.join(r['generos'])}">
  <link rel="canonical" href="{SITE_URL}/{r['pagina_url']}">

  <!-- Open Graph -->
  <meta property="og:site_name" content="Raupulus Tales">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{SITE_URL}/{r['pagina_url']}">
  <meta property="og:title" content="{r['titulo']} — Raupulus Tales">
  <meta property="og:description" content="{r['sinopsis']}">
  <meta property="og:image" content="{SITE_URL}/{r['portada']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{r['titulo']} — Raupulus Tales">
  <meta name="twitter:description" content="{r['sinopsis']}">
  <meta name="twitter:image" content="{SITE_URL}/{r['portada']}">

  <link rel="icon" type="image/webp" href="../assets/images/logo.webp">
  <link rel="stylesheet" href="../assets/css/tailwind.css">
  <script defer src="../assets/js/alpine.min.js"></script>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "ShortStory",
    "name": "{r['titulo']}",
    "description": "{r['sinopsis']}",
    "inLanguage": "es-ES",
    "genre": "{r['categoria_nombre']}",
    "wordCount": {r['palabras']},
    "url": "{SITE_URL}/{r['pagina_url']}",
    "image": "{SITE_URL}/{r['portada']}",
    "author": {{
      "@type": "Person",
      "name": "Raupulus"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "Raupulus Tales",
      "logo": "{SITE_URL}/assets/images/logo.png"
    }}
  }}
  </script>
</head>
<body class="bg-obsidian text-text-main min-h-screen flex flex-col selection:bg-crimson selection:text-white"
      x-data="{{ vistaPestana: 'relato' }}">

  <header class="sticky top-0 z-50 backdrop-blur-md bg-obsidian/90 border-b border-border-subtle">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <a href="../index.html" class="flex items-center gap-3 group">
        <img src="../assets/images/logo.webp" alt="Raupulus Logo" width="36" height="36" class="w-9 h-9 rounded-full border border-damask/50">
        <div>
          <span class="font-bold text-base text-text-bright tracking-wider">RAUPULUS</span>
          <span class="text-[9px] tracking-widest text-text-muted uppercase block -mt-1 font-semibold">TALES • RELATOS</span>
        </div>
      </a>
      <div class="flex items-center gap-4 text-xs">
        <a href="../index.html#catalogo" class="text-text-muted hover:text-white transition">← Catálogo</a>
        <a href="{YT_CHANNEL}" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 rounded-lg bg-yt-red text-white font-semibold">YouTube</a>
      </div>
    </div>
  </header>

  <main class="flex-1 py-10">
    <div class="max-w-4xl mx-auto px-4 sm:px-6">
      
      <!-- Navegación entre historias -->
      <div class="flex items-center justify-between text-xs text-text-muted mb-6 pb-3 border-b border-border-subtle">
        <a href="{prev_r['slug']}.html" class="hover:text-white transition">← Anterior: {prev_r['titulo']}</a>
        <a href="../index.html#catalogo" class="hover:text-white transition font-medium">Índice</a>
        <a href="{next_r['slug']}.html" class="hover:text-white transition">Siguiente: {next_r['titulo']} →</a>
      </div>

      <!-- Cabecera -->
      <div class="mb-6">
        <div class="flex items-center gap-2 mb-2">
          <span class="px-2.5 py-0.5 rounded text-xs font-bold bg-crimson text-white">{r['id']}</span>
          <span class="px-2.5 py-0.5 rounded text-xs font-semibold bg-plum/60 border border-damask/40 text-text-bright">{r['categoria_nombre']}</span>
          <span class="text-xs text-text-muted">• {r['palabras']} palabras • {r['duracion_audio']} min narración</span>
        </div>
        <h1 class="text-3xl sm:text-4xl font-extrabold text-text-bright">{r['titulo']}</h1>
      </div>

      <!-- Visor -->
      <div class="rounded-2xl bg-obsidian border border-border-subtle overflow-hidden shadow-2xl mb-12">
        {video_block}

        <!-- Pestañas -->
        <div class="flex border-b border-border-subtle bg-obsidian-elevated px-4 text-xs font-semibold">
          <button @click="vistaPestana = 'relato'" :class="vistaPestana === 'relato' ? 'text-white border-crimson bg-obsidian' : 'text-text-muted hover:text-white border-transparent'" class="px-5 py-3 border-b-2 transition">📖 Relato</button>
          <button @click="vistaPestana = 'capitulos'" :class="vistaPestana === 'capitulos' ? 'text-white border-crimson bg-obsidian' : 'text-text-muted hover:text-white border-transparent'" class="px-5 py-3 border-b-2 transition">🎬 Capítulos ({len(r.get('capitulos', []))})</button>
          <button @click="vistaPestana = 'personajes'" :class="vistaPestana === 'personajes' ? 'text-white border-crimson bg-obsidian' : 'text-text-muted hover:text-white border-transparent'" class="px-5 py-3 border-b-2 transition">👤 Personajes ({len(r.get('personajes', []))})</button>
        </div>

        <div class="p-6 md:p-10">
          <!-- Relato -->
          <div x-show="vistaPestana === 'relato'" class="max-w-prose mx-auto">
            <div class="p-4 rounded-xl bg-obsidian-card border border-border-subtle mb-8 text-xs sm:text-sm text-text-muted italic leading-relaxed">
              <strong class="text-damask-light not-italic block mb-1">Sinopsis:</strong>
              {r['sinopsis']}
            </div>
            <div class="text-text-main">
              {r['relato_html']}
            </div>
          </div>

          <!-- Capítulos -->
          <div x-show="vistaPestana === 'capitulos'" class="space-y-3">
            {caps_rendered}
          </div>

          <!-- Personajes -->
          <div x-show="vistaPestana === 'personajes'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {chars_rendered}
          </div>
        </div>
      </div>

    </div>
  </main>

  <footer class="bg-obsidian border-t border-border-subtle py-8 text-xs text-text-muted text-center">
    <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div>© 2026 Raupulus Tales. Todos los derechos reservados.</div>
      <div class="flex gap-4">
        <a href="../index.html" class="hover:text-white">Inicio</a>
        <a href="{YT_CHANNEL}" target="_blank" rel="noopener noreferrer" class="hover:text-white">YouTube Oficial</a>
        <a href="mailto:{PUBLIC_EMAIL}" class="hover:text-white">{PUBLIC_EMAIL}</a>
      </div>
    </div>
  </footer>
</body>
</html>
"""
        with open(page_file, 'w', encoding='utf-8') as pf:
            pf.write(page_html)

    print(f"✅ Generadas {len(relatos)} páginas individuales en relatos/")


def generate_sitemap_and_robots(relatos):
    """Genera sitemap.xml y robots.txt oficiales."""
    now_date = datetime.now().strftime("%Y-%m-%d")
    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <url><loc>{SITE_URL}/</loc><lastmod>{now_date}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>'
    ]
    for r in relatos:
        sitemap_lines.append(f"  <url><loc>{SITE_URL}/{r['pagina_url']}</loc><lastmod>{now_date}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>")
    sitemap_lines.append('</urlset>')

    with open(os.path.join(BASE_DIR, "sitemap.xml"), 'w', encoding='utf-8') as f:
        f.write("\n".join(sitemap_lines))

    robots_txt = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    with open(os.path.join(BASE_DIR, "robots.txt"), 'w', encoding='utf-8') as f:
        f.write(robots_txt)
    print("✅ sitemap.xml y robots.txt generados con éxito")


def compile_css():
    """Ejecuta la transpilación de Tailwind CSS v4 para que assets/css/tailwind.css esté listo."""
    print("🎨 Compilando Tailwind CSS...")
    try:
        res = subprocess.run(["npx", "@tailwindcss/cli", "-i", "src/input.css", "-o", "assets/css/tailwind.css", "--minify"], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        print("✅ Tailwind CSS compilado correctamente.")
    except Exception as e:
        print(f"⚠️ Error al compilar CSS: {e}")


def main():
    print("🚀 Iniciando compilación de relatos.raupulus.dev...")
    relatos = sync_assets_and_data()
    generate_index_html(relatos)
    generate_story_pages(relatos)
    generate_sitemap_and_robots(relatos)
    compile_css()
    print("✨ Sitio web compilado y listo para desplegar al 100%.")


if __name__ == "__main__":
    main()
