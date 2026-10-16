# REGLAS Y ESTÁNDARES OFICIALES DEL PROYECTO: RAUPULUS TALES (relatos.raupulus.dev)

> [!IMPORTANT]
> Estas reglas son de cumplimiento estricto y permanente en todas las sesiones para el diseño y desarrollo de la web `relatos.raupulus.dev`, la integración de relatos, storyboards, locuciones, vídeos cinematográficos y publicación.

---

## 1. MISIÓN Y ALCANCE DE LA WEB

**Raupulus Tales** (`relatos.raupulus.dev`) es el portal web oficial del universo de relatos y ficción multimedia de Raupulus. Presenta historias literarias completas concebidas con visión cinematográfica, audiolibros multilingües con locución calibrada (España `es-ES`, Latinoamérica `es-LAT`, Internacional `en-US`), biblias visuales de personajes y producciones en vídeo Full HD 1080p con movimiento Ken Burns y clips de apertura.

---

## 2. PRIVACIDAD Y SEGURIDAD ESTRICTA (PERMANENTE)

* **Correo personal estrictamente prohibido:** NUNCA utilizar bajo ningún concepto ningún correo personal o privado del creador.
* **Único correo público permitido:** `public@raupulus.dev`.
* **Prohibición en archivos del proyecto:** Queda terminantemente prohibido incluir direcciones de correo privadas reales en código, comentarios, metadatos, documentación o commits.
* Jamás exponer nombres reales completos, números telefónicos, direcciones IP privadas ni credenciales.
* **Propiedad Intelectual y Derechos Restrictivos:** Todos los textos literarios, relatos, tramas, personajes, ilustraciones, locuciones, storyboards y vídeos son obra artística y propiedad privada exclusiva de Raupulus Tales (Copyright © 2026). Prohibida terminantemente su explotación comercial, copia, redistribución, alteración o uso para minería/entrenamiento de modelos de IA sin autorización expresa. Ver `LICENSE.md`.
* **Identidad de Marca:** El logotipo y favicon oficiales del proyecto provienen exclusivamente de los activos de canal de Raupulus Tales (`avatar_icono.jpg` y `marca_de_agua.png`), nunca del logotipo de la web principal o personal.

---

## 3. ARQUITECTURA TÉCNICA Y SEO (DIRECTORIO PÚBLICO Y PÁGINAS DEDICADAS)

* **Directorio autocontenido `public/` (Apache DocumentRoot):**
  * Todo archivo expuesto o requerido para internet reside **exclusivamente dentro de `public/`**, permitiendo que servidores web (Apache, Nginx) apunten directamente a él como raíz (`DocumentRoot`) sin exponer `.git`, `node_modules/`, `package.json`, código fuente o scripts.
  * El primer nivel del repositorio contiene exclusivamente configuración, código fuente (`src/`), documentación (`docs/`, `AGENTS.md`), utilidades de compilación (`scripts/`, `serve.py`) y control de versiones.
* **Estructura amigable para SEO dentro de `public/`:**
  * `public/index.html`: Portada ligera con hero cinemático, filtros reactivos en Alpine.js y tarjetas 16:9 optimizadas.
  * `public/relatos/NNNN-slug.html`: Cada relato cuenta con su propia página estática dedicada para indexación óptima en buscadores (Google / Bing), metadatos Open Graph, Twitter Cards y marcado semántico Schema.org (`ShortStory`).
  * `public/sitemap.xml` y `public/robots.txt`: Indexación controlada y bloqueo explícito de bots de rastreo de IA.
  * `public/ai.txt` y `public/LICENSE.md`: Directivas anti-scraping de IA y términos legales accesibles directamente.
* **Cero dependencias externas en tiempo de ejecución:**
  * Prohibido cargar scripts, fuentes o estilos desde CDNs externos (Google Fonts, unpkg, cdnjs, etc.).
  * **Alpine.js local:** Ubicado y servido exclusivamente desde `public/assets/js/alpine.min.js` (origen en `src/assets/js/`).
  * **Tailwind CSS pretranspilado:** Generado localmente en `public/assets/css/tailwind.css` desde `src/input.css` usando `npm run build:css`.
  * Toda la web debe desplegarse completa y funcional de forma autónoma en servidores Apache, Nginx, Cloudflare Pages o GitHub Pages.
* **Optimización de recursos e imágenes (WebP Calidad 85):**
  * **Todas las imágenes de la web residen y se sirven exclusivamente en formato `.webp` con calidad 85** (`public/assets/images/`): logotipos, favicons, marcas de agua, portadas 16:9, avatares de personajes y escenas intercaladas.
  * Código CSS minificado sin reglas superfluas.

---

## 4. SISTEMA DE DISEÑO VISUAL Y PALETA CROMÁTICA

La identidad visual toma de referencia los tonos extraídos directamente del logotipo oficial de Raupulus:

* **Colores Principales:**
  * **Crimson Red (`#941300` / `#b81d05`):** Acento dominante de fuego, intensidad y misterio. Uso en botones de acción principales, bordes de elementos activos, badges destacados y barras de progreso.
  * **Velvet Plum (`#371632` / `#220d1f`):** Atmósfera secundaria noble y literaria. Uso en fondos intermedios, gradientes de ambientación y divisores.
  * **Rose Damask (`#8f2e49` / `#ab3858`):** Matiz dramático cálido para etiquetas de género, tags y estados hover.
  * **Obsidian Void (`#080308`):** Fondo general cinematográfico de contraste absoluto.
  * **Obsidian Card (`#120813`):** Superficie de tarjetas y paneles modales.
  * **Warm Mist (`#eedfe3`):** Color editorial de lectura óptima para textos de relatos, evitando el cansancio visual del blanco puro.
  * **YouTube Brand Red (`#ff0000`):** Enlaces directos y acciones del canal de YouTube.
* **Tipografía del sistema:**
  * Sin descargas de fuentes: Pila tipográfica local y moderna (`system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`).
  * Relatos formateados con `max-w-prose`, interlineado holgado (`leading-relaxed` / `leading-loose`) y legibilidad editorial.

---

## 5. ESTRUCTURA Y COMPONENTES DEL PORTAL

1. **Header / Navbar:**
   * Logotipo oficial local con enlace a inicio.
   * Navegación limpia (Catálogo, Visor, El Universo).
   * Selector rápido de idioma (`es-ES`, `es-LAT`, `en-US`).
   * Botón de suscripción y enlace oficial al canal de YouTube.
2. **Catálogo de Relatos:**
   * Filtro reactivo con Alpine.js por géneros temáticos (Sci-Fi, Fantasía, Misterio, Drama, etc.).
   * Tarjetas con formato 16:9 para portadas de episodios (`1280x720`).
   * Badges de metadatos: ID secuencial de 4 dígitos (`0001`), tiempo de lectura silenciosa (a 220 ppm), duración del vídeo/locución (a 160 ppm) y disponibilidad multilingüe.
   * Sinopsis directa sin spoilers.
3. **Visor de Historia y Reproductor Multimedia:**
   * Contenedor de vídeo responsive 16:9 preparado para embeber vídeos de YouTube sin desajustes de maquetación.
   * Pestañas reactivas con Alpine.js:
     * **Relato Literario:** Texto maestro completo dividido por escenas (`* * *`) con tipografía editorial.
     * **Capítulos & Storyboard:** Desglose narrativo limpio de capítulos con marcas de tiempo (`MM:SS`) y resumen dramático de acontecimientos. **PROHIBIDO estricta y terminantemente incluir nombres de archivos de producción audiovisual (`video1.mp4`, `video2.mp4`, `escena-XX.png`, `.wav`) o jerga técnica de software/renderizado.**
     * **Avatares & Biblia Visual:** Fichas de consistencia de personajes (edad fija, rasgos anatómicos y láminas de avatar).
     * **Locución & Audios:** Acceso a las tres pistas de locución calibradas.
4. **Footer:**
   * Enlaces al ecosistema Raupulus (`raupulus.dev`, `music.raupulus.dev`).
   * Correo público oficial: `public@raupulus.dev`.
   * Aviso de derechos y copyright.

---

## 6. INTEGRACIÓN CON EL ORIGEN DE DATOS (HISTORIAS MULTIMEDIA)

* Los datos de la web se nutren del repositorio y estructura canónica de historias (`Historias/NNNN-slug/`):
  * **Texto maestro:** `Historias/NNNN-slug/NNNN-slug.md`.
  * **Metadatos y escenas:** `storyboard/storyboard.md`, `storyboard/escenas.md`, `storyboard/marcas_tiempo.json`.
  * **Avatares:** `avatars/personaje-XX-<slug>-cabeza.png` y `-cuerpo.png`.
  * **Portadas YouTube:** `youtube/portada-es-ES.jpg`, `portada-es-LAT.jpg`, `portada-en-US.jpg`.
  * **ID de YouTube:** Registrado en `youtube/youtube.md`.
* Los identificadores de relato siempre siguen el formato de 4 dígitos secuenciales (`0001`, `0002`...).

---

## 7. PROTOCOLO OBLIGATORIO DE INSERCIÓN Y AGRUPACIÓN DE NUEVOS RELATOS

> [!IMPORTANT]
> Cada vez que se desarrolle, sincronice o publique un nuevo relato en el universo Raupulus Tales (`Historias/NNNN-slug/`), se debe incorporar a la web siguiendo rigurosamente este patrón:

1. **Agrupación y Clasificación Obligatoria por Tipo de Relato (`categoria`):**
   * Todo relato debe clasificarse en una de las categorías estándar para asegurar el correcto funcionamiento de los filtros reactivos en Alpine.js:
     * `suspense`: Suspense, intriga y thriller psicológico.
     * `scifi`: Ciencia ficción, distopías y futuros especulativos.
     * `terror`: Terror cósmico, criaturas y horror psicológico.
     * `drama`: Drama humano, relaciones familiares y comedia negra existencial.
     * `misterio`: Enigmas del pasado, cartas secretas y objetos perdidos.
     * `historico`: Ficción histórica y sucesos de época.
     * `fantasia`: Fantasía oscura y mitología.
   * Además, se deben registrar etiquetas secundarias libres en el array `generos` para potenciar el buscador en tiempo real.

2. **Regla Inmutable de la Pestaña Storyboard / Capítulos:**
   * **PROHIBICIÓN ESTRICTA:** Queda terminantemente prohibido escribir `video1.mp4`, `video2.mp4`, `escena-XX.png`, `.wav`, tiempos en fotogramas, o referencias a archivos locales de producción. Los visitantes de la web acceden al vídeo directamente a través de YouTube.
   * La pestaña debe mostrar únicamente el listado de capítulos con su marca de tiempo (`MM:SS`), título descriptivo y un breve resumen narrativo de lo que sucede en la trama.

3. **Ilustraciones Cinematográficas Intercaladas en el Relato Literario:**
   * Al ser historias largas (1.600 a 2.400+ palabras), la lectura en la pestaña *Relato Literario* debe enriquecerse visualmente intercalando **5 imágenes clave** del storyboard (`assets/images/escenas/NNNN-*.webp`) distribuidas proporcionalmente entre los párrafos.
   * Estas ilustraciones se extraen del lote de escenas de producción (`escenas/*.png`), se optimizan en formato WebP con relación de aspecto 16:9 y se insertan con sus respectivos pies de foto narrativos elegantes (`<figure>` y `<figcaption>`), mejorando la inmersión del lector sin interrumpir el ritmo dramático.

4. **Gestión Ágil y Fuente Canónica Centralizada (`relatos.json` en la raíz):**
   * El archivo `relatos.json` situado en la raíz del repositorio web actúa como la **fuente canónica directa** para el estado, metadatos y publicaciones de todas las historias.
   * `scripts/build_site.py` detecta y carga prioritariamente este archivo raíz, evitando reprocesamientos pesados y optimizando el consumo de tokens y recursos al realizar actualizaciones frecuentes.

5. **Flujo de Estados (`estreno` vs `publicado`) y Protección de Contenido:**
   * **Próximo Estreno (`"estado": "estreno"`, `"publicado": false`):**
     * Se aplica cuando el relato o vídeo está en producción, en reserva o subido a YouTube en modo privado/oculto antes de su liberación pública.
     * **En el Catálogo de Portada (`index.html`):** La tarjeta muestra un overlay oscuro transparente (`bg-black/75`) con el distintivo `Estreno`, el indicador "Próximamente en YouTube" y el botón de acción "Ver Ficha de Estreno".
     * **En la Página Dedicada (`relatos/NNNN-slug.html`):** **PROTECCIÓN ESTRICTA CONTRA PLAGIO PREVIO.** Queda terminantemente prohibido exponer la historia completa antes de su estreno oficial. La página muestra **exclusivamente el primer párrafo** del texto literario como aperitivo narrativo, seguido de un panel protector de contenido en reserva que invita a suscribirse al canal de YouTube. La pestaña de capítulos se mantiene en reserva y las escenas intercaladas no se publican hasta el estreno.
   * **Publicación Oficial (`"estado": "publicado"`, `"publicado": true`):**
     * Al estrenar la historia y liberar el vídeo en YouTube, se actualizan los campos en `relatos.json` a `"estado": "publicado"`, `"publicado": true` y se registra el `youtube_id`.
     * Al ejecutar `npm run build`, la página dedicada se regenera automáticamente al 100%, mostrando el reproductor de YouTube, el relato íntegro con sus 5 escenas intercaladas y el desglose narrativo de capítulos.

6. **Visibilidad y Ordenación del Catálogo y Botón Principal del Hero:**
   * En el catálogo de la portada (`index.html`) y en la base de datos `relatos.json`, los relatos deben ordenarse **siempre con los últimos subidos arriba** (orden descendente por ID: `0010`, `0009`... `0001`) para dar máxima visibilidad inmediata a los nuevos estrenos y publicaciones recientes.
   * **Botón principal del Hero («Leer Último Estreno»):** Debe enlazar **exclusivamente al último relato publicado de verdad** (`publicado === true` y `estado !== 'estreno'`), jamás a un relato en reserva o próximo estreno aún no publicado.

7. **Optimización de Compartición en Redes Sociales (Open Graph y Twitter Cards):**
   * Todas las páginas disponen de etiquetas meta canónicas completas para compartir en redes sociales y apps de mensajería (WhatsApp, Telegram, X, Facebook, LinkedIn).
   * La portada (`index.html`) utiliza el banner cinemático oficial de 1200x630 en formato WebP (`assets/images/og-raupulus-tales.webp`), diseñado con la paleta de color del canal (`#080308`, `#941300`, `#371632`), el logotipo y la tipografía de marca.
   * Cada relato individual (`relatos/NNNN-slug.html`) enlaza a su portada oficial 16:9 (`1280x720`) con dimensiones explícitas, tipo `article` y descripción adaptada.

8. **Compilación y Actualización Automática de la Web:**
   * Tras finalizar un relato o cambiar su estado en `relatos.json`, ejecutar desde la raíz del proyecto web:
     ```bash
     npm run build
     # Ejecuta scripts/build_site.py y recompila Tailwind CSS en public/
     ```
   * El script actualiza `data/relatos.json`, genera las portadas, avatares y las 5 escenas WebP en `public/assets/images/`, sincroniza directivas y librerías estáticas, actualiza `public/index.html` con orden descendente, crea o actualiza las páginas independientes `public/relatos/NNNN-slug.html` con la protección correspondiente según su estado, refresca `public/sitemap.xml`, `public/robots.txt` y recompila `public/assets/css/tailwind.css`. Todo el contenido listo para servir en Apache DocumentRoot sin exponer el directorio raíz del proyecto.

---

## 8. ESTÁNDARES OBLIGATORIOS DE ACCESIBILIDAD (A11Y), W3C Y RESPONSIVE

* **Contraste de color WCAG AA/AAA:** Texto principal `#eedfe3` sobre fondos oscuros `#080308` (ratio > 11:1). Texto secundario `#a5919b` con ratio de contraste superior a 4.5:1.
* **Navegación por teclado y foco visible:** Todo elemento interactivo debe contar con indicador visible de foco (`focus-visible:ring-2 focus-visible:ring-crimson`).
* **Jerarquía semántica estricta:** `H1` único por página o vista, seguido secuencialmente por `H2` y `H3` sin saltos de nivel.
* **Textos alternativos (`alt`):** Atributos `alt` exhaustivos y descriptivos en todas las imágenes. Elementos meramente decorativos marcados con `aria-hidden="true"`.
* **Dimensiones explícitas y prevención de CLS:** Especificar siempre `width` y `height` o ratios de aspecto fijos (`aspect-video`) en elementos multimedia para evitar saltos visuales durante la carga.
* **Touch targets en móviles:** Mínimo de 44x44px en botones, controles y selectores.

---

## 9. BUENAS PRÁCTICAS DE GIT Y CONTROL DE VERSIONES

* Commits atómicos, semánticos y descriptivos en español o inglés (`feat:`, `fix:`, `style:`, `docs:`, `refactor:`).
* No commitear `node_modules/`, archivos temporales de sistema (`.DS_Store`) ni registros de compilación.
* Mantener la compilación de `assets/css/tailwind.css` actualizada y sincronizada con cualquier cambio en `src/input.css` o plantillas HTML antes de cada entrega o commit.
* **Activos de Proyecto en Plataformas Git (GitHub / GitLab):**
  * **GitHub Social Preview:** `1280x640 px` (aspect ratio 2:1), formato PNG/WebP.
  * **GitLab Project Avatar:** Exactamente **`192x192 px`**, peso estricto **menor a 200 KiB** (formato PNG optimizado). Prohibido intentar subir imágenes panorámicas o de mayor peso en el avatar de proyecto de GitLab.
