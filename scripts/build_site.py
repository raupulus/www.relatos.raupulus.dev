#!/usr/bin/env python3
"""
Raupulus Tales — scripts/build_site.py
Generador estático optimizado para SEO y sincronizador oficial para relatos.raupulus.dev.

Arquitectura:
- index.html: Catálogo principal con diseño editorial, filtros temáticos reactivos,
  buscador en tiempo real, hero cinemático y tarjetas 16:9 con enlace directo a cada relato.
- relatos/NNNN-slug.html: Página dedicada independiente por cada relato con texto completo,
  marcas de tiempo, reproductor de YouTube, personajes y metadatos SEO / Schema.org individuales.
"""

import os
import sys
import glob
import re
import json
import shutil
import subprocess
import zoneinfo
from datetime import datetime
from PIL import Image

MADRID_TZ = zoneinfo.ZoneInfo("Europe/Madrid")


def parse_iso_datetime(dt_str):
    if not dt_str:
        return None
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=MADRID_TZ)
        return dt
    except Exception:
        return None


def get_current_time():
    """Retorna la hora actual en zona horaria oficial Europe/Madrid, admitiendo override vía BUILD_NOW."""
    custom_now = os.environ.get("BUILD_NOW")
    if custom_now:
        parsed = parse_iso_datetime(custom_now)
        if parsed:
            return parsed
    return datetime.now(tz=MADRID_TZ)


def is_story_published(story, now_dt=None):
    """
    Determina si un relato se considera publicado en base a su fecha de publicación
    o su estado previo. Si cuenta con fecha_publicacion fiable, evalúa si la hora actual
    ha superado dicho timestamp en la zona horaria oficial (Europe/Madrid).
    """
    if now_dt is None:
        now_dt = get_current_time()
    fecha_pub_str = story.get("fecha_publicacion")
    if fecha_pub_str:
        dt_pub = parse_iso_datetime(fecha_pub_str)
        if dt_pub:
            return now_dt >= dt_pub
    ts_pub = story.get("fecha_publicacion_ts")
    if ts_pub:
        return now_dt.timestamp() >= ts_pub
    return bool(story.get("publicado")) and story.get("estado") == "publicado"


def format_spanish_schedule_date(iso_str):
    """Formatea la fecha de estreno en formato legible en español."""
    if not iso_str:
        return "Próximamente"
    dt = parse_iso_datetime(iso_str)
    if not dt:
        return "Próximamente"
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    return f"{dt.day} de {meses[dt.month - 1]} de {dt.year} a las {dt.strftime('%H:%M')} h"

SITE_URL = "https://relatos.raupulus.dev"
YT_CHANNEL = "https://www.youtube.com/@RaupulusTales"
YT_SUBSCRIBE = "https://www.youtube.com/@RaupulusTales?sub_confirmation=1"
PUBLIC_EMAIL = "public@raupulus.dev"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORIAS_SRC_DEFAULT = os.environ.get("RELATOS_SRC_DIR", "")
if not HISTORIAS_SRC_DEFAULT:
    _candidates = glob.glob(os.path.expanduser("~/Library/CloudStorage/GoogleDrive-*/Mi unidad/ia/Relatos/Historias"))
    if _candidates and os.path.exists(_candidates[0]):
        HISTORIAS_SRC_DEFAULT = _candidates[0]

PUBLIC_DIR = os.path.join(BASE_DIR, "public")
DATA_DIR = os.path.join(BASE_DIR, "data")
RELATOS_DIR = os.path.join(PUBLIC_DIR, "relatos")
PORTADAS_DIR = os.path.join(PUBLIC_DIR, "assets", "images", "portadas")
AVATARS_DIR = os.path.join(PUBLIC_DIR, "assets", "images", "avatars")
ESCENAS_DIR = os.path.join(PUBLIC_DIR, "assets", "images", "escenas")
SRC_ASSETS_DIR = os.path.join(BASE_DIR, "src", "assets")
ROOT_RELATOS_FILE = os.path.join(BASE_DIR, "relatos.json")
DATA_FILE = os.path.join(DATA_DIR, "relatos.json")


def clean_narrative_text(txt, story_id=None, inline_images=None):
    """
    Limpia y formatea el relato en párrafos legibles con tipografía editorial.
    Si se proporciona una lista de inline_images (ej. 5 escenas clave del storyboard),
    las distribuye equitativamente a lo largo del texto entre los párrafos de forma armoniosa.
    """
    paragraphs = txt.strip().split("\n\n")
    html_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p == "* * *":
            html_paragraphs.append('<div class="scene-divider my-10 text-center text-damask-light font-serif tracking-widest text-xl font-bold select-none">* * *</div>')
        elif p.startswith("—") or p.startswith("- "):
            clean_p = p.lstrip("- ")
            html_paragraphs.append(f'<p class="mb-6 leading-relaxed text-text-main text-base sm:text-lg pl-3 border-l-2 border-damask/40 font-serif">{clean_p}</p>')
        elif p.startswith("«") and p.endswith("»"):
            html_paragraphs.append(f'<blockquote class="my-6 pl-4 border-l-2 border-crimson italic text-text-muted text-base sm:text-lg font-serif">{p}</blockquote>')
        else:
            html_paragraphs.append(f'<p class="mb-6 leading-relaxed text-text-main text-base sm:text-lg font-serif">{p}</p>')

    # Intercalar imágenes si existen para la historia
    if inline_images and len(html_paragraphs) > 6:
        num_imgs = len(inline_images)
        # Calcular posiciones distribuidas sin tocar los primeros 2 ni los últimos 2 párrafos
        step = max(3, len(html_paragraphs) // (num_imgs + 1))
        positions = [step * (i + 1) for i in range(num_imgs)]
        
        # Insertar de atrás hacia adelante para mantener los índices
        for pos, img_data in reversed(list(zip(positions, inline_images))):
            target_idx = min(pos, len(html_paragraphs) - 2)
            caption = img_data.get('caption', '')
            img_src = img_data.get('src', '')
            alt_text = img_data.get('alt', 'Escena cinematográfica del relato')
            
            fig_html = f"""
            <figure class="my-10 rounded-xl overflow-hidden bg-obsidian-card border border-border-subtle shadow-xl group">
              <div class="relative aspect-video bg-black overflow-hidden">
                <img src="../{img_src}" alt="{alt_text}" width="1280" height="720" loading="lazy" class="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-500">
                <div class="absolute inset-0 bg-gradient-to-t from-obsidian/90 via-transparent to-transparent opacity-80 pointer-events-none"></div>
              </div>
              <figcaption class="p-3.5 text-xs text-text-muted italic border-t border-border-subtle flex items-center justify-between">
                <span>{caption}</span>
                <span class="text-[10px] text-damask-light font-mono not-italic uppercase tracking-wider">Escena Oficial</span>
              </figcaption>
            </figure>
            """
            html_paragraphs.insert(target_idx, fig_html)

    return "\n".join(html_paragraphs)


def clean_chapter_title(title):
    """Elimina menciones técnicas a archivos o clips de apertura."""
    t = re.sub(r'\s*\((?:Clip|Clips) de apertura\)', '', title, flags=re.I)
    t = re.sub(r'\s*\(video\d+\.mp4\)', '', t, flags=re.I)
    t = re.sub(r'\s*\(Planos[^\)]*\)', '', t, flags=re.I)
    return t.strip()


def truncate_meta_desc(text, max_len=155):
    """Trunca el texto para meta description en una palabra limpia antes del límite."""
    clean_t = re.sub(r'\s+', ' ', text).strip()
    if len(clean_t) <= max_len:
        return clean_t
    cut = clean_t[:max_len]
    last_space = cut.rfind(' ')
    if last_space > 0:
        cut = cut[:last_space]
    return cut.rstrip('.,;:!?') + '…'


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
    },
    "0025": {
        0: "Apertura en el piso de la calle de la Palma; los preparativos minuciosos de Valeria y el inicio de la cena íntima con Adrián.",
        164: "El timbre inesperado a medianoche, la llegada de Marcos y el impacto paralizante al descubrir la presencia de Lucía.",
        248: "La colisión en el salón: el cruce de coartadas fallidas, miradas de reproche y la caída estrepitosa de las máscaras.",
        411: "La partida precipitada de los invitados, la mesa destrozada y el silencio asfixiante entre Valeria y Adrián en la madrugada.",
        495: "El reencuentro en la obra de Sagasta bajo el polvo y el cemento: una conversación franca sin cobardías ni rencores.",
        611: "La tarjeta de boda que llega por correo, el viaje solitario a Jávea y el cierre sereno de una herida del pasado.",
        737: "El retorno al piso de Malasaña, el brindis cómplice a oscuras y el rescate definitivo de una amistad madura y leal."
    },
    "0047": {
        0: "El timbre de Marcos no suena en el cruce de las cuatro esquinas y su madre asegura no tener ningún hijo.",
        141: "El pupitre de Marcos desaparece del aula y Lucía encuentra una tuerca de bronce grabada en su bolsillo.",
        252: "Una figura alta bajo la farola de medianoche muestra un rostro ondulante donde asoma por instantes la cara de Marcos.",
        335: "Lucía encara a Julián en la vieja fábrica harinera y descubre cómo la realidad cose el vacío de sus víctimas.",
        515: "En casa de la abuela Carmen, Lucía lucha por rescatar el recuerdo del nieto antes de que el borrado sea irreversible.",
        633: "Un alarido resuena en el molino, la fotografía recupera el color y Marcos reaparece en el pueblo.",
        733: "Durante la cena familiar, Lucía descubre en un viejo álbum a otra víctima olvidada desde el verano de 1972."
    }
}


def sync_assets_and_data(src_dir=HISTORIAS_SRC_DEFAULT):
    """Extrae datos de historias, convierte portadas/avatares a WebP y genera data/relatos.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PORTADAS_DIR, exist_ok=True)
    os.makedirs(AVATARS_DIR, exist_ok=True)
    os.makedirs(ESCENAS_DIR, exist_ok=True)
    os.makedirs(RELATOS_DIR, exist_ok=True)
    os.makedirs(os.path.join(PUBLIC_DIR, "assets", "js"), exist_ok=True)
    os.makedirs(os.path.join(PUBLIC_DIR, "assets", "images"), exist_ok=True)
    os.makedirs(os.path.join(PUBLIC_DIR, "assets", "css"), exist_ok=True)

    # Copiar activos estáticos maestros (Alpine.js, Logos, Favicon en WebP) desde src/assets hacia public/assets
    if os.path.exists(SRC_ASSETS_DIR):
        src_images = os.path.join(SRC_ASSETS_DIR, "images")
        dest_images = os.path.join(PUBLIC_DIR, "assets", "images")
        if os.path.exists(src_images):
            for img_file in os.listdir(src_images):
                if not img_file.lower().endswith(".webp"):
                    continue
                sf = os.path.join(src_images, img_file)
                df = os.path.join(dest_images, img_file)
                if os.path.isfile(sf) and (not os.path.exists(df) or os.path.getmtime(sf) > os.path.getmtime(df)):
                    shutil.copy2(sf, df)

        src_js = os.path.join(SRC_ASSETS_DIR, "js")
        dest_js = os.path.join(PUBLIC_DIR, "assets", "js")
        if os.path.exists(src_js):
            for js_file in os.listdir(src_js):
                sf = os.path.join(src_js, js_file)
                df = os.path.join(dest_js, js_file)
                if os.path.isfile(sf) and (not os.path.exists(df) or os.path.getmtime(sf) > os.path.getmtime(df)):
                    shutil.copy2(sf, df)

    # Sincronizar archivos estáticos legales y directivas IA en public/
    for fname in ["LICENSE.md", "ai.txt"]:
        src_f = os.path.join(BASE_DIR, fname)
        dest_f = os.path.join(PUBLIC_DIR, fname)
        if os.path.exists(src_f):
            if not os.path.exists(dest_f) or os.path.getmtime(src_f) > os.path.getmtime(dest_f):
                shutil.copy2(src_f, dest_f)

    force_sync = "--sync" in sys.argv or "--force" in sys.argv or bool(os.environ.get("FORCE_SYNC"))
    # Prioridad: si existe relatos.json en la raíz del proyecto web y no se fuerza sincronización, usarlo directamente
    if os.path.exists(ROOT_RELATOS_FILE) and not force_sync:
        print("📄 Cargando base de datos canónica desde relatos.json en la raíz...")
        with open(ROOT_RELATOS_FILE, 'r', encoding='utf-8') as f:
            relatos = json.load(f)
        changed = False
        for r in relatos:
            if r.get("fecha_publicacion"):
                dt_p = parse_iso_datetime(r["fecha_publicacion"])
                if dt_p:
                    ts = int(dt_p.timestamp())
                    if r.get("fecha_publicacion_ts") != ts:
                        r["fecha_publicacion_ts"] = ts
                        changed = True
            if r.get("fecha_publicacion") or r.get("fecha_publicacion_ts"):
                is_pub = is_story_published(r)
                if r.get("publicado") != is_pub:
                    r["publicado"] = is_pub
                    changed = True
                if is_pub and r.get("estado") in ("programado", "estreno"):
                    r["estado"] = "publicado"
                    changed = True
                elif not is_pub and r.get("estado") in ("publicado", "programado"):
                    r["estado"] = "estreno"
                    changed = True
            # Asegurar quinteto de locuciones oficiales
            if "locucion" in r and isinstance(r["locucion"], dict):
                if "pt_BR" not in r["locucion"]:
                    r["locucion"]["pt_BR"] = {"voz": "Antonio (pt-BR-AntonioNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Locución en portugués de Brasil"}
                    changed = True
                if "de_DE" not in r["locucion"]:
                    r["locucion"]["de_DE"] = {"voz": "Killian (de-DE-KillianNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Locución en alemán de Alemania"}
                    changed = True
        if changed:
            with open(ROOT_RELATOS_FILE, 'w', encoding='utf-8') as f:
                json.dump(relatos, f, ensure_ascii=False, indent=2)
        # Asegurar sincronización con data/relatos.json
        with open(DATA_FILE, 'w', encoding='utf-8') as df:
            json.dump(relatos, df, ensure_ascii=False, indent=2)
        return relatos

    if not os.path.exists(src_dir):
        print(f"Directorio fuente {src_dir} no accesible, usando data/relatos.json existente...")
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                relatos = json.load(f)
            changed = False
            for r in relatos:
                if r.get("fecha_publicacion") or r.get("fecha_publicacion_ts"):
                    is_pub = is_story_published(r)
                    if r.get("publicado") != is_pub:
                        r["publicado"] = is_pub
                        changed = True
                    if is_pub and r.get("estado") in ("programado", "estreno"):
                        r["estado"] = "publicado"
                        changed = True
                    elif not is_pub and r.get("estado") == "publicado":
                        r["estado"] = "programado"
                        changed = True
            if changed:
                with open(DATA_FILE, 'w', encoding='utf-8') as df:
                    json.dump(relatos, df, ensure_ascii=False, indent=2)
            with open(ROOT_RELATOS_FILE, 'w', encoding='utf-8') as rf:
                json.dump(relatos, rf, ensure_ascii=False, indent=2)
            return relatos
        return []

    # Mapa de estados y publicaciones previas para preservar decisiones manuales al resincronizar
    existing_status_map = {}
    if os.path.exists(ROOT_RELATOS_FILE):
        try:
            with open(ROOT_RELATOS_FILE, 'r', encoding='utf-8') as erf:
                prev_list = json.load(erf)
                for pr in prev_list:
                    existing_status_map[pr['id']] = {
                        "estado": pr.get("estado"),
                        "publicado": pr.get("publicado"),
                        "fecha_publicacion": pr.get("fecha_publicacion"),
                        "fecha_publicacion_ts": pr.get("fecha_publicacion_ts")
                    }
        except Exception:
            pass

    story_dirs = sorted([d for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d)) and re.match(r'^\d{4}-', d)])
    relatos = []

    for sdir in story_dirs:
        sp = os.path.join(src_dir, sdir)
        num_id = sdir[:4]
        slug = sdir[5:]

        # Criterio estricto de inclusión en la web:
        # Solo se incorporan a la web relatos que estén de verdad subidos a YouTube (tengan yt_id)
        # y cuenten con todos los activos completos (vídeo renderizado, subtítulos y portada).
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

        video_rendered = os.path.exists(os.path.join(sp, 'video', f"{sdir}-1080p-watermark.mp4"))
        has_subtitles = bool(glob.glob(os.path.join(sp, 'subtitulos', f"{num_id}-*.srt")))
        has_portada_src = os.path.exists(os.path.join(sp, 'youtube', 'portada.jpg')) or os.path.exists(os.path.join(sp, 'youtube', 'portada-es-ES.jpg'))

        # Si no tiene ID de YouTube o no tiene los activos mínimos terminados, se ignora hasta que se suba
        if not yt_id or not video_rendered or not has_subtitles or not has_portada_src:
            continue

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

        # Avatares WebP (convertir antes de asociar a personajes)
        avatars_src_dir = os.path.join(sp, 'avatars')
        if os.path.exists(avatars_src_dir):
            for af in glob.glob(os.path.join(avatars_src_dir, '*.png')):
                bname = os.path.splitext(os.path.basename(af))[0]
                dest_av = os.path.join(AVATARS_DIR, f"{num_id}-{bname}.webp")
                if not os.path.exists(dest_av) or os.path.getmtime(af) > os.path.getmtime(dest_av):
                    with Image.open(af) as im:
                        im.save(dest_av, 'WEBP', quality=85)

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

                c_slug = cname.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n')
                c_words = [w for w in re.findall(r'\b[a-z]{3,}\b', c_slug) if w not in ('don','dona','senor','senora')]
                avatar_cabeza = None
                avatar_cuerpo = None
                best_score_cabeza = 0
                best_score_cuerpo = 0

                for av_file in os.listdir(AVATARS_DIR) if os.path.exists(AVATARS_DIR) else []:
                    if av_file.startswith(num_id):
                        score = 0
                        if f"personaje-{cidx:02d}" in av_file or f"personaje-{cidx}-" in av_file:
                            score += 10
                        score += sum(1 for w in c_words if w in av_file.lower())
                        if score > 0:
                            if 'cabeza' in av_file and score > best_score_cabeza:
                                avatar_cabeza = f"assets/images/avatars/{av_file}"
                                best_score_cabeza = score
                            elif 'cuerpo' in av_file and score > best_score_cuerpo:
                                avatar_cuerpo = f"assets/images/avatars/{av_file}"
                                best_score_cuerpo = score

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

        # Portada WebP
        portada_webp = f"assets/images/portadas/{sdir}.webp"
        portada_src = os.path.join(sp, 'youtube', 'portada.jpg')
        if not os.path.exists(portada_src):
            portada_src = os.path.join(sp, 'youtube', 'portada-es-ES.jpg')
        if os.path.exists(portada_src):
            dest_portada = os.path.join(PUBLIC_DIR, portada_webp)
            if not os.path.exists(dest_portada) or os.path.getmtime(portada_src) > os.path.getmtime(dest_portada):
                with Image.open(portada_src) as im:
                    im.save(dest_portada, 'WEBP', quality=85)

        # Escenas WebP para intercalar en el relato literario (5 escenas clave distribuidas a lo largo del texto)
        escenas_src_dir = os.path.join(sp, 'escenas')
        inline_images = []
        if os.path.exists(escenas_src_dir):
            all_esc_pngs = sorted([f for f in glob.glob(os.path.join(escenas_src_dir, '*.png')) if not os.path.basename(f).startswith('video')])
            if len(all_esc_pngs) >= 5:
                # Seleccionar 5 escenas representativas a lo largo de la narración
                indices = [0, len(all_esc_pngs) // 4, len(all_esc_pngs) // 2, (len(all_esc_pngs) * 3) // 4, -1]
                chosen_pngs = [all_esc_pngs[i] for i in indices]
            elif all_esc_pngs:
                chosen_pngs = all_esc_pngs
            else:
                chosen_pngs = []

            for c_png in chosen_pngs:
                bname = os.path.splitext(os.path.basename(c_png))[0]
                dest_esc = os.path.join(ESCENAS_DIR, f"{num_id}-{bname}.webp")
                rel_web_path = f"assets/images/escenas/{num_id}-{bname}.webp"
                if not os.path.exists(dest_esc) or os.path.getmtime(c_png) > os.path.getmtime(dest_esc):
                    with Image.open(c_png) as im:
                        im.save(dest_esc, 'WEBP', quality=85)
                
                # Obtener descripción/caption legible a partir del nombre
                clean_name = re.sub(r'^\d+[a-z]?-', '', bname).replace('-', ' ').capitalize()
                inline_images.append({
                    "src": rel_web_path,
                    "caption": f"Ilustración de escena: {clean_name}",
                    "alt": f"Escena oficial de {titulo} — {clean_name}"
                })

        # Capítulos
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
                    c_summary = sum_map.get(c_sec, f"Acontecimientos del capítulo correspondientes al bloque de {c_time}.")
                    chapters.append({
                        "tiempo": c_time,
                        "segundos": c_sec,
                        "titulo": c_title,
                        "resumen": c_summary
                    })

        # Asignar estado y publicación respetando valores previos existentes o evaluando fecha_publicacion
        prev_info = existing_status_map.get(num_id, {})
        fecha_pub = prev_info.get("fecha_publicacion")
        fecha_pub_ts = prev_info.get("fecha_publicacion_ts")

        if fecha_pub:
            is_pub = is_story_published({"fecha_publicacion": fecha_pub})
            estado_final = "publicado" if is_pub else "programado"
            pub_final = is_pub
        else:
            estado_final = prev_info.get("estado")
            pub_final = prev_info.get("publicado")
            if estado_final is None and pub_final is None:
                estado_final = "estreno"
                pub_final = False

        relato_entry = {
            "id": num_id,
            "slug": slug,
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
            "escenas_ilustraciones": inline_images,
            "relato_raw": relato_raw,
            "relato_html": clean_narrative_text(relato_raw, story_id=num_id, inline_images=inline_images),
            "locucion": {
                "es_ES": {"voz": "Álvaro (es-ES-AlvaroNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Voz máster y vídeo"},
                "es_LAT": {"voz": "Alonso (es-US-AlonsoNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Voz neutra latinoamericana"},
                "en_US": {"voz": "Christopher (en-US-ChristopherNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Narración internacional en inglés"},
                "pt_BR": {"voz": "Antonio (pt-BR-AntonioNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Locución en portugués de Brasil"},
                "de_DE": {"voz": "Killian (de-DE-KillianNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Locución en alemán de Alemania"}
            },
            "estado": estado_final,
            "publicado": bool(pub_final),
            "fecha_publicacion": fecha_pub,
            "fecha_publicacion_ts": fecha_pub_ts
        }
        relatos.append(relato_entry)

    # Ordenar el catálogo con los últimos relatos arriba (orden descendente por ID)
    relatos = sorted(relatos, key=lambda x: x["id"], reverse=True)

    with open(ROOT_RELATOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(relatos, f, ensure_ascii=False, indent=2)

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(relatos, f, ensure_ascii=False, indent=2)

    print(f"✅ Sincronizados {len(relatos)} relatos en {ROOT_RELATOS_FILE}")
    return relatos


def generate_index_html(relatos):
    """Genera index.html optimizado para SEO: catálogo visual con tarjetas 16:9 que enlazan a cada página dedicada."""
    target_file = os.path.join(PUBLIC_DIR, "index.html")

    # Serializar catálogo ligero para Alpine.js (sin inyectar el texto completo de los relatos en el index)
    catalogo_light = []
    for r in relatos:
        is_published = is_story_published(r)
        catalogo_light.append({
            "id": r["id"],
            "slug": r["slug"],
            "pagina_url": r["pagina_url"],
            "titulo": r["titulo"],
            "sinopsis": r["sinopsis"],
            "categoria": r["categoria"],
            "categoria_nombre": r["categoria_nombre"],
            "generos": r["generos"],
            "palabras": r["palabras"],
            "lectura_min": r["lectura_min"],
            "duracion_audio": r["duracion_audio"],
            "portada": r["portada"],
            "youtube_id": r["youtube_id"],
            "estado": "publicado" if is_published else r.get("estado", "programado"),
            "publicado": is_published,
            "fecha_publicacion": r.get("fecha_publicacion"),
            "fecha_publicacion_ts": r.get("fecha_publicacion_ts")
        })

    # Schema.org hasPart estructurado
    has_part = [
        {
            "@type": "ShortStory",
            "name": r["titulo"],
            "url": f"{SITE_URL}/{r['pagina_url']}",
            "description": truncate_meta_desc(r["sinopsis"], 155),
            "inLanguage": "es-ES"
        }
        for r in relatos
    ]
    has_part_json = json.dumps(has_part, ensure_ascii=False, indent=6)

    # Elementos noscript para indexación SEO sin JavaScript
    noscript_items = "\n".join([
        f'''            <li class="border-b border-border-subtle/50 pb-3 last:border-b-0">
              <a href="{r['pagina_url']}" class="text-sm font-bold text-damask-light hover:underline">{r['id']} — {r['titulo']}</a>
              <p class="text-xs text-text-muted mt-1">{truncate_meta_desc(r['sinopsis'], 155)}</p>
              <span class="text-[10px] text-text-muted font-mono">{r['categoria_nombre']} • {r['palabras']} palabras • {r['duracion_audio']} min</span>
            </li>'''
        for r in relatos
    ])

    # Último relato publicado de verdad para el botón principal del Hero (por fecha de publicación más reciente)
    publicados = [r for r in relatos if is_story_published(r)]
    if publicados:
        ultimo_publicado = max(publicados, key=lambda x: x.get("fecha_publicacion_ts") or 0)
    else:
        ultimo_publicado = relatos[0]

    html = f"""<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Raupulus Tales — Portal Oficial de Relatos y Ficción Multimedia</title>
  <meta name="description" content="Portal oficial de Raupulus Tales. Descubre historias completas de suspense, terror, ciencia ficción y drama, audiolibros multilingües y producciones cinematográficas en vídeo 1080p.">
  <meta name="keywords" content="Raupulus Tales, Relatos, Cuentos, Ficción Sonora, Audiolibros, Historias de Terror, Suspense, Ciencia Ficción">
  <meta name="author" content="Raupulus Tales">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="ai" content="noai, noimageai">
  <meta name="google-extended" content="none">
  <link rel="author" href="ai.txt" type="text/plain">
  <meta name="theme-color" content="#941300">
  <link rel="canonical" href="{SITE_URL}/">

  <!-- Open Graph / Redes Sociales -->
  <meta property="og:site_name" content="Raupulus Tales">
  <meta property="og:locale" content="es_ES">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{SITE_URL}/">
  <meta property="og:title" content="Raupulus Tales — Historias y Ficción Multimedia">
  <meta property="og:description" content="Relatos literarios con audiolibros multilingües y producciones cinematográficas en vídeo 1080p.">
  <meta property="og:image" content="{SITE_URL}/assets/images/og-raupulus-tales.webp">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Raupulus Tales — Portal Oficial de Relatos y Ficción Multimedia">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@RaupulusTales">
  <meta name="twitter:title" content="Raupulus Tales — Historias y Ficción Multimedia">
  <meta name="twitter:description" content="Relatos de ficción multimedia con audiolibros calibrados y vídeos Full HD 1080p.">
  <meta name="twitter:image" content="{SITE_URL}/assets/images/og-raupulus-tales.webp">
  <meta name="twitter:image:alt" content="Raupulus Tales — Portal Oficial de Relatos y Ficción Multimedia">

  <!-- Iconos locales oficiales de Raupulus Tales -->
  <link rel="icon" type="image/webp" href="assets/images/favicon.webp">
  <link rel="apple-touch-icon" type="image/webp" href="assets/images/favicon.webp">

  <!-- CSS local pretranspilado (Sin CDNs externos) -->
  <link rel="stylesheet" href="assets/css/tailwind.css">

  <!-- Alpine.js local -->
  <script defer src="assets/js/alpine.min.js"></script>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "Catálogo Oficial de Relatos — Raupulus Tales",
    "url": "{SITE_URL}/",
    "description": "Colección de relatos literarios originales de ficción, suspense, ciencia ficción y drama con audiolibros en tres idiomas y vídeos cinematográficos.",
    "publisher": {{
      "@type": "Organization",
      "name": "Raupulus Tales",
      "logo": "{SITE_URL}/assets/images/logo.webp"
    }},
    "hasPart": {has_part_json}
  }}
  </script>
</head>
<body class="bg-obsidian text-text-main min-h-screen flex flex-col selection:bg-crimson selection:text-white"
      x-data="talesCatalog()">

  <!-- Enlace de salto a contenido principal (A11Y) -->
  <a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:z-50 focus:px-4 focus:py-2 focus:bg-crimson focus:text-white focus:rounded-lg focus:shadow-xl focus:outline-none">Saltar al contenido principal</a>

  <!-- Fondo ambiental cinemático -->
  <div class="fixed inset-0 pointer-events-none -z-10 overflow-hidden" aria-hidden="true">
    <div class="absolute -top-40 left-1/2 -translate-x-1/2 w-[850px] h-[550px] bg-gradient-to-b from-crimson/15 via-plum/10 to-transparent blur-3xl opacity-75"></div>
    <div class="absolute top-1/3 -right-48 w-[650px] h-[650px] bg-damask/10 blur-3xl rounded-full"></div>
    <div class="absolute bottom-10 -left-48 w-[550px] h-[550px] bg-plum/15 blur-3xl rounded-full"></div>
  </div>

  <!-- Header / Navbar Oficial -->
  <header class="sticky top-0 z-50 backdrop-blur-md bg-obsidian/90 border-b border-border-subtle transition-all">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      
      <!-- Brand & Logotipo Oficial de Raupulus Tales -->
      <a href="#" class="flex items-center gap-3 group focus:outline-none focus-visible:ring-2 focus-visible:ring-crimson rounded-lg p-1" aria-label="Raupulus Tales - Inicio">
        <div class="relative w-10 h-10 rounded-full overflow-hidden border border-damask/50 group-hover:border-crimson transition-colors duration-300">
          <img src="assets/images/logo-160.webp" alt="Raupulus Tales Logo Oficial" width="40" height="40" class="w-full h-full object-cover">
        </div>
        <div class="flex flex-col">
          <span class="font-bold text-lg text-text-bright tracking-wider group-hover:text-damask-light transition-colors">RAUPULUS</span>
          <span class="text-[10px] tracking-widest text-text-muted uppercase -mt-1 font-semibold">TALES • RELATOS</span>
        </div>
      </a>

      <!-- Navegación central -->
      <nav class="hidden md:flex items-center gap-6 text-sm font-medium">
        <a href="#catalogo" class="text-text-main hover:text-text-bright hover:underline underline-offset-4 decoration-crimson transition">Catálogo</a>
        <a href="#universo" class="text-text-main hover:text-text-bright hover:underline underline-offset-4 decoration-crimson transition">El Universo</a>
        <a href="LICENSE.md" class="text-text-muted hover:text-text-main transition text-xs">Propiedad & Derechos</a>

        <!-- Botón Canal YouTube -->
        <a href="{YT_CHANNEL}" target="_blank" rel="noopener noreferrer" 
           class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-yt-red/90 hover:bg-yt-red text-white text-xs font-semibold tracking-wide transition shadow-sm hover:shadow-crimson/50">
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
          Canal YouTube
        </a>
      </nav>

      <!-- Menú Móvil con ARIA y touch target 44px -->
      <button @click="menuAbierto = !menuAbierto" :aria-expanded="menuAbierto.toString()" aria-controls="mobile-menu" class="md:hidden min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg text-text-muted hover:text-text-bright hover:bg-obsidian-card focus:outline-none focus-visible:ring-2 focus-visible:ring-crimson" aria-label="Abrir menú de navegación">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
      </button>
    </div>

    <!-- Menú desplegable móvil -->
    <div id="mobile-menu" x-show="menuAbierto" @click.away="menuAbierto = false" x-cloak class="md:hidden border-b border-border-subtle bg-obsidian-card px-4 py-4 space-y-3">
      <a href="#catalogo" @click="menuAbierto = false" class="block text-sm text-text-main hover:text-text-bright">Catálogo de Relatos</a>
      <a href="#universo" @click="menuAbierto = false" class="block text-sm text-text-main hover:text-text-bright">El Universo</a>
      <a href="LICENSE.md" class="block text-sm text-text-muted hover:text-text-main">Aviso de Propiedad Intelectual</a>
      <a href="{YT_CHANNEL}" target="_blank" rel="noopener noreferrer" class="block text-sm font-semibold text-yt-red">YouTube Oficial ↗</a>
    </div>
  </header>

  <!-- Contenido Principal -->
  <main class="flex-1" id="main-content">

    <!-- Hero Section -->
    <section class="relative py-16 md:py-24 border-b border-border-subtle overflow-hidden">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
        
        <div class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-plum/40 border border-damask/40 text-xs font-semibold text-text-bright mb-6">
          <svg class="w-4 h-4 text-crimson-glow flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 18v-6a9 9 0 0 1 18 0v6"></path>
            <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"></path>
          </svg>
          <span>Ficción Multimedia • Audiolibros Calibrados • Escenas Full HD 1080p</span>
        </div>

        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-text-bright tracking-tight max-w-4xl mx-auto leading-tight">
          Historias que se leen, se escuchan y <span class="text-transparent bg-clip-text bg-gradient-to-r from-crimson via-damask to-damask-light">cobran vida</span>
        </h1>
        
        <p class="mt-6 text-base sm:text-lg text-text-muted max-w-2xl mx-auto leading-relaxed">
          Cada relato cuenta con su propia página dedicada: texto íntegro para lectura inmersiva, desglose de capítulos narrativos, fichas visuales de personajes y producciones en vídeo Full HD con locución multilingüe.
        </p>

        <!-- Accesos rápidos del Hero con fallback SSR -->
        <div class="mt-8 flex flex-wrap items-center justify-center gap-4">
          <a href="{ultimo_publicado['pagina_url']}" :href="ultimoPublicado?.pagina_url" class="px-6 py-3 rounded-lg bg-crimson hover:bg-crimson-glow text-white font-semibold text-sm transition-all duration-200 glow-crimson flex items-center gap-2">
            <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            <span>Leer Último Estreno (<span x-text="ultimoPublicado?.titulo">{ultimo_publicado['titulo']}</span>)</span>
          </a>
          <a href="#catalogo" class="px-6 py-3 rounded-lg bg-obsidian-card hover:bg-obsidian-elevated border border-border-subtle hover:border-damask text-text-main font-semibold text-sm transition-all duration-200">
            Explorar las <span x-text="relatos.length">{len(relatos)}</span> Historias
          </a>
        </div>
      </div>
    </section>

    <!-- Catálogo de Relatos Completo con Filtros Reactivos -->
    <section id="catalogo" class="scroll-mt-20 py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <!-- Cabecera de Sección y Controles -->
      <div class="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <span class="text-xs uppercase font-bold tracking-wider text-damask-light">Biblioteca de Ficción</span>
          <h2 class="text-2xl sm:text-3xl font-extrabold text-text-bright mt-1">Catálogo de Historias</h2>
          <p class="text-xs text-text-muted mt-1">Haz clic en cualquier historia para acceder a su página dedicada con lectura completa y contenido multimedia.</p>
        </div>

        <!-- Buscador reactivo -->
        <div class="w-full md:w-80">
          <label for="buscar-relato" class="sr-only">Buscar por título, temática o personaje</label>
          <div class="relative">
            <input type="text" id="buscar-relato" x-model="busqueda" placeholder="Buscar por título o palabra clave..." 
                   class="w-full min-h-[44px] px-4 py-2.5 pl-9 rounded-lg bg-obsidian-card border border-border-subtle text-xs text-text-main placeholder-text-muted focus:outline-none focus:border-damask focus:ring-1 focus:ring-crimson transition">
            <svg class="w-4 h-4 text-text-muted absolute left-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </div>
        </div>
      </div>

      <!-- Barra de Filtros Temáticos por Categoría con touch targets 44px -->
      <div class="flex flex-wrap items-center gap-2 mb-8 text-xs">
        <button @click="filtroCategoria = 'todos'" :class="filtroCategoria === 'todos' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="min-h-[44px] inline-flex items-center px-4 py-2 rounded-full border transition font-medium">Todos (<span x-text="relatos.length">{len(relatos)}</span>)</button>
        <button @click="filtroCategoria = 'suspense'" :class="filtroCategoria === 'suspense' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="min-h-[44px] inline-flex items-center px-4 py-2 rounded-full border transition font-medium">Suspense & Thriller</button>
        <button @click="filtroCategoria = 'scifi'" :class="filtroCategoria === 'scifi' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="min-h-[44px] inline-flex items-center px-4 py-2 rounded-full border transition font-medium">Ciencia Ficción</button>
        <button @click="filtroCategoria = 'terror'" :class="filtroCategoria === 'terror' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="min-h-[44px] inline-flex items-center px-4 py-2 rounded-full border transition font-medium">Terror</button>
        <button @click="filtroCategoria = 'drama'" :class="filtroCategoria === 'drama' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="min-h-[44px] inline-flex items-center px-4 py-2 rounded-full border transition font-medium">Drama</button>
        <button @click="filtroCategoria = 'misterio'" :class="filtroCategoria === 'misterio' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="min-h-[44px] inline-flex items-center px-4 py-2 rounded-full border transition font-medium">Misterio</button>
        <button @click="filtroCategoria = 'historico'" :class="filtroCategoria === 'historico' ? 'bg-crimson text-white border-crimson' : 'bg-obsidian-card text-text-muted border-border-subtle hover:text-white'" class="min-h-[44px] inline-flex items-center px-4 py-2 rounded-full border transition font-medium">Histórico</button>
      </div>

      <!-- Rejilla de Tarjetas -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <template x-for="(r, index) in relatosFiltrados" :key="r.id">
          <article class="group rounded-xl bg-obsidian-card border border-border-subtle hover:border-damask transition-all duration-300 overflow-hidden flex flex-col hover:-translate-y-1 hover:shadow-xl hover:shadow-crimson/15">
            
            <!-- Portada 16:9 con enlace a la página dedicada -->
            <a :href="r.pagina_url" class="relative aspect-video bg-black overflow-hidden border-b border-border-subtle block" :aria-label="'Abrir relato ' + r.titulo">
              <img :src="r.portada" :alt="'Portada oficial del relato ' + r.titulo" width="1280" height="720" :loading="index < 3 ? 'eager' : 'lazy'" :fetchpriority="index === 0 ? 'high' : 'auto'" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
              
              <!-- Badges de esquina -->
              <div class="absolute top-3 left-3 flex gap-2 z-20">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-crimson text-white" x-text="r.id"></span>
                <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-obsidian/85 text-text-bright backdrop-blur border border-border-subtle" x-text="r.categoria_nombre"></span>
                <template x-if="!estaPublicado(r)">
                  <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-damask/90 text-white border border-damask-light/40">Estreno</span>
                </template>
              </div>

              <!-- Duración en minutos -->
              <div class="absolute bottom-3 right-3 flex items-center gap-1.5 bg-obsidian/90 backdrop-blur px-2 py-0.5 rounded text-[11px] text-text-bright font-mono border border-border-subtle z-20">
                <svg class="w-3.5 h-3.5 text-crimson-text" fill="currentColor" viewBox="0 0 20 20"><path d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"/></svg>
                <span x-text="r.duracion_audio + ' min'"></span>
              </div>

              <!-- Overlay fondo negro transparente de Próximo Estreno -->
              <div x-show="!estaPublicado(r)" 
                   class="absolute inset-0 bg-black/75 backdrop-blur-[1px] flex flex-col items-center justify-center p-4 text-center z-10 transition-opacity">
                <span class="px-3 py-1 rounded-full bg-crimson/90 border border-crimson text-white text-xs font-bold uppercase tracking-widest shadow-xl flex items-center gap-1.5">
                  <svg class="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"/></svg>
                  Estreno Programado
                </span>
                <span class="text-[11px] text-text-bright mt-2 font-medium" x-text="formatearFechaEstreno(r.fecha_publicacion, r.fecha_publicacion_ts)"></span>
                <span class="text-[10px] text-text-muted mt-0.5">en YouTube</span>
              </div>
            </a>

            <!-- Contenido de la Tarjeta -->
            <div class="p-5 flex-1 flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between text-xs text-text-muted mb-2">
                  <span>≈ <span x-text="r.palabras"></span> palabras</span>
                  <span class="text-damask-light font-medium">ES • LAT • EN • PT • DE</span>
                </div>
                <h3 class="text-lg font-bold text-text-bright group-hover:text-damask-light transition-colors leading-snug">
                  <a :href="r.pagina_url" x-text="r.titulo"></a>
                </h3>
                <p class="mt-2 text-xs text-text-muted line-clamp-3 leading-relaxed" x-text="r.sinopsis"></p>
              </div>

              <!-- Botones de Acción -->
              <div class="mt-5 pt-4 border-t border-border-subtle flex items-center justify-between text-xs">
                <a :href="r.pagina_url" class="font-semibold text-crimson-glow group-hover:text-white flex items-center gap-1 transition">
                  <span x-text="estaPublicado(r) ? 'Leer Relato Dedicado' : 'Ver Ficha de Estreno'"></span>
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                </a>
                <span class="inline-flex items-center gap-1 text-[11px] text-text-muted font-medium">
                  <svg class="w-3 h-3 text-damask-light" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/></svg>
                  <span x-text="estaPublicado(r) ? 'Audio & Vídeo HD' : (r.fecha_publicacion_ts ? 'Estreno 20:00 h' : 'En producción')"></span>
                </span>
              </div>
            </div>
          </article>
        </template>
      </div>

      <!-- Si la búsqueda no arroja resultados -->
      <div x-show="relatosFiltrados.length === 0" x-cloak class="text-center py-12">
        <p class="text-sm text-text-muted">No se encontraron relatos para el filtro o término seleccionado.</p>
        <button @click="busqueda = ''; filtroCategoria = 'todos'" class="mt-3 text-xs text-crimson-text hover:underline font-semibold">Restablecer filtros</button>
      </div>

      <!-- Fallback estático para motores de búsqueda y usuarios sin JavaScript -->
      <noscript>
        <div class="mt-8 p-6 rounded-xl bg-obsidian-card border border-border-subtle">
          <h3 class="text-lg font-bold text-text-bright mb-4">Índice Completo de Historias (Versión Estática)</h3>
          <ul class="space-y-4">
{noscript_items}
          </ul>
        </div>
      </noscript>

    </section>

    <!-- Sección El Universo Raupulus -->
    <section id="universo" class="scroll-mt-20 py-16 bg-obsidian-card/40 border-t border-border-subtle">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-2xl mx-auto mb-12">
          <span class="text-xs uppercase font-bold tracking-wider text-damask-light">Pilares de Producción</span>
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
            <h3 class="text-sm font-bold text-text-bright mb-2">Quinteto de Voces Multilingües</h3>
            <p class="text-text-muted leading-relaxed">
              Locución en estudio a 192 kbps: Álvaro (España), Alonso (Latinoamérica), Christopher (Inglés), Antonio (Portugués de Brasil) y Killian (Alemán), con tempo y duración calibrados exactamente al segundo.
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

  <!-- Footer Oficial con Reserva Estricta de Derechos -->
  <footer class="bg-obsidian border-t border-border-subtle py-12 text-xs text-text-muted">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
      
      <div class="flex items-center gap-3">
        <img src="assets/images/logo-160.webp" alt="Raupulus Tales Logo Oficial" width="32" height="32" class="w-8 h-8 rounded-full border border-border-subtle">
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
        <a href="LICENSE.md" class="hover:text-text-bright text-damask-light font-semibold transition">Propiedad & Derechos</a>
        <a href="mailto:{PUBLIC_EMAIL}" class="hover:text-text-bright transition">{PUBLIC_EMAIL}</a>
      </div>

      <div class="text-center md:text-right text-[11px] leading-relaxed">
        <span class="block">Código web bajo <a href="LICENSE.md" class="underline hover:text-white">AGPLv3</a> • © 2026 Raupulus Tales.</span>
        <span class="text-text-muted/75 text-[10px]">Contenido literario y audiovisual bajo reserva estricta de derechos. Prohibida copia, comercialización o uso en IA.</span>
      </div>

    </div>
  </footer>

  <!-- Lógica Reactiva Alpine.js para Catálogo -->
  <script>
    function talesCatalog() {{
      const rawRelatos = {json.dumps(catalogo_light, ensure_ascii=False)};

      return {{
        relatos: rawRelatos,
        filtroCategoria: 'todos',
        busqueda: '',
        menuAbierto: false,
        ahora: Date.now(),

        init() {{
          setInterval(() => {{
            this.ahora = Date.now();
          }}, 10000);
        }},

        estaPublicado(r) {{
          if (r.fecha_publicacion_ts) {{
            return (r.fecha_publicacion_ts * 1000) <= this.ahora;
          }}
          return Boolean(r.publicado && r.estado === 'publicado');
        }},

        formatearFechaEstreno(isoStr, ts) {{
          if (!ts && !isoStr) return 'Próximamente';
          try {{
            const d = ts ? new Date(ts * 1000) : new Date(isoStr);
            const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
            const partes = new Intl.DateTimeFormat('es-ES', {{
              day: 'numeric', month: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Europe/Madrid'
            }}).formatToParts(d);
            const map = {{}};
            partes.forEach(p => map[p.type] = p.value);
            const mesNom = meses[parseInt(map.month, 10) - 1] || map.month;
            return `${{map.day}} ${{mesNom}} • ${{map.hour}}:${{map.minute}} h`;
          }} catch (e) {{
            return 'Próximamente';
          }}
        }},

        get ultimoPublicado() {{
          const pub = this.relatos.filter(r => this.estaPublicado(r));
          if (!pub.length) return this.relatos[0];
          return pub.reduce((latest, r) => {{
            return ((r.fecha_publicacion_ts || 0) > (latest.fecha_publicacion_ts || 0)) ? r : latest;
          }}, pub[0]);
        }},

        get relatosFiltrados() {{
          return this.relatos.filter(r => {{
            const coincideCat = (this.filtroCategoria === 'todos') ||
                                (r.categoria === this.filtroCategoria) ||
                                (r.generos && r.generos.some(g => g.toLowerCase().includes(this.filtroCategoria)));
            
            const query = this.busqueda.trim().toLowerCase();
            if (!query) return coincideCat;

            const coincideBusqueda = r.titulo.toLowerCase().includes(query) ||
                                     r.sinopsis.toLowerCase().includes(query) ||
                                     (r.generos && r.generos.some(g => g.toLowerCase().includes(query)));
            
            return coincideCat && coincideBusqueda;
          }});
        }}
      }};
    }}
  </script>
</body>
</html>
"""
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ index.html optimizado para SEO generado ({os.path.getsize(target_file)} bytes)")


def generate_story_pages(relatos):
    """Genera las páginas estáticas independientes relatos/NNNN-slug.html para SEO y lectura directa."""
    for idx, r in enumerate(relatos):
        prev_r = relatos[idx - 1] if idx > 0 else relatos[-1]
        next_r = relatos[idx + 1] if idx < len(relatos) - 1 else relatos[0]
        page_file = os.path.join(RELATOS_DIR, f"{r['id']}-{r['slug']}.html")
        is_published = is_story_published(r)
        fecha_pub = r.get("fecha_publicacion") or ""
        fecha_pub_ts = r.get("fecha_publicacion_ts") or 0
        fecha_formateada = format_spanish_schedule_date(fecha_pub)
        date_pub_schema = f'\n    "datePublished": "{fecha_pub}",' if fecha_pub else ""
        
        if not is_published:
            meta_desc = f"Próximo estreno en Raupulus Tales ({fecha_formateada}). {truncate_meta_desc(r['sinopsis'], 110)}"
        else:
            meta_desc = truncate_meta_desc(r['sinopsis'], 155)

        # Capítulos HTML
        caps_html = []
        for c in r.get('capitulos', []):
            yt_link = f"<a href='{r['youtube_url']}&t={c['segundos']}s' target='_blank' rel='noopener noreferrer' class='text-[11px] text-damask-light hover:text-white font-semibold'>Ver instante en YouTube ↗</a>" if r.get('youtube_url') else ""
            caps_html.append(f"""
            <div class="p-4 rounded-xl bg-obsidian-elevated border border-border-subtle flex flex-col sm:flex-row sm:items-start justify-between gap-3">
              <div class="flex items-start gap-3">
                <span class="font-mono text-xs font-bold text-crimson-text px-2.5 py-1 rounded bg-obsidian border border-border-subtle">{c['tiempo']}</span>
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
                img1 = f"<div class='aspect-video rounded-lg bg-black overflow-hidden border border-border-subtle'><img src='../{p['avatar_cabeza']}' alt='Avatar cabeza de {p['nombre']}' width='1280' height='720' loading='lazy' class='w-full h-full object-cover'></div>" if p.get('avatar_cabeza') else ""
                img2 = f"<div class='aspect-video rounded-lg bg-black overflow-hidden border border-border-subtle'><img src='../{p['avatar_cuerpo']}' alt='Avatar cuerpo de {p['nombre']}' width='1280' height='720' loading='lazy' class='w-full h-full object-cover'></div>" if p.get('avatar_cuerpo') else ""
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

        # Enlace directo al vídeo en YouTube
        yt_watch_url = r.get('youtube_url') or (f"https://www.youtube.com/watch?v={r['youtube_id']}" if r.get('youtube_id') else YT_CHANNEL)

        # Barra de acciones de YouTube debajo del vídeo
        video_actions = f"""
        <div class="px-4 py-3 bg-obsidian-card border-b border-border-subtle flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
          <a href="{YT_SUBSCRIBE}" target="_blank" rel="noopener noreferrer" 
             class="w-full sm:w-auto min-h-[44px] px-4 py-2 rounded-lg bg-yt-red hover:bg-red-700 text-white font-semibold flex items-center justify-center gap-2 transition shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-crimson">
            <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
            <span>Suscribirme en YouTube</span>
          </a>
          <a href="{yt_watch_url}" target="_blank" rel="noopener noreferrer" 
             class="w-full sm:w-auto min-h-[44px] px-4 py-2 rounded-lg bg-obsidian-elevated hover:bg-plum/60 border border-border-subtle hover:border-damask text-text-bright font-semibold flex items-center justify-center gap-2 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-crimson">
            <span>Ver vídeo en YouTube</span>
            <svg class="w-4 h-4 text-damask-light" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
          </a>
        </div>
        """

        # Video embed or poster
        if is_published and r.get('youtube_id'):
            video_block = f"""
            <div class="relative aspect-video bg-black overflow-hidden border-b border-border-subtle">
              <iframe src="https://www.youtube-nocookie.com/embed/{r['youtube_id']}?rel=0&modestbranding=1" 
                      title="{r['titulo']} — Raupulus Tales" 
                      class="w-full h-full border-0" 
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                      allowfullscreen></iframe>
            </div>
            {video_actions}
            """
        else:
            video_block = f"""
            <div class="relative aspect-video bg-black overflow-hidden border-b border-border-subtle">
              <img src="../{r['portada']}" alt="Portada de {r['titulo']}" width="1280" height="720" class="w-full h-full object-cover opacity-60">
              <div class="absolute inset-0 bg-black/75 backdrop-blur-[2px] flex flex-col items-center justify-center text-center p-6">
                <span class="px-3.5 py-1.5 rounded-full bg-crimson/90 border border-crimson text-white text-xs font-bold uppercase tracking-widest shadow-xl flex items-center gap-1.5 mb-3">
                  <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"/></svg>
                  Estreno Programado en YouTube
                </span>
                <div class="text-xl sm:text-2xl font-bold text-white max-w-lg mb-2">{r['titulo']}</div>
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-plum/60 border border-damask/40 text-xs font-semibold text-text-bright mb-4">
                  <svg class="w-3.5 h-3.5 text-crimson-glow" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                  <span>Fecha de estreno: {fecha_formateada}</span>
                </div>
                <p class="text-xs text-text-muted max-w-md mb-5">El vídeo y la historia completa se desbloquearán en esta página el día del estreno oficial.</p>
                <a href="{YT_SUBSCRIBE}" target="_blank" rel="noopener noreferrer" class="px-4 py-2 rounded-lg bg-yt-red text-white text-xs font-semibold hover:bg-red-700 transition shadow-lg flex items-center gap-2">
                  <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
                  Suscribirme para ver el estreno
                </a>
              </div>
            </div>
            {video_actions}
            """

        # Contenido del Relato: en estreno solo se muestra el primer párrafo para evitar plagio previo al lanzamiento
        if is_published:
            narrative_rendered = f"""
            <div class="text-text-main">
              {r['relato_html']}
            </div>
            """
            chapters_panel_content = f"""
            <div class="flex items-center justify-between border-b border-border-subtle pb-3 mb-4">
              <h3 class="font-bold text-sm text-text-bright">Estructura Dramática de la Historia</h3>
              <span class="text-xs font-mono text-damask-light font-bold">{r['duracion_audio']}</span>
            </div>
            {caps_rendered}
            """
            capitulos_btn_text = f"🎬 Capítulos ({len(r.get('capitulos', []))})"
        else:
            first_p = ""
            if r.get('relato_raw'):
                first_p = clean_narrative_text(r['relato_raw'].strip().split("\n\n")[0].strip())
            elif r.get('relato_html'):
                m_p = re.search(r'(<p\b[^>]*>[\s\S]*?</p>)', r['relato_html'])
                first_p = m_p.group(1) if m_p else ""
            if not first_p:
                first_p = f'<p class="mb-6 leading-relaxed text-text-main text-base sm:text-lg font-serif">{r["sinopsis"]}</p>'

            narrative_rendered = f"""
            <div class="text-text-main">
              {first_p}
            </div>

            <!-- Panel de Contenido Protegido hasta Estreno -->
            <div class="my-10 p-6 sm:p-8 rounded-2xl bg-gradient-to-b from-obsidian-card to-obsidian border border-damask/40 shadow-2xl text-center">
              <div class="w-12 h-12 mx-auto rounded-full bg-crimson/20 border border-crimson/50 text-crimson-glow flex items-center justify-center mb-4">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
              </div>
              <span class="inline-block px-3 py-1 rounded-full bg-crimson/30 border border-crimson/60 text-damask-light text-xs font-bold uppercase tracking-wider mb-2">Contenido Protegido • Próximo Estreno</span>
              <h3 class="text-xl sm:text-2xl font-extrabold text-text-bright mb-2">La historia completa estará disponible en su estreno oficial</h3>
              <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-plum/60 border border-damask/40 text-xs font-semibold text-text-bright mb-4">
                <svg class="w-3.5 h-3.5 text-crimson-glow" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                <span>Estreno: {fecha_formateada}</span>
              </div>
              <p class="text-xs sm:text-sm text-text-muted max-w-lg mx-auto leading-relaxed mb-6">
                Por protección estricta de derechos de autor y exclusividad editorial, el texto completo, el minutado de capítulos y las escenas cinematográficas se desbloquearán el día del estreno público en YouTube.
              </p>
              <div class="flex flex-wrap items-center justify-center gap-3">
                <a href="{YT_SUBSCRIBE}" target="_blank" rel="noopener noreferrer" class="px-5 py-2.5 rounded-lg bg-yt-red hover:bg-red-700 text-white font-semibold text-xs transition shadow-lg flex items-center gap-2">
                  <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
                  Suscribirme para ver el estreno
                </a>
                <a href="../index.html#catalogo" class="px-5 py-2.5 rounded-lg bg-obsidian-card hover:bg-obsidian-elevated border border-border-subtle text-text-main font-semibold text-xs transition">
                  Explorar historias publicadas
                </a>
              </div>
            </div>
            """
            chapters_panel_content = f"""
            <div class="p-8 text-center bg-obsidian-elevated rounded-xl border border-border-subtle">
              <div class="w-10 h-10 mx-auto rounded-full bg-plum/60 border border-damask/40 text-damask-light flex items-center justify-center mb-3">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              </div>
              <h4 class="text-sm font-bold text-text-bright mb-1">Capítulos y Momentos Clave en Reserva</h4>
              <p class="text-xs text-text-muted max-w-md mx-auto leading-relaxed">
                El minutado oficial, las escenas cinematográficas y las marcas de tiempo narrativas se revelarán públicamente al estrenarse el vídeo el <strong class="text-text-bright">{fecha_formateada}</strong>.
              </p>
            </div>
            """
            capitulos_btn_text = "🎬 Capítulos (En reserva)"

        estreno_badge = f'<span class="px-2 py-0.5 rounded text-xs font-bold bg-crimson/30 border border-crimson text-damask-light uppercase tracking-wider">Estreno: {fecha_formateada}</span>' if not is_published else ''

        page_html = f"""<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{r['titulo']} | Raupulus Tales</title>
  <meta name="description" content="{meta_desc}">
  <meta name="keywords" content="{r['titulo']}, Raupulus Tales, Relatos, {', '.join(r['generos'])}">
  <meta name="author" content="Raupulus Tales">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="ai" content="noai, noimageai">
  <meta name="google-extended" content="none">
  <link rel="author" href="../ai.txt" type="text/plain">
  <meta name="theme-color" content="#941300">
  <link rel="canonical" href="{SITE_URL}/{r['pagina_url']}">

  <!-- Open Graph / Redes Sociales (1280x720 16:9 Oficial) -->
  <meta property="og:site_name" content="Raupulus Tales">
  <meta property="og:locale" content="es_ES">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{SITE_URL}/{r['pagina_url']}">
  <meta property="og:title" content="{r['titulo']} — Raupulus Tales">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:image" content="{SITE_URL}/{r['portada']}">
  <meta property="og:image:width" content="1280">
  <meta property="og:image:height" content="720">
  <meta property="og:image:alt" content="Portada oficial del relato {r['titulo']} — Raupulus Tales">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@RaupulusTales">
  <meta name="twitter:title" content="{r['titulo']} — Raupulus Tales">
  <meta name="twitter:description" content="{meta_desc}">
  <meta name="twitter:image" content="{SITE_URL}/{r['portada']}">
  <meta name="twitter:image:alt" content="Portada oficial del relato {r['titulo']} — Raupulus Tales">

  <!-- Iconos locales oficiales de Raupulus Tales -->
  <link rel="icon" type="image/webp" href="../assets/images/favicon.webp">
  <link rel="apple-touch-icon" type="image/webp" href="../assets/images/favicon.webp">

  <link rel="stylesheet" href="../assets/css/tailwind.css">
  <script defer src="../assets/js/alpine.min.js"></script>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "ShortStory",
    "name": "{r['titulo']}",
    "description": "{meta_desc}",
    "inLanguage": "es-ES",
    "genre": "{r['categoria_nombre']}",
    "wordCount": {r['palabras']},{date_pub_schema}
    "url": "{SITE_URL}/{r['pagina_url']}",
    "image": "{SITE_URL}/{r['portada']}",
    "author": {{
      "@type": "Person",
      "name": "Raupulus"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "Raupulus Tales",
      "logo": "{SITE_URL}/assets/images/logo.webp"
    }}
  }}
  </script>
</head>
<body class="bg-obsidian text-text-main min-h-screen flex flex-col selection:bg-crimson selection:text-white"
      x-data="{{ vistaPestana: 'relato' }}">

  <!-- Enlace de salto a contenido principal (A11Y) -->
  <a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:z-50 focus:px-4 focus:py-2 focus:bg-crimson focus:text-white focus:rounded-lg focus:shadow-xl focus:outline-none">Saltar al contenido principal</a>

  <header class="sticky top-0 z-50 backdrop-blur-md bg-obsidian/90 border-b border-border-subtle">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <a href="../index.html" class="flex items-center gap-3 group focus:outline-none focus-visible:ring-2 focus-visible:ring-crimson rounded-lg p-1" aria-label="Raupulus Tales - Portada">
        <img src="../assets/images/logo-160.webp" alt="Raupulus Tales Logo Oficial" width="36" height="36" class="w-9 h-9 rounded-full border border-damask/50">
        <div>
          <span class="font-bold text-base text-text-bright tracking-wider">RAUPULUS</span>
          <span class="text-[9px] tracking-widest text-text-muted uppercase block -mt-1 font-semibold">TALES • RELATOS</span>
        </div>
      </a>
      <div class="flex items-center gap-4 text-xs">
        <a href="../index.html#catalogo" class="text-text-muted hover:text-white transition">← Catálogo Completo</a>
        <a href="{YT_CHANNEL}" target="_blank" rel="noopener noreferrer" class="px-3.5 py-1.5 rounded-lg bg-yt-red text-white font-semibold shadow-sm hover:bg-red-700 transition">YouTube</a>
      </div>
    </div>
  </header>

  <main class="flex-1 py-10" id="main-content">
    <div class="max-w-4xl mx-auto px-4 sm:px-6">
      
      <!-- Navegación entre historias (Responsive 320px+) -->
      <nav class="grid grid-cols-1 sm:grid-cols-3 gap-2 items-center text-xs text-text-muted mb-6 pb-3 border-b border-border-subtle" aria-label="Navegación entre relatos">
        <a href="{prev_r['id']}-{prev_r['slug']}.html" class="hover:text-white transition flex items-center gap-1 truncate" title="{prev_r['titulo']}">
          <span class="shrink-0 text-damask-light">←</span>
          <span class="shrink-0 text-text-muted">Anterior:</span>
          <span class="truncate">{prev_r['titulo']}</span>
        </a>
        <a href="../index.html#catalogo" class="hover:text-white transition font-medium text-center order-first sm:order-none py-1">Índice del Catálogo</a>
        <a href="{next_r['id']}-{next_r['slug']}.html" class="hover:text-white transition flex items-center justify-start sm:justify-end gap-1 truncate" title="{next_r['titulo']}">
          <span class="shrink-0 text-text-muted">Siguiente:</span>
          <span class="truncate">{next_r['titulo']}</span>
          <span class="shrink-0 text-damask-light">→</span>
        </a>
      </nav>

      <!-- Cabecera de la Historia -->
      <header class="mb-6">
        <div class="flex flex-wrap items-center gap-2 mb-2">
          <span class="px-2.5 py-0.5 rounded text-xs font-bold bg-crimson text-white">{r['id']}</span>
          <span class="px-2.5 py-0.5 rounded text-xs font-semibold bg-plum/60 border border-damask/40 text-text-bright">{r['categoria_nombre']}</span>
          {estreno_badge}
          <span class="text-xs text-text-muted">• {r['palabras']} palabras • {r['duracion_audio']} min narración</span>
        </div>
        <h1 class="text-3xl sm:text-4xl font-extrabold text-text-bright">{r['titulo']}</h1>
      </header>

      <!-- Visor Multimedia y Lectura -->
      <div class="rounded-2xl bg-obsidian border border-border-subtle overflow-hidden shadow-2xl mb-12">
        {video_block}

        <!-- Pestañas Interactivas con Accesibilidad ARIA y touch targets 44px -->
        <div role="tablist" aria-label="Secciones del relato" class="flex border-b border-border-subtle bg-obsidian-elevated px-4 text-xs font-semibold overflow-x-auto">
          <button role="tab" id="tab-relato" aria-controls="panel-relato" :aria-selected="(vistaPestana === 'relato').toString()" :tabindex="vistaPestana === 'relato' ? '0' : '-1'" @click="vistaPestana = 'relato'" :class="vistaPestana === 'relato' ? 'text-white border-crimson bg-obsidian shadow-sm' : 'text-text-muted hover:text-white border-transparent'" class="min-h-[44px] inline-flex items-center px-5 py-2.5 border-b-2 transition whitespace-nowrap focus:outline-none focus-visible:ring-2 focus-visible:ring-crimson">📖 Relato Literario</button>
          <button role="tab" id="tab-capitulos" aria-controls="panel-capitulos" :aria-selected="(vistaPestana === 'capitulos').toString()" :tabindex="vistaPestana === 'capitulos' ? '0' : '-1'" @click="vistaPestana = 'capitulos'" :class="vistaPestana === 'capitulos' ? 'text-white border-crimson bg-obsidian shadow-sm' : 'text-text-muted hover:text-white border-transparent'" class="min-h-[44px] inline-flex items-center px-5 py-2.5 border-b-2 transition whitespace-nowrap focus:outline-none focus-visible:ring-2 focus-visible:ring-crimson">{capitulos_btn_text}</button>
          <button role="tab" id="tab-personajes" aria-controls="panel-personajes" :aria-selected="(vistaPestana === 'personajes').toString()" :tabindex="vistaPestana === 'personajes' ? '0' : '-1'" @click="vistaPestana = 'personajes'" :class="vistaPestana === 'personajes' ? 'text-white border-crimson bg-obsidian shadow-sm' : 'text-text-muted hover:text-white border-transparent'" class="min-h-[44px] inline-flex items-center px-5 py-2.5 border-b-2 transition whitespace-nowrap focus:outline-none focus-visible:ring-2 focus-visible:ring-crimson">👤 Personajes ({len(r.get('personajes', []))})</button>
          <button role="tab" id="tab-locucion" aria-controls="panel-locucion" :aria-selected="(vistaPestana === 'locucion').toString()" :tabindex="vistaPestana === 'locucion' ? '0' : '-1'" @click="vistaPestana = 'locucion'" :class="vistaPestana === 'locucion' ? 'text-white border-crimson bg-obsidian shadow-sm' : 'text-text-muted hover:text-white border-transparent'" class="min-h-[44px] inline-flex items-center px-5 py-2.5 border-b-2 transition whitespace-nowrap focus:outline-none focus-visible:ring-2 focus-visible:ring-crimson">🎙️ Locución</button>
        </div>

        <div class="p-6 md:p-10">
          <!-- Panel Relato Literario -->
          <article role="tabpanel" id="panel-relato" aria-labelledby="tab-relato" tabindex="0" x-show="vistaPestana === 'relato'" class="max-w-prose mx-auto focus:outline-none">
            <div class="p-4 rounded-xl bg-obsidian-card border border-border-subtle mb-8 text-xs sm:text-sm text-text-muted italic leading-relaxed">
              <strong class="text-damask-light not-italic block mb-1">Sinopsis Oficial:</strong>
              {r['sinopsis']}
            </div>
            {narrative_rendered}

            <!-- Aviso restrictivo de derechos al pie del texto -->
            <div class="mt-12 p-4 rounded-lg bg-obsidian-card border border-border-subtle text-[11px] text-text-muted text-center leading-relaxed">
              <strong class="text-damask-light block mb-1">Aviso Legal de Propiedad Intelectual:</strong>
              Este relato es obra literaria protegida por derechos de autor (Copyright © 2026 Raupulus Tales). Queda terminantemente prohibida su comercialización, copia, reproducción total o parcial, adaptación o reutilización en modelos de IA sin autorización expresa.
            </div>
          </article>

          <!-- Panel Capítulos (Sin archivos técnicos) -->
          <div role="tabpanel" id="panel-capitulos" aria-labelledby="tab-capitulos" tabindex="0" x-show="vistaPestana === 'capitulos'" class="space-y-3 focus:outline-none">
            {chapters_panel_content}
          </div>

          <!-- Panel Personajes -->
          <div role="tabpanel" id="panel-personajes" aria-labelledby="tab-personajes" tabindex="0" x-show="vistaPestana === 'personajes'" class="grid grid-cols-1 md:grid-cols-2 gap-4 focus:outline-none">
            {chars_rendered}
          </div>

          <!-- Panel Locución -->
          <div role="tabpanel" id="panel-locucion" aria-labelledby="tab-locucion" tabindex="0" x-show="vistaPestana === 'locucion'" class="space-y-4 focus:outline-none">
            <div class="border-b border-border-subtle pb-3 mb-4">
              <h3 class="font-bold text-sm text-text-bright">Quinteto Oficial de Locuciones de Estudio</h3>
              <p class="text-xs text-text-muted">Masterizadas a 192 kbps (48 kHz) y calibradas con la duración del máster en vídeo.</p>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 text-xs">
              <div class="p-3.5 rounded-xl bg-obsidian-elevated border border-border-subtle">
                <span class="font-bold text-text-bright block mb-1">🇪🇸 España (Álvaro)</span>
                <span class="text-text-muted text-[11px]">Pista máster en vídeo Full HD.</span>
              </div>
              <div class="p-3.5 rounded-xl bg-obsidian-elevated border border-border-subtle">
                <span class="font-bold text-text-bright block mb-1">🌎 Latinoamérica (Alonso)</span>
                <span class="text-text-muted text-[11px]">Español neutro disponible en YouTube.</span>
              </div>
              <div class="p-3.5 rounded-xl bg-obsidian-elevated border border-border-subtle">
                <span class="font-bold text-text-bright block mb-1">🇺🇸 Inglés (Christopher)</span>
                <span class="text-text-muted text-[11px]">Adaptación oficial internacional.</span>
              </div>
              <div class="p-3.5 rounded-xl bg-obsidian-elevated border border-border-subtle">
                <span class="font-bold text-text-bright block mb-1">🇧🇷 Portugués (Antonio)</span>
                <span class="text-text-muted text-[11px]">Locución en portugués de Brasil.</span>
              </div>
              <div class="p-3.5 rounded-xl bg-obsidian-elevated border border-border-subtle">
                <span class="font-bold text-text-bright block mb-1">🇩🇪 Alemán (Killian)</span>
                <span class="text-text-muted text-[11px]">Locución en alemán de Alemania.</span>
              </div>
            </div>
          </div>

        </div>
      </div>

  </main>

  <footer class="bg-obsidian border-t border-border-subtle py-8 text-xs text-text-muted text-center">
    <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div>Código bajo <a href="../LICENSE.md" class="underline hover:text-white">AGPLv3</a> • Contenido © 2026 Raupulus Tales. Todos los derechos reservados.</div>
      <div class="flex gap-4">
        <a href="../index.html" class="hover:text-white">Inicio</a>
        <a href="../LICENSE.md" class="hover:text-white text-damask-light">Propiedad & Derechos</a>
        <a href="{YT_CHANNEL}" target="_blank" rel="noopener noreferrer" class="hover:text-white">YouTube</a>
        <a href="mailto:{PUBLIC_EMAIL}" class="hover:text-white">{PUBLIC_EMAIL}</a>
      </div>
    </div>
  </footer>

</body>
</html>
"""
        with open(page_file, 'w', encoding='utf-8') as pf:
            pf.write(page_html)

    print(f"✅ Generadas {len(relatos)} páginas individuales dedicadas en relatos/")


def generate_sitemap_and_robots(relatos):
    """Genera sitemap.xml y robots.txt oficiales."""
    now_date = datetime.now().strftime("%Y-%m-%d")
    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <url><loc>{SITE_URL}/</loc><lastmod>{now_date}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>'
    ]
    for r in relatos:
        sitemap_lines.append(f"  <url><loc>{SITE_URL}/{r['pagina_url']}</loc><lastmod>{now_date}</lastmod><changefreq>monthly</changefreq><priority>0.9</priority></url>")
    sitemap_lines.append('</urlset>')

    with open(os.path.join(PUBLIC_DIR, "sitemap.xml"), 'w', encoding='utf-8') as f:
        f.write("\n".join(sitemap_lines))

    robots_txt = f"""# robots.txt — Raupulus Tales (relatos.raupulus.dev)
# Permitir indexación web estándar (SEO en Google, Bing, DuckDuckGo)
User-agent: *
Allow: /

# Bloqueo estricto de bots de rastreo e ingesta para entrenamiento de IA
User-agent: GPTBot
Disallow: /

User-agent: ChatGPT-User
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: Anthropic-AI
Disallow: /

User-agent: Claude-Web
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Cohere-AI
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: Diffbot
Disallow: /

User-agent: FacebookBot
Disallow: /

User-agent: Meta-ExternalAgent
Disallow: /

User-agent: Omgilibot
Disallow: /

User-agent: Timpibot
Disallow: /

User-agent: PerplexityBot
Disallow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    with open(os.path.join(PUBLIC_DIR, "robots.txt"), 'w', encoding='utf-8') as f:
        f.write(robots_txt)
    print("✅ sitemap.xml y robots.txt generados con éxito en public/")


def compile_css():
    """Ejecuta la transpilación de Tailwind CSS v4 para que public/assets/css/tailwind.css esté listo."""
    print("🎨 Compilando Tailwind CSS...")
    try:
        dest_css = os.path.join(PUBLIC_DIR, "assets", "css", "tailwind.css")
        os.makedirs(os.path.dirname(dest_css), exist_ok=True)
        subprocess.run(["npx", "@tailwindcss/cli", "-i", "src/input.css", "-o", "public/assets/css/tailwind.css", "--minify"], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        print("✅ Tailwind CSS compilado correctamente en public/assets/css/tailwind.css.")
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
