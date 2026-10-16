# Patrón de Inserción y Publicación de Nuevos Relatos (relatos.raupulus.dev)

> Este documento define el **estándar técnico y de contenidos obligatorio** para incorporar nuevos relatos a la web oficial (`relatos.raupulus.dev`), garantizando que se integren coherentemente en el catálogo, en los filtros temáticos y en el visor interactivo.

---

## 1. Agrupación y Clasificación Obligatoria por Tipo de Relato

Para que el catálogo pueda filtrarse de manera precisa y homogénea en Alpine.js, todo nuevo relato **debe clasificarse en una de las categorías estándar** del portal:

| Clave de Categoría (`categoria`) | Nombre Público (`categoria_nombre`) | Criterio y Temáticas de Agrupación |
| :--- | :--- | :--- |
| **`suspense`** | **Suspense & Thriller** | Intriga psicológica, secretos inconfesables, investigaciones oscuras, giros de guion inesperados, crímenes y conspiraciones. |
| **`scifi`** | **Ciencia Ficción** | Futuros distópicos, tecnología cuántica, inteligencia artificial, colapsos sistémicos, viajes espaciales y advertencias bioéticas. |
| **`terror`** | **Terror** | Horror psicológico, criaturas marinas o mitológicas, leyendas urbanas, atmósfera opresiva y fenómenos inexplicables. |
| **`drama`** | **Drama & Humano** | Conflictos familiares, pérdidas, reconciliaciones vitales, memoria histórica íntima y comedia negra existencial. |
| **`misterio`** | **Misterio** | Objetos perdidos, cartas anónimas, enigmas del pasado y resolución de incógnitas. |
| **`historico`** | **Histórico** | Ficción de época, posguerra, oficios clandestinos y acontecimientos situados en periodos históricos concretos. |
| **`fantasia`** | **Fantasía** | Fantasía oscura, reinos imaginarios, mitos arcanos y épica sombría. |

> [!NOTE]
> Además de la categoría principal (`categoria`), el relato puede incluir una lista de etiquetas descriptivas secundarias en el array `generos` (ej: `["Suspense", "Terror Psicológico"]`), que también son indexadas por el motor de búsqueda en tiempo real de la web.

---

## 2. Regla Crítica de la Pestaña Storyboard & Capítulos

> [!CAUTION]
> **PROHIBICIÓN ESTRICTA DE ARCHIVOS TÉCNICOS:**  
> En la pestaña de Storyboard/Capítulos del visor web **queda terminantemente prohibido incluir nombres de archivos de producción audiovisual** (como `video1.mp4`, `video2.mp4`, `001-intro.png`, `audio.wav`, etc.) ni jerga interna de renderizado (CRF, interpolaciones de fotogramas o régimen de planos).

### Formato Permitido y Exigido:
La pestaña muestra **única y exclusivamente el desglose narrativo de capítulos**:
1. **Marca de tiempo:** `MM:SS` (ej. `00:00`, `02:56`, etc.).
2. **Título del capítulo:** Nombre sugerente y dramático del bloque (ej: `Capítulo 1 — Las tres y diez de la madrugada`). Si existe clip de apertura, titular simplemente `Introducción` o `Apertura`.
3. **Resumen narrativo:** 1 o 2 frases explicando qué ocurre dramáticamente en ese fragmento, redactado para el oyente o espectador (ej: *«Yolanda inicia su primera guardia nocturna y descubre la silueta que vigila el portal enfrente bajo la nevada.»*).

---

## 3. Estructura de Datos Canónica en `data/relatos.json`

Cada relato registrado en `data/relatos.json` debe cumplir este esquema JSON:

```json
{
  "id": "0001",
  "slug": "la-que-no-tuvo-hijos",
  "url_hash": "#0001-la-que-no-tuvo-hijos",
  "pagina_url": "relatos/0001-la-que-no-tuvo-hijos.html",
  "titulo": "La que no tuvo hijos",
  "sinopsis": "Yolanda acepta un trabajo de cuidadora nocturna en una casa del casco antiguo de Cuenca...",
  "categoria": "suspense",
  "categoria_nombre": "Suspense",
  "generos": ["Suspense", "Terror Psicológico"],
  "palabras": 3261,
  "lectura_min": 15,
  "duracion_audio": "23:12",
  "duracion_segundos": 1392,
  "youtube_id": "xFOrshoYaJc",
  "youtube_url": "https://www.youtube.com/watch?v=xFOrshoYaJc",
  "portada": "assets/images/portadas/0001-la-que-no-tuvo-hijos.webp",
  "personajes": [
    {
      "id": "0001-p1",
      "nombre": "Yolanda Tébar",
      "rol": "protagonista",
      "rasgos": "cuarenta y un años, cuidadora. Práctica y desconfiada...",
      "motivacion": "cobrar tres meses seguidos y saldar sus deudas.",
      "conflicto": "lo que descubre en la casa no la deja dormir.",
      "avatar_cabeza": null,
      "avatar_cuerpo": null
    }
  ],
  "capitulos": [
    {
      "tiempo": "00:00",
      "segundos": 0,
      "titulo": "Introducción — La que no tuvo hijos",
      "resumen": "Apertura en la noche de Cuenca; la llegada al portal bajo la niebla y el silencio gélido de la judería."
    },
    {
      "tiempo": "00:20",
      "segundos": 20,
      "titulo": "Capítulo 1 — Las tres y diez de la madrugada",
      "resumen": "La primera noche de guardia de Yolanda, el despertar de Amparo y la misteriosa figura frente a la puerta."
    }
  ],
  "relato_raw": "Texto literario íntegro en Markdown...",
  "relato_html": "<p>Texto formateado en párrafos HTML...</p>",
  "locucion": {
    "es_ES": {"voz": "Álvaro (es-ES-AlvaroNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Voz máster y vídeo"},
    "es_LAT": {"voz": "Alonso (es-US-AlonsoNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Voz neutra latinoamericana"},
    "en_US": {"voz": "Christopher (en-US-ChristopherNeural)", "calidad": "192 kbps, 48 kHz", "rol": "Narración internacional en inglés"}
  }
}
```

---

## 4. Flujo de Trabajo y Automatización de Nuevos Relatos

Al finalizar un nuevo relato en el repositorio canónico de Historias (`Historias/NNNN-slug/`):

1. **Verificar que existan los archivos canónicos:**
   - Relato maestro: `Historias/NNNN-slug/NNNN-slug.md` (con YAML frontmatter `genero: [...]`, `## Descripción`, `## Personajes` y `## Relato`).
   - Portada oficial: `Historias/NNNN-slug/youtube/portada.jpg` (o `portada-es-ES.jpg`, 1280x720 16:9).
   - Metadatos YouTube: `Historias/NNNN-slug/youtube/youtube.md` (con el Vídeo ID si ya está publicado).
   - Marcas y capítulos: `Historias/NNNN-slug/storyboard/marcas_tiempo.json`.
   - Avatares (opcional si están generados): `Historias/NNNN-slug/avatars/*.png`.

2. **Ejecutar la compilación sincronizada:**
   Desde la raíz de `www.relatos.raupulus.dev`, ejecutar:
   ```bash
   npm run build
   # Equivale a: python3 scripts/build_site.py
   ```
   Este comando realiza automáticamente:
   - Extracción de metadatos y conversión de portadas y avatares a WebP optimizado en `assets/images/`.
   - Actualización de `data/relatos.json`.
   - Regeneración de `index.html` con todos los relatos y filtros activos.
   - Creación de la página independiente en `relatos/NNNN-slug.html`.
   - Actualización de `sitemap.xml` y `robots.txt`.
   - Transpilación de `assets/css/tailwind.css`.

3. **Verificación visual:**
   - Comprobar que el relato aparece en la categoría correspondiente y responde al filtro.
   - Comprobar que el visor interactivo abre el relato, reproduce el vídeo si tiene ID y muestra las pestañas limpias de capítulos y personajes.
   - Realizar commit semántico en git: `feat: incorporar relato NNNN-slug al catálogo y compilar web`.
