# Evaluation Rubric: EventTick Frontend Design

Evaluation framework for the EventTick web interface using the GAN-Design loop.

Pass threshold: **7.5 / 10.0**

---

### 1. Design Quality (weight: 0.35)
- **Visual Hierarchy**: Clear separation of primary, secondary, and tertiary elements across pages.
- **Color Harmony & Palette**: Cohesive modern slate-indigo aesthetic inspired by Luma/Stripe/Linear without visual noise.
- **Typography & Rhythm**: Appropriate font scale, line heights, letter-spacing, and clear content scannability.
- **Layout & Composition**: Responsive grid layout, elegant whitespace breathing room, balanced information density.

---

### 2. Originality (weight: 0.30)
- **Creative Identity**: Beyond standard cookie-cutter bootstrap dashboards; distinctive event ticketing aesthetic.
- **Memorable Micro-Moments**:
  - Digital perforated boarding pass / ticket stub layout with notch accents for e-tickets.
  - Interactive gate check-in scanner feedback with high-contrast state transitions.
  - Sticky checkout drawer with real-time price calculation and voucher preview.
- **Atmosphere & Polish**: Subtle glowing gradients, modern backdrop-blur navbars, polished status pill designs.

---

### 3. Craft & Attention to Detail (weight: 0.25)
- **Tabular Numerics**: Consistent numeric alignment (`font-variant-numeric: tabular-nums`) for currency, quantities, and dates.
- **State Design**: Elegant empty states, loading placeholders, active/hover transitions, focus rings.
- **Edge-Case Resilience**: Text wrapping, badge truncation, responsive stacking on mobile vs. desktop viewports.
- **Bug-Preservation Discipline**: Clean separation between intentional educational seeded bugs (SEED-06, SEED-07, SEED-08, SEED-09, SEED-10, SEED-11) and actual design craft flaws.

---

### 4. Functionality & Usability (weight: 0.10)
- **Information Architecture**: Intuitive user journey from Discovery -> Detail -> Booking -> Receipt -> Passbook -> Scanner.
- **Frictionless Navigation**: Role badges, balance indicators, clear CTA prominence, breadcrumb/back navigations.
- **Accessibility Baselines**: Semantic HTML structures, readable contrast ratios on text elements.
