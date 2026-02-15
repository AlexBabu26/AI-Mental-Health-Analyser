## Front-end design + implementation document (HTML/CSS/JS + Bootstrap)

**Product name:** **AI Mental Health Analyzer**
**Context:** Marketing + conversion website for a mental health platform (programs, resources, clinician-led support). Visual style: calm pastel gradient hero, bold dark typography, rounded “pill” CTAs, rounded cards, and a high-contrast dark feature section.

---

## 1) Tech stack and conventions

**Stack**

* **HTML5**
* **CSS3** (custom CSS + Bootstrap utilities)
* **JavaScript (ES6)** for interactivity
* **Bootstrap 5** (layout, components, responsive behavior)

**Recommended dependencies**

* Bootstrap 5 CSS/JS bundle (includes Popper)
* Optional: Bootstrap Icons (or Font Awesome)
* Optional: AOS (Animate On Scroll) *or* a small IntersectionObserver script (preferred for performance)


---

## 2) Information architecture mapped to sections (Bootstrap-first)

**Header/Nav (sticky)**

* Brand: **AI Mental Health Analyzer**
* Links: Services, Programs, Resources, About
* Right: Primary CTA “Start assessment” + optional search icon

**Homepage sections**

1. **Hero** (gradient background, H1, trust microcopy, CTA)
2. **Value proposition** (light section)
3. **Dark feature panel** (charcoal background + inner cards)
4. **Programs grid** (cards with tags/filters)
5. **Credibility** (team highlight + testimonials)
6. **Final CTA** (simple and reassuring)

**Footer**

* Privacy, Terms, Contact, Crisis resources link, Social

---

## 3) Layout + Bootstrap grid specs

**Container strategy**

* Use `container` (fixed max width) for most sections.
* Use `container-fluid` only for full-bleed backgrounds (hero gradient/dark panel), with inner `container`.

**Grid**

* Desktop: `row` with `col-lg-*`
* Tablet: `col-md-*`
* Mobile: `col-12` stacked

**Spacing**

* Section padding: `py-5` (mobile) up to `py-lg-6` (custom class for desktop)
* Card gap: `g-4`
* Keep whitespace generous; mental health content needs low cognitive load.

---

## 4) Visual system translated to CSS tokens

Put these in `assets/css/styles.css` and reuse them across components.

### CSS variables (design tokens)

```css
:root{
  --bg: #fbfaf7;               /* warm off-white */
  --text: #121212;             /* near-black */
  --muted: #5b5b5b;

  --accent: #8f87ff;           /* lavender/periwinkle */
  --accent-2: #b9b4ff;

  --panel: #141417;            /* charcoal */
  --card: #ffffff;
  --border: rgba(18,18,18,.10);

  --radius-lg: 24px;
  --radius-md: 16px;
  --radius-pill: 999px;

  --shadow-sm: 0 8px 24px rgba(0,0,0,.08);
  --shadow-xs: 0 6px 18px rgba(0,0,0,.06);
}
```

### Global base styles

* `body` background `--bg`, text `--text`
* Headings: bold, tight-ish tracking
* Body: comfortable line height (1.6–1.8)

```css
body{
  background: var(--bg);
  color: var(--text);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  line-height: 1.7;
}

h1,h2,h3{ letter-spacing: -0.02em; }
```

### Hero background gradient (full-bleed)

```css
.hero{
  background: radial-gradient(1200px 500px at 20% 20%, #fff2b8 0%, transparent 60%),
              radial-gradient(900px 420px at 80% 10%, #d7d2ff 0%, transparent 55%),
              linear-gradient(180deg, #fbfaf7 0%, #fbfaf7 100%);
}
```

---

## 5) Bootstrap component mapping

### 5.1 Header / Navbar

**Bootstrap components**

* `navbar navbar-expand-lg`
* `sticky-top`
* CTA button as `btn` with custom pill styling

**Custom styles**

```css
.navbar{
  background: rgba(251,250,247,.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
}

.btn-pill{
  border-radius: var(--radius-pill);
  padding: .75rem 1.1rem;
}

.btn-accent{
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
.btn-accent:hover{ filter: brightness(.95); }
.btn-accent:focus{ box-shadow: 0 0 0 .25rem rgba(143,135,255,.35); }
```

### 5.2 Hero

**Bootstrap layout**

* Left: text (`col-lg-6`)
* Right: image/collage (`col-lg-6`)

**Hero elements**

* H1: “Embark on your mental journey with professionals”
* Supporting copy
* Trust row: overlapping avatars + “Trusted by …”
* Primary CTA + secondary “Explore programs”

**Trust avatars**

* Use `d-flex align-items-center`
* Overlap via negative margin class or custom CSS

```css
.avatar-stack img{
  width: 36px; height: 36px; border-radius: 50%;
  border: 2px solid var(--bg);
  margin-left: -10px;
}
.avatar-stack img:first-child{ margin-left: 0; }
```

### 5.3 Card system (Programs / Value props)

**Bootstrap**

* `card h-100 border-0`
* `shadow-sm` via custom var

**Custom**

```css
.card-soft{
  border-radius: var(--radius-lg);
  background: var(--card);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
}
.card-soft:hover{ transform: translateY(-2px); transition: .2s ease; }
```

### 5.4 Dark feature panel

**Structure**

* Full-bleed `section` with `background: var(--panel)`
* Inside: `container` with light cards

```css
.panel-dark{
  background: var(--panel);
  color: #fff;
}
.panel-dark .card-soft{
  background: #fff;
  color: var(--text);
}
```

### 5.5 Testimonials

* Bootstrap `carousel` OR simple card grid
* Prefer grid for accessibility and performance; carousel only if you truly need it.

### 5.6 Footer

* Simple grid: columns for links, contact, social
* Add “Crisis resources” link and privacy note (important in this domain)

---

## 6) JavaScript behaviors (minimal, accessible)

Put in `assets/js/main.js`.

### 6.1 Smooth scroll for anchor links

* Use `scrollIntoView({behavior:'smooth'})`
* Respect reduced motion

### 6.2 “Active section” nav highlighting (optional)

* IntersectionObserver to add `active` to nav items

### 6.3 Program filter (tags)

* Add `data-category` to cards
* Clicking a filter hides non-matching cards (set `hidden` attribute)

Example filtering logic (high level):

* Query all filter buttons and program cards
* On click: set active button state; toggle card visibility based on `data-category`

### 6.4 Form validation (if you add intake/lead form)

* Use Bootstrap validation classes (`was-validated`)
* Never claim diagnoses; keep language “screening / insights” only.

---

## 7) Accessibility requirements (implementation-ready)

* **Color contrast:** ensure accent buttons meet WCAG AA (consider darker accent shade for text-on-accent).
* **Focus states:** keep visible focus ring on all interactive elements.
* **Reduced motion:** disable animations if `prefers-reduced-motion: reduce`.
* **ARIA:** navbar toggler, modals, accordions should follow Bootstrap ARIA patterns.
* **Language:** avoid coercive CTAs; use supportive microcopy.

CSS for reduced motion:

```css
@media (prefers-reduced-motion: reduce){
  *{ scroll-behavior: auto !important; transition: none !important; animation: none !important; }
}
```

---

## 8) Suggested `index.html` section outline (Bootstrap skeleton)

Use this as your page outline (not full code, but implementation mapping):

* `<nav class="navbar navbar-expand-lg sticky-top">`

  * Brand: **AI Mental Health Analyzer**
  * Links
  * CTA button `.btn btn-accent btn-pill`
* `<section class="hero py-5 py-lg-6">`

  * `container` → `row align-items-center g-5`
  * Left: H1, copy, CTAs, trust row
  * Right: hero image in rounded container
* `<section class="py-5">` Value props (3 cards)
* `<section class="panel-dark py-5">` Dark panel with inner cards
* `<section class="py-5">` Programs grid + filter pills
* `<section class="py-5">` Team + Testimonials
* `<section class="py-5">` Final CTA (simple)
* `<footer class="py-5 border-top">`

---

## 9) Content and compliance notes (mental health domain)

* Use “assessment,” “screening,” “insights,” “support”—avoid “diagnose” unless clinically validated and legally supported.
* Add clear privacy statement near any form input.
* Add crisis resources link in footer (and optionally in header).

---

## 10) Deliverables (engineering-ready)

* `index.html` (single-page marketing site)
* `styles.css` (tokens + component overrides)
* `main.js` (smooth scroll, filtering, nav active state, validation)
* Assets: optimized WebP images, avatar placeholders, icons

---