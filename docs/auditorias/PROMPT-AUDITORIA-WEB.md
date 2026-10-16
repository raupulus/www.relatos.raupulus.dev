# Prompt Unificado de Auditoría Web Integral (UI, Responsive, SEO, A11Y, Rendimiento, Seguridad y Git)

## Uso

- **Cuándo:** Quieres realizar una auditoría técnica y visual exhaustiva de un proyecto web (en local o producción) de una sola pasada, obteniendo un informe limpio en `docs/auditorias/` centrado **exclusivamente en los problemas que requieren atención** (sin relleno ni listas de lo que ya está bien).
- **Placeholders opcionales (si no se indican, el agente los inferirá del código y `AGENTS.md`/`README.md`):**
  - `[OBJETIVO_DE_LA_WEB]` — Propósito principal del sitio (ej. catálogo multimedia, e-commerce, portfolio, SaaS, blog…).
  - `[TONO_Y_AUDIENCIA]` — Estilo visual y público objetivo (ej. editorial oscuro, corporativo, minimalista, técnico…).
  - `[STACK_TECNOLÓGICO]` — Tecnologías empleadas (ej. HTML5, Tailwind CSS, Alpine.js, Laravel, Astro, React…).
  - `[NOMBRE_REPOSITORIO]` — Nombre del repositorio para configurar/validar los remotos en GitLab y GitHub (si no se especifica, usar el nombre del directorio raíz).

---

## 📋 PROMPT PARA COPIAR Y PEGAR

```markdown
Actúa como un equipo senior multidisciplinar compuesto por: **Diseñador de Producto (UI/UX), Frontend Engineer (Responsive), Especialista en SEO Técnico, Auditor de Accesibilidad (WCAG 2.1 AA), Ingeniero de Rendimiento (Performance) y Auditor DevOps/Seguridad**.

Tu objetivo es auditar a fondo este proyecto web y generar un informe ejecutivo en el directorio `docs/auditorias/` (ej. `docs/auditorias/AUDITORIA-YYYY-MM-DD.md`) que contenga **ÚNICA Y EXCLUSIVAMENTE los problemas reales detectados que requieren atención y acción**.

### Parámetros del proyecto (inferir del repositorio si no se especifican):
- **Objetivo del sitio:** [OBJETIVO_DE_LA_WEB]
- **Tono y audiencia:** [TONO_Y_AUDIENCIA]
- **Stack tecnológico:** [STACK_TECNOLÓGICO]
- **Nombre del repositorio:** [NOMBRE_REPOSITORIO]

---

### REGLA DE ORO DEL INFORME (CERO RELLENO)
1. **Solo problemas accionables:** PROHIBIDO incluir listas de comprobaciones superadas ("✅ Lo que está bien"), teoría genérica o elogios. Si una dimensión o breakpoint no tiene fallos, omítela o indica en una sola línea: *"Sin incidencias detectadas"*.
2. **Evidencia estricta:** Cada problema reportado DEBE citar el archivo exacto, línea de código, selector CSS/HTML o medición concreta donde ocurre. No inventes ni supongas problemas sin verificarlos en el código.
3. **Solución directa (Fix):** Cada problema debe incluir la propuesta técnica exacta para resolverlo (clases del framework CSS, código HTML/JS, comando o ajuste de configuración).

---

### DIMENSIONES A AUDITAR

#### 1. Seguridad, Privacidad e Higiene del Repositorio (Prioridad Crítica)
- **Privacidad y datos personales:**
  - Identidad pública permitida: Usuario `@raupulus`, Web `https://raupulus.dev`, Email `public@raupulus.dev`.
  - Detecta y alerta inmediatamente sobre cualquier otro email personal/privado, nombre real completo, teléfono o dato sensible en código, metadatos, commits o documentación.
- **Secretos y rutas locales:**
  - Escanea en busca de API keys, tokens, credenciales hardcodeadas, certificados (`.pem`, `.key`) o archivos `.env` rastreados.
  - Detecta rutas absolutas del sistema operativo local infiltradas en archivos públicos o scripts (ej. `/Users/...`, `/home/...`, `C:\Users\...`).
- **Exposición del servidor (DocumentRoot) y `.gitignore`:**
  - Verifica que la raíz pública web (ej. `public/` o `dist/`) esté aislada y no exponga `.git`, `node_modules/`, `src/`, `package.json` ni scripts internos.
  - Verifica que `.gitignore` excluya archivos de sistema (`.DS_Store`, `Thumbs.db`), IDEs (`.idea/`, `.vscode/`), dependencias (`node_modules/`, `vendor/`), cachés y logs.
  - Revisa `git status` para alertar de archivos residuales o sin seguimiento (untracked) que no deban subirse.
- **Estado de Remotos Git (GitLab + GitHub Mirror):**
  - Comprueba con `git remote -v` si el remoto `origin` está configurado con GitLab como principal (`fetch` y `push`) y GitHub como mirror adicional de `push`:
    - `https://gitlab.com/raupulus/<NOMBRE_REPOSITORIO>.git`
    - `https://github.com/raupulus/<NOMBRE_REPOSITORIO>.git`
  - *(Nota: Si falta configurar o hacer push, documéntalo en el informe con los comandos exactos, pero **NUNCA ejecutes `git push` automáticamente sin confirmación explícita**).*

#### 2. SEO Técnico, On-Page y Datos Estructurados
- **Indexación y metadatos:** Presencia y longitud óptima de `<title>` (30-60 chars), `<meta name="description">` (110-160 chars), `<link rel="canonical">`, `<meta name="robots">`, atributo `lang` en `<html>`, y `hreflang` simétrico (si es multi-idioma).
- **Archivos de control:** Existencia y validez de `robots.txt`, `sitemap.xml` y directivas de protección (`ai.txt` si aplica).
- **Social Meta:** Integridad de Open Graph (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`) y Twitter Cards (`summary_large_image`).
- **Schema.org (JSON-LD):** Presencia, validez sintáctica y coherencia con el contenido visible.
- **Estructura semántica y enlaces:** Único `<h1>` por vista, jerarquía lógica sin saltos (`h1 -> h2 -> h3`), URLs limpias en kebab-case, enlaces internos con anchor descriptivo y enlaces externos con `rel="noopener noreferrer"`.

#### 3. Accesibilidad (WCAG 2.1 Nivel AA)
- **Perceptible:**
  - `1.1.1`: Imágenes informativas con `alt` descriptivo; decorativas con `alt=""` o `aria-hidden="true"`.
  - `1.3.1`: Landmarks semánticos (`<header>`, `<nav>`, `<main>`, `<footer>`, `<article>`).
  - `1.4.3 / 1.4.11`: Contraste de texto mínimo 4.5:1 (3:1 en texto grande y elementos de UI/bordes interactivos).
- **Operable:**
  - `2.1.1 / 2.1.2`: Todo control interactivo operable por teclado (`<button>`, `<a>`, inputs) sin trampas de foco.
  - `2.4.1`: Enlace para saltar al contenido principal (*skip link*) si aplica.
  - `2.4.4`: Propósito de enlaces claro fuera de contexto (evitar botones vacíos o sin `aria-label`).
  - `2.4.7`: Indicador de foco (`:focus-visible`) siempre visible (prohibido `outline: none` sin reemplazo).
  - `2.5.5`: Áreas táctiles (*touch targets*) de al menos 44×44 px.
- **Comprensible y Robusto:**
  - `3.3.2`: Todo `<input>` o `<select>` con `<label>` asociado o `aria-label` explícito (el `placeholder` no sustituye al label).
  - `4.1.2`: Atributos ARIA (`aria-expanded`, `aria-selected`, `aria-controls`, `role="tab"`, `role="dialog"`) correctamente implementados y sincronizados con el estado real.

#### 4. Diseño Visual (UI) y Consistencia
- **Jerarquía y Foco:** ¿Compiten varios elementos por la atención primaria? ¿Destaca el CTA principal sobre los secundarios?
- **Espaciado y Ritmo:** Inconsistencias en la escala de espaciado, elementos apelotonados o desalineados del grid.
- **Tipografía:** Legibilidad (mínimo 16px en cuerpo de lectura), longitud de línea óptima (50-75 caracteres en bloques de lectura), escala coherente y uso intencional de pesos.
- **Color y Estados:** Coherencia de paleta, estados interactivos (`hover`, `focus`, `active`, `disabled`) predecibles, consistencia en radios de borde, sombras e iconografía.
- **Adecuación al objetivo:** Fricciones de experiencia de usuario o ruido visual que distraiga del propósito de la página.

#### 5. Diseño Responsive y Adaptación Mobile
Evalúa el comportamiento en todos los breakpoints: `XS (320px)`, `SM (375-414px)`, `MD (768px)`, `LG (1024px)` y `XL+ (1280px+)`:
- Desbordamientos horizontales involuntarios (`overflow-x`).
- Elementos solapados, cabeceras fijas que tapan contenido al navegar por anclas, grids o tarjetas que quedan demasiado estrechas antes de apilarse.
- Menús móviles inaccesibles, tablas o contenedores rígidos que rompen en pantallas de 320px.
- Dependencia exclusiva de `:hover` sin alternativa táctil en dispositivos móviles.

#### 6. Rendimiento (Performance y Core Web Vitals)
- **Activos e Imágenes:** Peso de archivos, uso de formatos modernos (`.webp` / `.avif`), presencia de `width` y `height` o `aspect-ratio` explícitos para evitar saltos de diseño (CLS), uso de `loading="lazy"` below-the-fold y `fetchpriority="high"` en la imagen principal (LCP).
- **Carga de Recursos:** Dependencias externas innecesarias (CDNs bloqueantes), tamaño de CSS/JS, bloqueo del hilo principal (INP) o payloads JSON excesivos inyectados en el documento inicial.
- **Backend / Datos (si aplica):** Consultas N+1, cargas completas en memoria sin paginar o falta de caché.

---

### FORMATO OBLIGATORIO DEL ARCHIVO EN `docs/auditorias/AUDITORIA-YYYY-MM-DD.md`

```markdown
# Auditoría Integral — <Nombre del Proyecto> (<Fecha>)

## Resumen Ejecutivo de Incidencias

| Severidad | Cantidad | Descripción |
| :--- | :---: | :--- |
| 🔴 **Crítico** | N | Bloqueantes: seguridad, privacidad, datos expuestos, accesibilidad rota o fallos graves de indexación/layout. |
| 🟠 **Importante** | N | Degradan la experiencia, el SEO, el cumplimiento WCAG AA o el rendimiento percibido. |
| 🟡 **Menor** | N | Ajustes de pulido visual, consistencia UI o micro-optimizaciones de código. |

---

## 🔴 Problemas Críticos (Atención Inmediata)

### [C-01] <Categoría: Seguridad / SEO / A11Y / Responsive / UI / Perf> — <Título claro del problema>
- **Dónde:** `<archivo:línea>` o `<selector>`
- **Evidencia:** `<fragmento de código, métrica o valor actual>`
- **Impacto:** `<por qué es crítico y a quién afecta>`
- **Fix propuesto:**
  ```<lenguaje>
  <código o comando exacto para solucionarlo>
  ```

---

## 🟠 Problemas Importantes

### [I-01] <Categoría> — <Título del problema>
- **Dónde:** `<archivo:línea>`
- **Evidencia:** `<evidencia concreta>`
- **Impacto:** `<impacto real>`
- **Fix propuesto:** `<solución técnica exacta>`

---

## 🟡 Problemas Menores y Pulido

### [M-01] <Categoría> — <Título del problema>
- **Dónde:** `<archivo:línea>`
- **Evidencia:** `<evidencia concreta>`
- **Fix propuesto:** `<solución técnica exacta>`

---

## 📋 Plan de Acción Priorizado (Impacto vs. Esfuerzo)

| Orden | ID | Acción concreta | Archivo(s) | Impacto | Esfuerzo (S/M/L) |
| :---: | :---: | :--- | :--- | :---: | :---: |
| 1 | C-01 | ... | ... | Alto | S |
| 2 | I-01 | ... | ... | Medio | S |
```

**Instrucción final:** Una vez generado el archivo de auditoría en `docs/auditorias/`, muéstrame un resumen breve y espera mi confirmación antes de aplicar cualquier cambio en el código o ejecutar `git push`.
```
