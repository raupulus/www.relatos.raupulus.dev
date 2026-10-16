# Auditoría Integral — www.relatos.raupulus.dev (2026-10-16)

## Resumen Ejecutivo de Incidencias

| Severidad | Cantidad | Descripción |
| :--- | :---: | :--- |
| 🔴 **Crítico** | 3 | Bloqueantes de privacidad y seguridad (nombre real en historial Git, correo privado y ruta local en script) y ausencia de remotos Git configurados. |
| 🟠 **Importante** | 9 | Incidencias de accesibilidad WCAG 2.1 AA (contraste insuficiente, áreas táctiles < 44px, falta de patrón ARIA en pestañas), SEO (meta descriptions truncadas, crawlabilidad sin JS) y responsive en móvil (320px). |
| 🟡 **Menor** | 4 | Pulido de UI/UX (`[x-cloak]` ausente, avatares no enlazados en relatos 0001/0002, prioridad de carga LCP e higiene de `.gitignore`). |

---

## 🔴 Problemas Críticos (Atención Inmediata)

### [C-01] Seguridad y Privacidad — Ruta absoluta local y correo personal expuestos en script del repositorio
- **Dónde:** [`scripts/build_site.py:28`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/scripts/build_site.py#L28)
- **Evidencia:**
  ```python
  HISTORIAS_SRC_DEFAULT = "/Users/fryntiz/Library/CloudStorage/GoogleDrive-..."
  ```
  *(Contiene tanto el nombre de usuario del sistema operativo local como la dirección de correo personal privada en el nombre de la carpeta de Google Drive).*
- **Impacto:** Incumplimiento directo de la regla de privacidad estricta. Al publicar el repositorio en GitLab/GitHub bajo licencia AGPLv3, cualquier persona o bot podrá extraer el correo privado y la estructura de directorios local del autor.
- **Fix propuesto:** Eliminar la ruta absoluta hardcodeada y resolverla mediante variable de entorno (`RELATOS_SRC_DIR`) o ruta relativa fuera del repositorio sin exponer usuarios ni correos, manteniendo como fallback seguro `data/relatos.json`:
  ```python
  HISTORIAS_SRC_DEFAULT = os.environ.get("RELATOS_SRC_DIR", "")
  ```

### [C-02] Seguridad y Privacidad — Nombre real completo expuesto en la autoría de los commits de Git y aparición de correo privado en el historial
- **Dónde:** Historial de Git (`.git/logs/` y los 9 commits de la rama `main`, desde `44fb1fc` hasta `c96e8c9`)
- **Evidencia:**
  - `git log --format="%h %an <%ae>"` devuelve el nombre real completo del autor junto a `<public@raupulus.dev>` en todos los commits.
  - `git log -S "gmail.com"` detecta el commit inicial donde se introdujo la ruta de `scripts/build_site.py` con el correo privado.
- **Impacto:** Aunque se corrija el archivo en un nuevo commit, el nombre real completo en los metadatos de autoría de Git y el correo privado en el diff del commit `44fb1fc` quedarían accesibles públicamente en el historial de GitLab/GitHub.
- **Fix propuesto:** Configurar `git config user.name "raupulus"` y `git config user.email "public@raupulus.dev"` en el repositorio local y reescribir/aplanar el historial antes del primer `push` remoto (o reinicializar el historial limpio una vez aplicadas las correcciones de esta auditoría):
  ```bash
  git config user.name "raupulus"
  git config user.email "public@raupulus.dev"
  # Tras aplicar correcciones, recrear historial limpio sin rastros en reflog:
  git checkout --orphan temp_main
  git add -A
  git commit -m "feat: initial release of Raupulus Tales web portal (relatos.raupulus.dev)"
  git branch -D main
  git branch -m main
  ```

### [C-03] DevOps / Git — Remoto `origin` (GitLab principal + GitHub mirror) no configurado
- **Dónde:** Configuración Git del repositorio (`.git/config`)
- **Evidencia:** `git remote -v` devuelve salida vacía (sin remotos configurados).
- **Impacto:** El proyecto no está vinculado a los repositorios remotos oficiales para su despliegue y respaldo dual.
- **Fix propuesto:** Configurar el remoto `origin` apuntando a GitLab como principal y añadir ambos destinos de `push` (GitLab + GitHub mirror):
  ```bash
  git remote add origin https://gitlab.com/raupulus/www.relatos.raupulus.dev.git
  git remote set-url --add --push origin https://gitlab.com/raupulus/www.relatos.raupulus.dev.git
  git remote set-url --add --push origin https://github.com/raupulus/www.relatos.raupulus.dev.git
  ```

---

## 🟠 Problemas Importantes

### [I-01] Accesibilidad (WCAG 1.4.3 Contraste Mínimo) — Textos en color `damask`, `damask-light`, `crimson` y botones `yt-red` por debajo del ratio 4.5:1
- **Dónde:** [`src/input.css:4-20`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/src/input.css#L4-L20), [`public/index.html`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/index.html) y [`public/relatos/*.html`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/relatos/0001-la-que-no-tuvo-hijos.html)
- **Evidencia (medición exacta de luminancia relativa):**
  - `text-damask` (`#8f2e49`) sobre `bg-obsidian` (`#080308`): **2.59:1** (usado en subtítulos de sección `text-xs` en `index.html:152, 242` y etiquetas `Escena Oficial` en `0001-la-que-no-tuvo-hijos.html:153`).
  - `text-damask-light` (`#ab3858`) sobre `bg-obsidian-card` (`#120813`): **3.21:1** (usado en `ES • LAT • EN` en `index.html:206`, enlaces `Ver instante en YouTube ↗` en `0001-la-que-no-tuvo-hijos.html:320` y enlace `Propiedad & Derechos` en el footer).
  - `text-crimson` (`#941300`) sobre `bg-obsidian` (`#080308`): **2.29:1** (usado en las marcas de tiempo `00:00` en `0001-la-que-no-tuvo-hijos.html:314`).
  - `text-crimson-glow` (`#b81d05`) sobre `bg-obsidian-card` (`#120813`): **3.01:1** (usado en el enlace `Leer Relato Dedicado` en `index.html:216`).
  - Texto blanco (`#ffffff`) sobre `bg-yt-red` (`#ff0000`) en texto pequeño (`text-xs`): **4.00:1** (requiere 4.5:1 para texto menor de 18pt/14pt bold).
- **Impacto:** Incumple el criterio WCAG 2.1 AA 1.4.3 (mínimo 4.5:1 para texto normal) y la sección 8 de `AGENTS.md`, dificultando la lectura en pantallas con brillo bajo o usuarios con baja visión.
- **Fix propuesto:**
  - En `src/input.css`, ajustar `--color-damask-light` a un tono más luminoso para textos (ej. `#e06c88`, ratio **6.18:1** sobre `#080308` y **5.93:1** sobre `#120813`) y añadir un token de texto acentuado legible `--color-crimson-text: #ff6b52` (ratio **6.55:1**), manteniendo `#941300` y `#8f2e49` para fondos y bordes.
  - Para botones de YouTube con texto blanco `text-xs`, usar fondo `#cc0000` (ratio **5.89:1** con `#ffffff`).

### [I-02] Accesibilidad (WCAG 2.4.7 Foco Visible) — Elementos interactivos sin indicador de foco visible por teclado
- **Dónde:** [`public/index.html:83-107, 135-141, 170-176, 185, 209, 216`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/index.html#L83-L107) y [`public/relatos/*.html:65, 73-74, 84-86, 113-116`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/relatos/0001-la-que-no-tuvo-hijos.html#L65-L116)
- **Evidencia:** Solo el logotipo de `index.html:71` tiene `focus-visible:ring-2 focus-visible:ring-crimson`. Los botones de filtro de categoría, enlaces de tarjetas, pestañas de relato/capítulos/personajes/locución y enlaces de navegación carecen de clases `focus-visible:ring-2`.
- **Impacto:** Usuarios que navegan con teclado (`Tab`) no ven claramente qué control o pestaña tiene el foco activo, incumpliendo WCAG 2.4.7 y la sección 8 de `AGENTS.md`.
- **Fix propuesto:** Añadir una regla global en `src/input.css` para todos los elementos interactivos:
  ```css
  a:focus-visible, button:focus-visible, input:focus-visible, iframe:focus-visible {
    outline: 2px solid var(--color-crimson-glow, #b81d05);
    outline-offset: 2px;
  }
  ```

### [I-03] Accesibilidad (WCAG 2.5.5 / Mobile Responsive) — Controles táctiles inferiores al mínimo de 44×44 px
- **Dónde:**
  - Botones de filtro en [`public/index.html:170-176`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/index.html#L170-L176): `px-3.5 py-1.5 text-xs` (~28px de alto).
  - Buscador en [`public/index.html:161`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/index.html#L161): `py-2 text-xs` (~34px de alto).
  - Enlaces del menú móvil en [`public/index.html:102-106`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/index.html#L102-L106): `block text-sm` sin padding vertical (~20px de alto).
  - Botón hamburguesa en [`public/index.html:96`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/index.html#L96): `p-2` con icono `w-6 h-6` (40×40px).
  - Pestañas en [`public/relatos/*.html:113-116`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/relatos/0001-la-que-no-tuvo-hijos.html#L113-L116): `px-5 py-3 text-xs` (~40px de alto).
- **Impacto:** Dificulta la pulsación precisa en pantallas táctiles móviles e incumple el estándar de `min-h-[44px]` definido en `AGENTS.md` (sección 8).
- **Fix propuesto:** Añadir `min-h-[44px] inline-flex items-center` en botones de filtro, pestañas, input de búsqueda y enlaces del menú móvil (`min-h-[44px] min-w-[44px]` en el botón de menú móvil).

### [I-04] Accesibilidad (WCAG 4.1.2 Nombre, Rol, Valor) — Pestañas y menú móvil sin atributos ARIA de estado ni enlace "Saltar al contenido" (WCAG 2.4.1)
- **Dónde:**
  - Menú móvil en [`public/index.html:96-107`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/index.html#L96-L107)
  - Sistema de pestañas en [`public/relatos/*.html:112-117, 121, 306, 410, 462`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/relatos/0001-la-que-no-tuvo-hijos.html#L112-L121)
  - Inicio de `<body>` en todas las páginas y ausencia de `id="main-content"` en `<main>` de `public/relatos/*.html:79`.
- **Evidencia:**
  - El botón del menú móvil no tiene `:aria-expanded="menuAbierto.toString()"` ni `aria-controls="mobile-menu"`.
  - El contenedor de pestañas carece de `role="tablist"`, los botones no tienen `role="tab"` ni `:aria-selected="(vistaPestana === '...').toString()"`, y los paneles no tienen `role="tabpanel"`.
  - No existe enlace `sr-only focus:not-sr-only` al inicio del `<body>` para saltar bloques de navegación.
- **Impacto:** Los lectores de pantalla (VoiceOver, NVDA) no anuncian qué pestaña está activa ni si el menú móvil está desplegado o cerrado.
- **Fix propuesto:** Añadir skip-link al principio de `<body>`, `id="main-content"` al `<main>` de las páginas de relatos, `:aria-expanded="menuAbierto"` al botón móvil y roles `tablist` / `tab` / `tabpanel` con `:aria-selected` en las pestañas.

### [I-05] SEO On-Page y Rastreabilidad — Catálogo de `index.html` renderizado exclusivamente por cliente (`<template x-for>`) sin enlaces estáticos en el HTML inicial
- **Dónde:** [`public/index.html:181-227`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/index.html#L181-L227) y [`public/index.html:135`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/index.html#L135)
- **Evidencia:**
  - Las 10 tarjetas del catálogo están dentro de `<template x-for="r in relatosFiltrados">`. En el documento HTML inicial los elementos dentro de `<template>` están inertes en el DOM hasta que se ejecuta JS.
  - Además, el botón principal del Hero `<a :href="relatos[0]?.pagina_url">` (`index.html:135`) no tiene atributo `href` estático de respaldo antes de que Alpine.js hidrate la página.
- **Impacto:** Rastreadores de búsqueda que no ejecutan JavaScript en primera pasada (Bingbot básico, DuckDuckBot, validadores de enlaces y lectores RSS/curadores) no encuentran ningún enlace `<a href="relatos/...">` en la portada `index.html`.
- **Fix propuesto:**
  1. En el botón Hero (`index.html:135`), incluir el `href` y texto estático del último relato directamente desde Python (`href="{relatos[0]['pagina_url']}"`).
  2. Inyectar en el Schema.org `CollectionPage` (`index.html:41-54`) la lista `hasPart` con las URLs y nombres de los 10 relatos, y añadir un bloque `<noscript>` limpio con el listado de enlaces HTML estáticos a cada relato para garantizar un 100% de rastreabilidad sin depender de JS.

### [I-06] SEO On-Page — `<meta name="description">` excesivamente largas (385 a 708 caracteres) y `<title>` que superan los 60 caracteres
- **Dónde:** [`scripts/build_site.py:926-927`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/scripts/build_site.py#L926-L927) y las 10 páginas en [`public/relatos/*.html:6-7`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/relatos/0001-la-que-no-tuvo-hijos.html#L6-L7)
- **Evidencia:**
  - En los 10 relatos se inyecta la sinopsis completa en `<meta name="description">`, resultando en longitudes de entre **385 y 708 caracteres** (ej. relato `0009`: 708 caracteres; relato `0010`: 596 caracteres). Google trunca las descripciones a partir de ~155-160 caracteres.
  - 5 de los 10 `<title>` superan los 60 caracteres recomendados (ej. `0010`: 75 caracteres: `La conspiración autocumplida de la pandemia — Relato #0010 | Raupulus Tales`).
  - Faltan las etiquetas `<meta property="og:locale" content="es_ES">`, `<meta property="og:image:width" content="1280">`, `<meta property="og:image:height" content="720">` y `<meta property="og:image:alt">` en las páginas de relatos.
- **Impacto:** Los buscadores cortan las frases a mitad en las SERPs, reduciendo el CTR orgánico.
- **Fix propuesto:**
  - Crear una función auxiliar `truncate_meta_desc(text, max_len=158)` en `scripts/build_site.py` que corte limpiamente en la última palabra o punto antes de 155 caracteres añadiendo `…` para `<meta name="description">` y `twitter:description` (manteniendo la sinopsis íntegra dentro del cuerpo de la página).
  - Simplificar el formato de `<title>` a `{r['titulo']} | Raupulus Tales` (dejando el `#0010` solo si el título total no supera los 60 caracteres).
  - Añadir `og:locale`, `og:image:width`, `og:image:height` y `og:image:alt`.

### [I-07] Diseño Responsive / Mobile (XS 320px - SM 375px) — Desbordamiento y colisión en la barra de navegación "Anterior / Índice / Siguiente" de cada relato
- **Dónde:** [`public/relatos/*.html:83-87`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/relatos/0001-la-que-no-tuvo-hijos.html#L83-L87) (generado en [`scripts/build_site.py:986-990`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/scripts/build_site.py#L986-L990))
- **Evidencia:**
  ```html
  <nav class="flex items-center justify-between text-xs text-text-muted mb-6 pb-3 border-b border-border-subtle">
    <a href="0002-servicio-de-atencion-al-difunto.html" class="...">← Anterior: Servicio de atención al difunto</a>
    <a href="../index.html#catalogo" class="...">Índice</a>
    <a href="0010-la-conspiracion-autocumplida-de-la-pandemia.html" class="...">Siguiente: La conspiración autocumplida de la pandemia →</a>
  </nav>
  ```
- **Impacto:** En pantallas móviles (`320px` y `375px`), los tres elementos en una sola fila `flex` sin `flex-wrap` ni truncado chocan entre sí, aplastando el enlace central `Índice` y generando líneas de 3-4 renglones pegadas unas a otras.
- **Fix propuesto:** Apilar o distribuir en grid en móvil y truncar títulos largos:
  ```html
  <nav class="grid grid-cols-2 sm:flex sm:items-center sm:justify-between gap-2 text-xs text-text-muted mb-6 pb-3 border-b border-border-subtle" aria-label="Navegación entre relatos">
    <a href="..." class="hover:text-white transition truncate pr-2">← <span class="hidden sm:inline">Anterior: </span>{prev_r['titulo']}</a>
    <a href="../index.html#catalogo" class="hidden sm:inline-block hover:text-white transition font-medium shrink-0">Índice</a>
    <a href="..." class="hover:text-white transition truncate pl-2 text-right"><span class="hidden sm:inline">Siguiente: </span>{next_r['titulo']} →</a>
  </nav>
  ```

### [I-08] Diseño Responsive / Mobile (XS 320px) — Cabecera de metadatos del relato sin `flex-wrap` y enlaces de ancla tapados por el header fijo
- **Dónde:**
  - Cabecera de relato en [`public/relatos/*.html:91-95`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/relatos/0001-la-que-no-tuvo-hijos.html#L91-L95)
  - Secciones `#catalogo` y `#universo` en [`public/index.html:147, 239`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/index.html#L147)
- **Evidencia:**
  - `<div class="flex items-center gap-2 mb-2">` contiene el badge de ID, el badge de categoría (ej. `Ciencia Ficción`) y el texto `• 2210 palabras • 14:32 min narración` sin `flex-wrap`, desbordando en un viewport de `320px`.
  - Al pulsar en `#catalogo` o `#universo`, el `<header class="sticky top-0 z-50 ... h-16">` queda superpuesto sobre los primeros 64px de la sección porque las secciones carecen de `scroll-mt-16`.
- **Impacto:** En móviles pequeños (`320px`) el texto de metadatos se comprime o desborda horizontalmente, y al navegar por el menú los títulos quedan parcialmente ocultos bajo el navbar.
- **Fix propuesto:** Añadir `flex-wrap` al contenedor de badges en `scripts/build_site.py:994` y añadir `scroll-mt-16` a `<section id="catalogo">` y `<section id="universo">`.

### [I-09] Rendimiento (LCP y Optimización de Imágenes) — Logotipo sobredimensionado (`1024×1024`, 144 KB) para un contenedor de `40×40` px y falta de `fetchpriority="high"` en LCP
- **Dónde:**
  - [`public/assets/images/logo.webp`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/assets/images/logo.webp) y [`src/assets/images/logo.webp`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/src/assets/images/logo.webp)
  - Portada LCP en [`public/relatos/0010-la-conspiracion-autocumplida-de-la-pandemia.html:103`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/relatos/0010-la-conspiracion-autocumplida-de-la-pandemia.html#L103) y primera tarjeta de [`public/index.html:186`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/index.html#L186)
- **Evidencia:**
  - `logo.webp` se muestra únicamente a `40×40` px en el header y `32×32` px en el footer, pero el archivo servido tiene resolución `1024×1024` px y pesa **144 KB** (casi 4 veces más que todo el CSS y JS juntos).
  - En `index.html:186`, todas las portadas tienen `loading="lazy"`, incluidas las primeras 3 tarjetas visibles above-the-fold.
  - En los relatos sin vídeo publicado aún (como `0010`), la imagen hero principal no incluye `fetchpriority="high"`.
- **Fix propuesto:**
  - Redimensionar `logo.webp` para el icono de UI (ej. `160×160` px en WebP calidad 85, que pesará ~6 KB en lugar de 144 KB) o mantener una versión `logo-sm.webp` para el navbar/footer y `logo.webp` para Open Graph.
  - En `index.html:186`, aplicar `:loading="index < 3 ? 'eager' : 'lazy'"` y `:fetchpriority="index === 0 ? 'high' : 'auto'"` usando `<template x-for="(r, index) in relatosFiltrados" :key="r.id">`.
  - Añadir `fetchpriority="high"` a la imagen de portada principal en páginas de relato cuando no hay iframe.

---

## 🟡 Problemas Menores y Pulido

### [M-01] UI / CSS — Falta la regla `[x-cloak] { display: none !important; }` en la hoja de estilos
- **Dónde:** [`src/input.css`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/src/input.css) y su uso en [`public/index.html:102, 231`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/index.html#L102)
- **Evidencia:** `index.html` utiliza el atributo `x-cloak` en el menú móvil desplegable y en el mensaje de "No se encontraron relatos", pero `src/input.css` no define la regla `[x-cloak]`.
- **Impacto:** Durante la carga inicial antes de que Alpine.js se inicialice, se produce un parpadeo visual (FOUC) donde el menú móvil y el aviso de "sin resultados" aparecen brevemente en pantalla.
- **Fix propuesto:** Añadir en `src/input.css`:
  ```css
  [x-cloak] {
    display: none !important;
  }
  ```

### [M-02] Consistencia de Contenido / UI — Faltan las imágenes de avatares en la pestaña "Personajes" de los relatos `0001` y `0002`, y el relato `0010` solo intercala 2 escenas en vez de 5
- **Dónde:** [`data/relatos.json`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/data/relatos.json), [`public/relatos/0001-la-que-no-tuvo-hijos.html:412-458`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/relatos/0001-la-que-no-tuvo-hijos.html#L412-L458) y [`public/relatos/0002-servicio-de-atencion-al-difunto.html`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/public/relatos/0002-servicio-de-atencion-al-difunto.html)
- **Evidencia:**
  - En los relatos `0003` al `0010` todos los personajes muestran sus 2 láminas de avatar (`avatar_cabeza` y `avatar_cuerpo`), pero en `0001` y `0002` aparecen en `null`.
  - En el relato `0010` solo se han intercalado 2 escenas (`0010-004` y `0010-005`) frente a las 5 escenas exigidas por la regla 7.3 de `AGENTS.md`.
- **Fix propuesto:** Revisar los nombres de archivos de avatares/escenas en las carpetas origen de `0001`, `0002` y `0010` o ajustar el emparejamiento en `scripts/build_site.py:310-390` para que detecte todos los avatares y las 5 escenas cuando estén disponibles.

### [M-03] Consistencia de Dimensiones de Imágenes — Los avatares del relato `0005` están a `1376×768` en lugar de `1280×720`
- **Dónde:** `public/assets/images/avatars/0005-*.webp` y [`scripts/build_site.py:368-370`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/scripts/build_site.py#L368-L370)
- **Evidencia:** Las 6 imágenes de `0005-personaje-*` tienen dimensiones `1376×768`, mientras que el HTML declara `width="1280" height="720"`.
- **Fix propuesto:** Redimensionar automáticamente a `1280×720` (`im.resize((1280, 720), Image.Resampling.LANCZOS)`) en `scripts/build_site.py` al convertir portadas, avatares y escenas a WebP calidad 85 si superan `1280×720`.

### [M-04] Higiene del Repositorio — `.gitignore` incompleto según estándares DevOps
- **Dónde:** [`.gitignore`](file:///Users/fryntiz/git/3-Raupulus/www.relatos.raupulus.dev/.gitignore)
- **Evidencia:** Actualmente solo contiene 3 líneas (`node_modules/`, `.DS_Store`, `*.log`).
- **Fix propuesto:** Ampliar `.gitignore` para cubrir archivos de sistema, cachés de Python (`__pycache__/`, `*.pyc`), variables de entorno (`.env`, `.env.*`, `!.env.example`) y carpetas de editores (`.idea/`, `.vscode/`).

---

## 📋 Plan de Acción Priorizado (Impacto vs. Esfuerzo)

| Orden | ID | Acción concreta | Archivo(s) | Impacto | Esfuerzo (S/M/L) |
| :---: | :---: | :--- | :--- | :---: | :---: |
| **1** | **C-01** | Eliminar ruta local y correo privado de `HISTORIAS_SRC_DEFAULT` usando variable de entorno o fallback `data/relatos.json` | `scripts/build_site.py` | Crítico | S |
| **2** | **M-04** | Actualizar `.gitignore` con reglas completas de seguridad, sistema, Python, `.env` e IDEs | `.gitignore` | Alto | S |
| **3** | **I-01 / I-02 / M-01** | Ajustar colores de texto para cumplir ratio > 4.5:1 WCAG AA, añadir `:focus-visible` global y regla `[x-cloak]` | `src/input.css`, `scripts/build_site.py` | Alto | S |
| **4** | **I-03 / I-04** | Añadir skip-link, atributos ARIA (`tablist`, `tab`, `tabpanel`, `aria-expanded`) y `min-h-[44px]` en controles táctiles | `scripts/build_site.py` | Alto | M |
| **5** | **I-05 / I-06** | Truncar `<meta name="description">` a ≤158 chars, ajustar `<title>`, añadir `href` estático al CTA Hero y bloque `<noscript>` + `hasPart` en Schema.org | `scripts/build_site.py` | Alto | M |
| **6** | **I-07 / I-08** | Corregir layout responsive del navegador Anterior/Siguiente en 320px, añadir `flex-wrap` a metadatos y `scroll-mt-16` a secciones | `scripts/build_site.py` | Medio | S |
| **7** | **I-09 / M-03** | Optimizar tamaño de `logo.webp` para el navbar, normalizar dimensiones a `1280×720` y añadir `fetchpriority="high"` en LCP | `scripts/build_site.py`, `src/assets/images/` | Medio | S |
| **8** | **M-02** | Verificar y vincular avatares de relatos `0001`/`0002` y escenas de `0010` si existen en origen | `scripts/build_site.py` | Bajo | S |
| **9** | **C-02 / C-03** | Configurar `user.name` (`raupulus`), recrear historial Git limpio sin datos personales y configurar remotos `origin` (GitLab + GitHub mirror) | `.git/config` | Crítico | S |
