# Design: the reading room, after hours (Problem 10)

The shop now looks like a university library late at night — deep Yale blue, oak
and brass, lamplight on whatever you are looking at. Everything below is original
SVG drawn for this project; no external images, no Yale logos or marks.

---

## What changed

### The room
Deep Yale blue (`#0f4d92`) over near-black navy, with lamplight pooling at the top
of the page and warm oak and brass for anything structural — shelf edges under the
cards, a brass plate for every button, a hairline of gold under the navigation. Body
text is parchment rather than white, which is easier on the eye against dark blue and
reads like paper under a lamp.

**Why it helps.** The old palette was generic dark-mode. This one says *where you
are* before a shopper reads a word, and it makes the merchandise — mostly navy and
heather grey — sit in a setting rather than float on a background.

### A window onto the night
An arched reading-room window, drawn in SVG, sits beside the headline: stone
mullions, a moon, and sixteen stars that twinkle on their own timers, with lamplight
from the room spilling up the glass.

**Why it helps.** It fixes the time and place in one image, and it gives the home
page somewhere for the eye to rest that is not another product.

### The librarian
An original bulldog — wide head, rose ears, heavy jowls, brass reading glasses, blue
collar — with three states:

| State | When | What you see |
|---|---|---|
| **Sleeping** | desk closed | eyes shut, two gold *z*'s drifting up |
| **Awake** | panel open | eyes open behind the glasses |
| **Thinking** | looking something up | paw prints walking across the desk |

The chat panel is headed **"Ask the Librarian"** with the line *"Open late. Ask the
librarian any time."* — also in the footer of every page.

**Why it helps.** A sleeping dog is an invitation; a spinner is furniture. The
"thinking" paw trail answers the only question a waiting shopper has — *is this
working?* — in the language of the rest of the page. And "ask the librarian" sets a
more accurate expectation than "chat": a librarian looks things up and tells you
when the answer isn't in the building, which is exactly what this assistant does.

### Paw cursors
Two states, both inline SVG: a brass paw for ordinary browsing, and a larger, lit
paw inside a ring over anything clickable. Text fields keep a normal text caret, and
disabled controls keep `not-allowed`.

**Why it helps.** It is the one piece of pure delight here, and it doubles as an
affordance — the cursor changing weight tells you something is clickable before you
have read the label.

### Lamplight on the shelf
Hovering a product card lifts it, warms its border to brass, and throws a soft pool
of lamplight across the top of the photo, as though a desk lamp had been angled at
it. Each card sits on a thin oak shelf edge.

**Why it helps.** Browsing 102 items is tiring. Lighting the one under the cursor
gives a clear sense of place in the grid and makes picking things up feel good —
the small reward that keeps someone scrolling to the end of a shelf.

### "Checked out" stamps
Out-of-stock products get a red double-ruled **CHECKED OUT · ALL SIZES** stamp
across the photo at a slight angle, with the image dimmed behind it. Individual
sizes that are gone get the same stamp in miniature in the size table, with the
size struck through.

**Why it helps.** A greyed-out item is ambiguous — is it gone, or is the page
broken? A stamp is unmistakable, and it reframes an absence as a thing that will
come back, which is both truer and easier to take than "unavailable".

---

## One honest note about the stamps

**No product in the catalogue is currently out of stock in every size** — all 102
have stock somewhere — so the full-card stamp does not appear in normal browsing
today. It is implemented and correct, and will show the moment a product sells out;
it was verified by mocking the API response rather than editing the database.

What *does* occur is **145 of 612 size rows at zero**, so the per-size stamp is the
one shoppers actually see. That is why both exist: the full stamp for the case the
brief describes, the size stamp for the case the data contains.

---

## Accessibility and restraint

- Every animation is disabled under `prefers-reduced-motion` — stars, paw trail,
  lamp flicker, card lift.
- The bulldog carries an `aria-label`; the window and paw prints are `aria-hidden`
  decoration.
- Focus rings are brass and clearly visible against the dark blue.
- Gold on navy and parchment on navy both clear WCAG AA for body text.
- Red appears **only** on a checked-out stamp, so it still reads as a signal.

Colour lives entirely in `frontend/src/theme.css`; the whole shop can be retuned
from that one block.

---

# Second pass — after seeing it built

Six refinements, all about weight: which parts of the room should pull the eye,
and which surfaces should look like the material they are named after.

### The reference desk is louder

The bell is now **92px** rather than 66, with a lamp halo behind it that breathes
in and out on a four-second cycle — brightening, swelling slightly, fading back.
Hovering doubles the tempo. When the desk is closed, three gold **z**'s drift up
and off the top of the button on staggered timers.

**Why it helps.** The assistant is the thing here that a product grid cannot do,
and it was sitting in the corner being tasteful. A light that breathes is read by
peripheral vision as *something alive over there* without ever blocking the page,
and a sleeping dog with z's rising off him is an invitation to wake him. The first
version was decoration; this one asks to be clicked.

### "Open late. Ask the librarian any time." now opens it

The line is a button, on the home page and in the footer of every page. It
underlines and warms to lamplight on hover.

**Why it helps.** It looked clickable and wasn't, which is worse than not looking
clickable at all. Now the one sentence that tells a shopper help is available is
also the way to get it — the shortest possible path from "I have a question" to
asking it.

### Prices on brass plaques

Every price sits on a small engraved brass plate: bevelled edge, highlight along
the top, dark engraved numerals, and a screw head at each end.

**Why it helps.** Price is the single number a shopper is scanning for, and it was
competing with product names in the same gold. Giving it a physical object of its
own makes it findable at a glance down a column of cards, and it reads as a
considered price on a display case rather than a line of text.

### Oak panelling over the stacks

The navigation is now actual wood — fine vertical grain, a few darker heartwood
streaks, lamplight falling across the top, and a brass strip along the bottom
edge where the panel meets the room.

**Why it helps.** It was the last generic dark-mode surface on the page, and it
sits above everything. Making it a material gives the shop a top edge that looks
built rather than rendered, and the brass strip does the work the old hairline
border did while belonging to the room.

### The window actually has panes

Two bugs, both visible in the first build and both now fixed:

- The mullions were drawn with a gradient stroke, but a perfectly straight line has
  a zero-width bounding box and SVG's default `objectBoundingBox` gradient units
  cannot be mapped onto one — so they silently did not paint. Switching the
  gradient to `userSpaceOnUse` brought all six panes back.
- The lamplight at the base of the glass was a flat translucent ellipse, which read
  as a grey hill rather than light. It is now a radial gradient that fades out.

### Footer trimmed

The coursework disclaimer is gone. The footer is the shop's address line and the
invitation to ask the librarian.

**Why it helps.** Telling someone mid-browse that the shop is not real is the
fastest way to end a visit.
