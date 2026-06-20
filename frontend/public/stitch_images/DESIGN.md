---
name: Neon Slate
colors:
  surface: '#0e1511'
  surface-dim: '#0e1511'
  surface-bright: '#343b36'
  surface-container-lowest: '#09100c'
  surface-container-low: '#161d19'
  surface-container: '#1a211d'
  surface-container-high: '#242c27'
  surface-container-highest: '#2f3632'
  on-surface: '#dde4dd'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dde4dd'
  inverse-on-surface: '#2b322d'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#c0c1ff'
  on-secondary: '#1000a9'
  secondary-container: '#3131c0'
  on-secondary-container: '#b0b2ff'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#e29100'
  on-tertiary-container: '#523200'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#e1e0ff'
  secondary-fixed-dim: '#c0c1ff'
  on-secondary-fixed: '#07006c'
  on-secondary-fixed-variant: '#2f2ebe'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0e1511'
  on-background: '#dde4dd'
  surface-variant: '#2f3632'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 28px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.2'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 48px
  container-max: 1280px
  gutter: 20px
---

## Brand & Style
The design system is engineered for a premium, AI-driven culinary discovery experience. It employs a **Modern Dark UI** aesthetic characterized by deep oceanic slates and high-energy neon accents. The visual narrative balances professional utility with futuristic sophistication, evoking a sense of "intelligence behind the curtain."

The style leverages **Glassmorphism** for navigational elements and overlays to maintain a sense of depth and transparency in the data. Interactive elements are treated with subtle luminosity and scale-based haptics to ensure the interface feels alive and responsive to the user's intent.

## Colors
The palette is rooted in a "Deep Slate" foundation to minimize eye strain and allow neon accents to vibrate. 

- **Action State:** Use Emerald Green (#10b981) for primary CTA buttons and success states. These should often be accompanied by a subtle outer glow (`box-shadow`) of the same color at low opacity.
- **Data & Info:** Use Violet/Indigo (#6366f1) for secondary AI-driven insights and information badges.
- **Validation:** Rose Red is reserved for critical errors, while Amber is used exclusively for ratings and cautionary system alerts.
- **Glassmorphism:** Apply a `backdrop-filter: blur(12px)` to the glass surface variable to create the signature premium layered effect.

## Typography
This design system utilizes a dual-type approach. **Outfit** provides a geometric, modern flair for high-level headings and brand touchpoints, ensuring the "premium" feel is immediate. **Inter** is used for all functional UI components, data tables, and long-form descriptions to ensure maximum legibility at smaller scales.

For AI-generated text or recommendations, use `body-lg` with a slightly increased line height to differentiate it from standard system text.

## Layout & Spacing
The layout follows a **12-column fluid grid** for desktop and a **single-column stack** for mobile. 

- **Grid:** Use a 24px gutter on desktop and a 16px gutter on mobile. 
- **Margins:** Page margins should scale from 16px (mobile) to 48px+ (desktop) to allow the UI to breathe.
- **Rhythm:** All spacing between elements must be a multiple of the 4px base unit. Component internal padding should default to `md` (16px).

## Elevation & Depth
Depth is created through color stacking rather than traditional heavy shadows.
- **Level 0 (Base):** Deep Slate (#0b0f19)
- **Level 1 (Cards):** Navy Slate (#131b2e) with a 1px border of `rgba(255, 255, 255, 0.05)`.
- **Level 2 (Dropdowns/Modals):** Muted Blue Slate (#1e293b) or Glassmorphic surfaces with a 12px blur.
- **Interaction:** On hover, cards should lift slightly using a `transform: translateY(-4px)` and increase border opacity to `0.15`.
- **Shadows:** Use a very soft, large-radius ambient shadow for floating elements: `0 20px 40px rgba(0, 0, 0, 0.4)`.

## Shapes
The shape language follows a progressive rounding scale to reinforce the friendly yet professional AI persona.
- **Standard (8px):** Buttons, input fields, and small tags.
- **Large (14px):** Content cards, menu panels, and image containers.
- **Extra Large (24px):** Main container wraps and specialized "AI Insight" bubbles.

## Components
- **Buttons:** Primary buttons use a solid Emerald Green fill with white text. Apply a `cubic-bezier(0.4, 0, 0.2, 1)` transition for hover states. On hover, add a 10px Emerald glow.
- **Cards:** Restaurant cards should use the Navy Slate background. Images should have a subtle dark gradient overlay at the bottom to ensure white typography (price/rating) remains legible.
- **Chips:** For cuisine types, use a ghost-style border (1px `text_muted`) with `label-sm` typography. Active chips flip to the Primary accent color.
- **Inputs:** Use the Tertiary background (#1e293b). On focus, the border transitions to Emerald Green with a 2px outer glow.
- **Skeletons:** Loading states should use a pulsing shimmer effect moving from Navy Slate to Muted Blue Slate.
- **AI recommendation badge:** A special component using a Violet-to-Emerald gradient border and a subtle pulse animation to signify "Active Intelligence."