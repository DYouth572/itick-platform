# Design Specification: EventTick Web Interface

## 1. Design Vision & Aesthetic Direction
EventTick is an event discovery and ticketing platform built for technology summits, conferences, and community workshops.
- **Inspiration**: Luma (lu.ma), Stripe, Linear, Apple Developer events.
- **Palette**: Deep slate (`slate-900`, `slate-950`), clean neutral backgrounds (`slate-50`, `white`), refined indigo accents (`indigo-600`, `indigo-500`), subtle border contrast (`border-slate-200/80`).
- **Typography & Details**: Clean geometric sans-serif (Inter / System font), precise tabular figures (`font-variant-numeric: tabular-nums`) for currency, ticket counters, timestamps; subtle shadow elevations; high-contrast badges.
- **Key Experience Touchpoints**:
  1. Discovery Grid (`/`): High-converting event cards with category pills, date badges, pricing hierarchy.
  2. Booking Flow (`/events/{id}`): Sticky checkout ticket tier selector, real-time discount calculation, clear breakdown.
  3. Gate Scanner (`/checkin-gate`): Full-screen interactive state feedback (Emerald Green on valid, Crimson Red on invalid/used).
  4. Ticket Passbook (`/my-tickets`): Digital boarding pass / ticket stub layout with perforated notch effect, simulated QR code.

## 2. Testing Constraints (Intentionally Preserved Seeded Bugs)
To preserve the educational testing rubric of the capstone:
- SEED-06: Disabled state styling bug on sold-out tier.
- SEED-07: Unclamped text bug on Event 3.
- SEED-08: Left-aligned and unformatted currency on checkout receipt.
- SEED-09, SEED-10, SEED-11: Content and copy inconsistencies.
All other UI surfaces must meet top-tier design craft standards.
