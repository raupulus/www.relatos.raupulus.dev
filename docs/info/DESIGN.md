# Sistema de Diseño y Arquitectura Visual — relatos.raupulus.dev

> **Proyecto:** Raupulus Tales / Historias Multimedia (`relatos.raupulus.dev`)  
> **Propósito:** Portal web para relatos literarios de ficción multimedia generados con IA, audiolibros multilingües, vídeos cinematográficos 1080p y storyboards.  
> **Despliegue:** 100% estático, autosuficiente, sin dependencias ni CDNs externos (`alpine.js` local + Tailwind CSS precompilado).

---

## 1. Identidad de Marca y Paleta Cromática

Basado en la fisonomía y colores extraídos directamente del logotipo oficial de Raupulus (`logo_512x512.png` / `logo_512x512.webp`):

| Token | Valor Hexadecimal | Rol en el Diseño | Uso Principal |
| :--- | :--- | :--- | :--- |
| **Crimson Red (Primario)** | `#941300` | Acento dominante de fuego / sangre / intensidad narrativa | Botones de acción, bordes activos, badges destacados, barras de progreso |
| **Crimson Glow / Hover** | `#b81d05` | Resplandor y estado hover del acento primario | Hover en botones principales, glows de tarjetas |
| **Deep Velvet Plum (Secundario)** | `#371632` | Tonalidad noble misteriosa / atmósfera literaria | Fondos de tarjetas intermedias, bordes sutiles, degradados |
| **Rose Damask / Baya (Terciario)** | `#8f2e49` | Matiz dramático cálido | Etiquetas de género, tags temáticos, acentos secundarios |
| **Obsidian Void (Fondo Principal)** | `#0a060a` / `#050205` | Fondo oscuro inmersivo cinematográfico | Fondo general del viewport (`body`), contraste máximo |
| **Surface Dark (Superficie 1)** | `#120a14` | Contenedor base de contenido | Tarjetas de relatos, paneles modales, navbar |
| **Surface Elevated (Superficie 2)** | `#1a0f1d` | Elevación y tarjetas interactivas | Estado hover de tarjetas, menú desplegable |
| **Border Subtle** | `#2d1728` | Delimitación estructural no invasiva | Divisores, bordes de contenedor |
| **Border Glow** | `#8f2e4966` / `#94130088` | Resplandor dinámico en foco/hover | Selección de historias y botones |
| **Text Bright (Blanco puro)** | `#ffffff` | Títulos y llamadas a la acción clave | Encabezados H1, H2, botones primarios |
| **Text Main (Casi blanco rosáceo)** | `#eedfe3` | Lectura de relatos y párrafos | Texto del cuerpo, sinergia directa con el logo |
| **Text Muted (Lavanda ceniza)** | `#a5919b` | Metadatos y detalles técnicos | Tiempos de lectura, número de palabras, autoría |
| **YouTube Brand Red** | `#ff0000` | Integración y llamadas al canal oficial | Botones directos a YouTube y badges |

---

## 2. Tipografía y Jerarquía Visual

- **Pila tipográfica sin fuentes externas (Local/System First):**
  - **Cuerpo y lectura:** Sistema de fuentes sans-serif de alta legibilidad en pantallas (`system-ui`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, `Helvetica Neue`, `sans-serif`).
  - **Títulos y encabezados:** Acentos tipográficos fuertes, con tracking ligeramente ampliado (`letter-spacing: -0.02em` a `0.05em`) para títulos cinematográficos.
  - **Relatos literarios:** Máxima comodidad de lectura con `max-w-prose`, interlineado relajado (`leading-relaxed` / `leading-loose`) y escala de grises cálida derivada del `#eedfe3`.

---

## 3. Estructura y Componentes Clave

1. **Header / Barra de Navegación:**
   - Logotipo oficial local (`assets/images/logo.webp` / `.png`) con texto de marca *Raupulus Tales*.
   - Selector de filtro rápido (Todos, Ficción, Suspense, Sci-Fi, Fantasía).
   - Acceso directo al canal de YouTube y selector de idioma (es-ES, es-LAT, en-US).

2. **Hero Banner:**
   - Gancho cinematográfico con degradado radial `from-crimson/20 via-plum/10 to-transparent`.
   - Llamada a la acción rápida: «Último relato estrenado» y «Ver videorrelato en YouTube».

3. **Rejilla de Relatos / Historias:**
   - Tarjetas (*Story Cards*) con ratio 16:9 para portadas de episodios.
   - Badges con tiempo de lectura (ej. 9 min) y duración del vídeo (ej. 12 min).
   - Indicador de idiomas disponibles (ES / LAT / EN).
   - Sinopsis sugerente sin spoilers.

4. **Visor de Relato / Maqueta de Escenas:**
   - Estructura preparada para integrar el reproductor de YouTube responsive (ratio 16:9) manteniendo el flujo sin bloqueos.
   - Pestañas con Alpine.js para alternar entre:
     - 📖 **Relato Literario** (lectura cuidada con tipografía editorial).
     - 🎬 **Storyboard & Escenas** (marcas de tiempo e ilustraciones).
     - 🎙️ **Locución & Audios** (versiones en español peninsular, latino e inglés).

5. **Footer:**
   - Enlace oficial a la red Raupulus (`raupulus.dev`, `music.raupulus.dev`).
   - Contacto legal y público: `public@raupulus.dev`.
   - Nota de producción y copyright.

---

## 4. Principios Técnicos

1. **Cero activos de terceros en runtime:** Ni Google Fonts, ni CDNs de Tailwind, ni scripts externos rastreadores.
2. **Alpine.js local:** En `assets/js/alpine.min.js`.
3. **Tailwind CSS pretranspilado:** Generado en `assets/css/tailwind.css` y `assets/css/style.css` para despliegue estático directo en GitHub Pages / Nginx / Cloudflare.
4. **Accesibilidad (a11y):** Contraste WCAG AAA en fondos oscuros, focus visible en `#941300` / `#eedfe3`, soporte para modo lectura.
