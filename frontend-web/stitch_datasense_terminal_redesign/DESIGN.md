---
name: Synthetic Intelligence Terminal
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#bdc9c5'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#879390'
  outline-variant: '#3e4946'
  surface-tint: '#7ad7c6'
  primary: '#7ad7c6'
  on-primary: '#003730'
  primary-container: '#0c7e70'
  on-primary-container: '#cefff4'
  inverse-primary: '#006b5e'
  secondary: '#e6feff'
  on-secondary: '#003739'
  secondary-container: '#00f4fe'
  on-secondary-container: '#006c71'
  tertiary: '#ffb59f'
  on-tertiary: '#581e0a'
  tertiary-container: '#a85b43'
  on-tertiary-container: '#fff3f0'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#96f3e2'
  primary-fixed-dim: '#7ad7c6'
  on-primary-fixed: '#00201c'
  on-primary-fixed-variant: '#005047'
  secondary-fixed: '#63f7ff'
  secondary-fixed-dim: '#00dce5'
  on-secondary-fixed: '#002021'
  on-secondary-fixed-variant: '#004f53'
  tertiary-fixed: '#ffdbd0'
  tertiary-fixed-dim: '#ffb59f'
  on-tertiary-fixed: '#3a0a00'
  on-tertiary-fixed-variant: '#75331e'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
  terminal-black: '#050505'
  surface-charcoal: '#111111'
  matrix-green: '#0C7E70'
  electric-cyan: '#00F5FF'
  glass-border: rgba(255, 255, 255, 0.1)
typography:
  headline-lg:
    fontFamily: Geist
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  body-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  terminal-code:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  terminal-log:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.1em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin: 32px
  container-max: 1440px
---

## Brand & Style

The design system is engineered to evoke the feeling of a high-end, futuristic command center. It targets technical power users who value precision, speed, and a sophisticated aesthetic. The brand personality is **Atmospheric, Technical, and Sovereign**, positioning the AI not just as a tool, but as a high-performance operating environment.

The design style is a hybrid of **Glassmorphism** and **Modern Terminal** aesthetics. It utilizes deep, "cosmic" layering to create visual depth, where high-density information is balanced by translucent surfaces and vibrant, luminous accents. Every interaction should feel intentional, with subtle glows and crisp borders reinforcing the "synthetic" nature of the interface.

## Colors

The palette is rooted in the "Void" — a deep, multi-tonal dark mode that uses **#050505** as the true base. Surface elevations are defined by **#111111**, providing a subtle contrast for container separation. 

**Matrix Green (#0C7E70)** acts as the primary functional color, used for success states, system logs, and stable connections. **Electric Cyan (#00F5FF)** is the secondary accent, reserved for high-importance interactions, active cursors, and AI processing states. These "Neon" colors should be used sparingly against the dark backgrounds to maintain a sophisticated, low-light atmosphere.

## Typography

This design system employs a dual-font strategy to balance legibility with technical character. 

**Geist** is used for the interface layer (cards, navigation, settings). It provides a clean, high-contrast sans-serif look that feels premium and legible against blurred backgrounds. 

**JetBrains Mono** is used for the data layer (input terminals, code blocks, system status). This font is the "voice" of the AI. Use it for any content that represents machine output or user input. Labels and small metadata should use JetBrains Mono in all caps with increased letter spacing to reinforce the technical, industrial feel.

## Layout & Spacing

The layout follows a **Fixed-Fluid Hybrid Grid**. The main interaction terminal is often centered or sidebar-aligned, with floating glassmorphic panels for supplementary data. 

- **Grid:** A 12-column system is used for dashboard views, while a single-column focused layout is used for the primary terminal interface.
- **Rhythm:** Spacing is strictly based on a 4px increment. Use larger gaps (32px+) between distinct modules to allow the background gradients and blurs to "breathe."
- **Responsive:** On mobile, sidebars collapse into a bottom-anchored command bar. Margins reduce to 16px to maximize the tight horizontal space for code-heavy content.

## Elevation & Depth

Depth is not achieved through shadows, but through **Backdrop Blurs (Glassmorphism)** and **Tonal Layering**. 

1.  **Level 0 (Base):** #050505. The deep void.
2.  **Level 1 (Sub-surface):** #111111 with a 1px solid border of #FFFFFF at 5% opacity.
3.  **Level 2 (Floating Panels):** Background set to #FFFFFF at 3% opacity with a `backdrop-filter: blur(20px)`. This level features a 1px subtle white border (10% opacity) to catch the "light" of the screen.
4.  **Level 3 (Popovers/Modals):** Same as Level 2 but with a subtle outer glow using the primary color (#0C7E70) at a very low spread and opacity (10-15%) to indicate focus.

Interaction triggers a "luminous" response; buttons and active inputs should feel like they are powered by an internal light source.

## Shapes

The shape language is **Soft-Geometric**. We avoid "pill" shapes for buttons to maintain a professional, architectural feel. 

Standard components use a 4px (0.25rem) radius, which provides just enough softness to feel modern without losing the precision of a terminal. Large containers and glass cards may use up to 12px (0.75rem) to differentiate them from smaller UI widgets. Any "active" state or cursor should remain perfectly sharp (0px radius) to emphasize mathematical precision.

## Components

### Buttons
Primary buttons use a solid **Matrix Green** background with black text. Secondary buttons are "ghost" style with a 1px white-border (10% opacity) and white text. All buttons should have a hover state that increases the brightness of the border and adds a faint outer glow.

### Terminal Inputs
Inputs consist of a prompt symbol (`>`) in **Electric Cyan**, followed by a monospaced cursor. There is no enclosing box; instead, a subtle bottom-border glows when the line is active. 

### Glassmorphic Cards
Cards are the primary container for non-terminal data. They must feature a high backdrop-blur (20px+) and a semi-transparent white border. Avoid using background images within cards; keep them minimal to ensure text contrast remains high.

### Status Markers
Small circular indicators for system health. 
- **Active:** Pulsing Electric Cyan.
- **Stable:** Solid Matrix Green.
- **Error:** Solid #FF4D4D (standard warning red, used sparingly).

### Iconography
Icons should be thin-stroke (1px or 1.5px) and strictly geometric. Avoid filled icons unless they represent an active toggle state. Use terminal-inspired symbols (slashes, brackets, carets) as much as possible.