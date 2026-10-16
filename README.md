<p align="center">
  <a href="https://relatos.raupulus.dev" target="_blank" rel="noopener noreferrer">
    <img src="assets/images/logo.webp" alt="Raupulus Tales Logo Oficial" width="120" style="border-radius: 50%;">
  </a>
</p>

<h1 align="center">RAUPULUS TALES</h1>

<p align="center">
  <strong>📖 Ficción Multimedia • Audiolibros Calibrados • Cinematografía Digital y Relatos Literarios 🎬</strong><br>
  <em>Portal web oficial del universo de relatos de Raupulus Tales</em>
</p>

<p align="center">
  <a href="https://www.youtube.com/@RaupulusTales" target="_blank">
    <img src="https://img.shields.io/badge/YouTube-%40RaupulusTales-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube Channel">
  </a>
  <a href="https://www.youtube.com/@RaupulusTales?sub_confirmation=1" target="_blank">
    <img src="https://img.shields.io/badge/Suscribirse-Canal%20Oficial-red?style=for-the-badge&logo=youtube&logoColor=white" alt="Suscribirse al canal">
  </a>
  <a href="https://relatos.raupulus.dev" target="_blank">
    <img src="https://img.shields.io/badge/Web%20Oficial-relatos.raupulus.dev-941300?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Sitio Web">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Relatos-10%20Historias-crimson?style=flat-square" alt="10 Relatos">
  <img src="https://img.shields.io/badge/C%C3%B3digo-GNU%20AGPLv3-blue?style=flat-square" alt="AGPLv3 License">
  <img src="https://img.shields.io/badge/Contenido-Todos%20los%20derechos%20reservados-darkred?style=flat-square" alt="All Rights Reserved">
  <img src="https://img.shields.io/badge/Contacto-public%40raupulus.dev-8f2e49?style=flat-square" alt="Contacto">
</p>

---

## ⚡ Accesos Rápidos

| 🎯 Destino | 🔗 Enlace Directo | ℹ️ Descripción |
| :--- | :--- | :--- |
| 🌐 **Portal Web Oficial** | [**relatos.raupulus.dev**](https://relatos.raupulus.dev) | Catálogo interactivo con páginas dedicadas por relato, sinopsis y visor. |
| 🔴 **Canal Oficial de YouTube** | [**youtube.com/@RaupulusTales**](https://www.youtube.com/@RaupulusTales) | Producciones cinematográficas en vídeo Full HD 1080p con locución en estudio. |
| 🔔 **Suscripción Directa (1 Clic)** | [**Suscribirse a @RaupulusTales**](https://www.youtube.com/@RaupulusTales?sub_confirmation=1) | Recibe estrenos semanales y nuevas sagas narrativas. |

---

## 📖 Acerca del Proyecto

**Raupulus Tales** (`relatos.raupulus.dev`) es el portal web oficial del universo de relatos y ficción multimedia de Raupulus. Presenta historias literarias completas concebidas con visión cinematográfica:

- **Relatos Literarios Completos:** Narrativa madura y humana (1.600 a 2.400 palabras) optimizada para lectura silenciosa o en voz alta.
- **Páginas Dedicadas por Relato:** Cada historia cuenta con su propia URL estática (`relatos/NNNN-slug.html`) con metadatos Open Graph, Twitter Cards y marcado semántico Schema.org (`ShortStory`) para indexación en Google.
- **Trinidad de Voces Multilingües:** Locución calibrada a 192 kbps en tres variantes: España (`es-ES`), Latinoamérica (`es-LAT`) e Internacional (`en-US`), con duración idéntica al segundo.
- **Consistencia Visual y Avatares:** Biblia visual de personajes con láminas de referencia anatómica en 3 posiciones (cabeza y cuerpo completo).
- **Vídeos Cinematográficos 1080p:** Movimiento Ken Burns, clips de apertura y grano analógico embebidos directamente desde YouTube.

---

## 🛠️ Arquitectura Técnica

- **Frontend Estático y Ligero:** HTML5 semántico con [Alpine.js](https://alpinejs.dev/) embebido localmente para reactividad instantánea (buscador en tiempo real y filtrado por categorías).
- **Estilos:** [Tailwind CSS v4](https://tailwindcss.com/) pretranspilado en local (`assets/css/tailwind.css`) sin dependencias externas en tiempo de ejecución.
- **Cero CDNs externos:** Sin llamadas a Google Fonts ni CDNs de terceros; máxima privacidad, velocidad y cumplimiento de RGPD.
- **Generador Estático Python:** `scripts/build_site.py` sincroniza relatos, genera páginas dedicadas, comprime portadas y avatares a WebP, y actualiza el catálogo, `sitemap.xml` y `robots.txt`.

### Estructura del Repositorio

```text
├── index.html                  # Catálogo principal con hero y filtros reactivos
├── relatos/                    # Páginas estáticas dedicadas por cada historia
│   ├── 0001-la-que-no-tuvo-hijos.html
│   └── ...
├── data/
│   └── relatos.json            # Base de datos local sincronizada
├── assets/
│   ├── css/tailwind.css        # CSS minificado compilado localmente
│   ├── js/alpine.min.js        # Alpine.js local autónomo
│   └── images/                 # Portadas 16:9, avatares WebP, logo y favicon
├── scripts/
│   └── build_site.py           # Generador estático y sincronizador
├── src/
│   └── input.css               # Hoja fuente de Tailwind CSS
├── LICENSE                     # Licencia dual AGPLv3 + Reserva de Derechos
├── LICENSE.md                  # Términos detallados de propiedad intelectual
└── package.json
```

---

## 💻 Compilación y Ejecución en Local

1. **Instalar dependencias:**
   ```bash
   npm install
   ```

2. **Compilar el sitio web completo:**
   ```bash
   npm run build
   ```
   *Sincroniza datos, genera las páginas HTML dedicadas, actualiza sitemap y transpila Tailwind CSS.*

3. **Previsualizar en servidor local:**
   ```bash
   npx serve .
   ```

---

## ⚖️ Licencia y Propiedad Intelectual

Este proyecto cuenta con un **modelo de licenciamiento dual** estrictamente delimitado para proteger las creaciones literarias y multimedia mientras se comparte el código técnico con la comunidad de software libre:

### 1. Código Fuente del Portal Web: GNU AGPLv3
Todo el código de desarrollo del portal (código HTML, scripts en `scripts/build_site.py`, hojas de estilo CSS en `src/` y `assets/css/`, y lógica de interfaz en JavaScript) está licenciado bajo la **[GNU Affero General Public License v3.0 (AGPLv3)](LICENSE)**.

### 2. Contenido Creativo y Relatos: Propiedad Privada y Derechos Reservados
> [!IMPORTANT]
> **Copyright © 2026 Raupulus Tales. Todos los derechos reservados.**
>
> Todos los relatos literarios, textos narrativos, sinopsis, personajes, guiones, storyboards, pistas de audio, locuciones, ilustraciones de portada, láminas de avatar, marcas y producciones en vídeo son **obra artística privada y propiedad exclusiva de Raupulus Tales**.
>
> - **Queda terminantemente prohibida** su reproducción, distribución, comercialización, modificación, traducción o republicación sin autorización previa expresa por escrito.
> - **Prohibición estricta de IA:** Se prohíbe de forma explícita el uso, scraping o ingestión de cualquier relato, texto, locución o imagen de este proyecto para entrenar o ajustar modelos de Inteligencia Artificial (LLMs, modelos multimodales, clonación de voz, etc.).

Para consultar los términos jurídicos completos, consulte [LICENSE.md](LICENSE.md).

---

## 📬 Contacto Oficial

- **Correo Oficial:** `public@raupulus.dev`
- **Web Oficial:** [https://relatos.raupulus.dev](https://relatos.raupulus.dev)
- **Canal de YouTube:** [https://www.youtube.com/@RaupulusTales](https://www.youtube.com/@RaupulusTales)
- **Proyecto Matriz:** [https://raupulus.dev](https://raupulus.dev)
