# 🌸 Terminal 3D Potted Plant & Stargazer Lily Blooming Simulation

A high-fidelity botanical 3D simulation in ASCII/Unicode terminal art featuring a **dense potted plant growing from scratch** in a modern two-tone ceramic planter (modeled directly on **Image 2**) from which **multiple magnificent pink lilies bloom** (modeled directly on **Image 1**), woven delicately from the **falling flower/petal characters** (`❀`, `✿`, `❁`, `✽`, `✾`), with steady upright 3D framing (NO 360° spinning), continuous 3D span rasterization with zero gaps or barcode pixelation, realistic shadow casting, ceramic pot lighting with ambient occlusion, a clean default terminal background with falling background petals, and synchronized audio from **"Golden Brown"** (starting from 21 seconds).

---

## 🌺 Botanical Design & Anatomy

### 1. Modern Two-Tone Ceramic Planter (Image 2)
- **Non-Pixelated in Character Modes (`floral`, `botanical`, etc.)**:
  - **White Porcelain Upper Band**: Sleek, non-pixelated horizontal ceramic strokes (`━`, `─`, `┄`).
  - **Ribbed Tan Ceramic Base**: Lathe-turned bamboo / terracotta horizontal grooves (`═`, `━`, `─`, `┄`, `┈`) following the actual 3D ribs of the pot in Image 2.
  - **Soil & Ground Shadow**: Fine organic stipple (`•`, `·`) grounding the pot cleanly without blockiness.
- **Pixelated Shaded Blocks Exclusively in `shaded` Mode**:
  - Retains pure solid density blocks (`█`, `▓`, `▒`, `░`) strictly when running in `shaded` mode.
- **Realistic 3D Cylindrical Lighting**:
  - Front-right side catches direct warm sunlight with specular porcelain ceramic gloss, while the left side rolls into a soft core shadow.
  - **Foliage Canopy Shadow**: Overhanging cascading leaves cast a realistic diagonal shadow onto the upper pot rim and body.

### 2. Dense Lush Foliage Plant (Image 2)
- **20 Broad Lanceolate Leaves across 3 Tiers**:
  - *Tier 1 (Lower Rim Cascade)*: 7 leaves arching out and gracefully draping downward over the pot rim.
  - *Tier 2 (Mid Spread)*: 7 broad, glossy deep emerald leaves (`#1B5E20` / `#2E7D32`) expanding horizontally.
  - *Tier 3 (Upper Canopy)*: 6 tall upright leaves forming a dense, lush green interior canopy.
- **Transverse V-Gutter Surface Normals**: Each leaf has a natural 3D fold where one side catches the sunlight and the other falls into gentle shade.
- **Tiered Cast Shadows**: Lower cascading leaves receive natural cast shadows from the canopy leaves above.
- **Pale Spring Green Midrib Veins**: Continuous sleek veins (`║`) running from stem to tip down the center of every leaf.

### 3. Multiple Pink Stargazer Lilies (Image 1)
- **6 Recurved Star-Shaped Tepals** (3 inner + 3 outer):
  - Inner petals broader, outer petals slightly narrower, alternating in a 6-pointed star.
  - Wavy, undulating margins and recurving tips reflexing backwards towards the stem.
  - Formed from the delicate falling flower glyphs (`❀`, `✿`, `❁`, `✽`, `✾`) with zero pixelation.
- **Deep Throat Ambient Occlusion**: The recessed throat naturally self-shadows, creating rich depth and color saturation.
- **Exact Coloration (Image 1)**:
  - **Throat**: Radiant electric lime-chartreuse star throat (`#D4E157` / `#CDDC39`).
  - **Midrib**: Fiery hot magenta / ruby-fuchsia ray (`#E91E63` / `#C2185B`).
  - **Throat Freckles**: Speckled deep velvet crimson papillae (`▪`, `#880E4F`).
  - **Body**: Soft glowing blush baby pink (`#F48FB1` / `#F8BBD0`).
  - **Margins & Tips**: Crisp snow-white wavy edges (`#FFFFFF`).
- **Floral Organs (Image 1 Anatomy)**:
  - **6 Stamen Filaments**: Slender pale lime-white filaments (`│`) arching outward and forward.
  - **6 Anthers**: Large, prominent dark chocolate / mahogany reddish-brown pollen sacs (`━`, `#4E342E` / `#5D4037`) poised atop the filaments.
  - **Pistil**: Central spring-green style topped with a swollen 3-lobed emerald stigma (`✦`, `#388E3C`).

### 4. Growth Lifecycle (Synced to 1-Minute "Golden Brown" starting at 21s)
1. **0.0s – 3.5s (Potted Soil & Green Sprouts)**: The two-tone pot sits solidly at the bottom; tender green shoot tips emerge from the dark soil.
2. **3.5s – 12.0s (Dense Foliage Unfurling)**: The 20 lanceolate leaves grow smoothly from the soil, draping over the rim and expanding into a thick, lush potted bush.
3. **12.0s – 17.5s (Lily Stalks & Swelling Buds)**: Multiple flower stalks surge upward high above the green foliage; tapered spindle buds form and swell, blushing with soft pink streaks.
4. **17.5s – 25.0s (Grand Lily Bloom - Song Climax)**: At the musical climax, the 6 star tepals peel open and recurve backwards, revealing the lime throat, magenta midribs, crimson freckles, chocolate anthers, and emerald stigma!
5. **25.0s – 33.0s (Full Glory & Radiance)**: Fully expanded star lilies showcase their vivid hot magenta rays, lime green throat star, and delicate anthers.
6. **33.0s – 60.0s (Gentle Sway & 1-Minute Petal Cascade)**: The music continues playing the iconic harpsichord/vocal themes for the full 1 minute while mature petals gently detach in a staggered cascade and flutter to the pot base, with ambient background petals showering continuously until the gentle fadeout at 60s.

---

## 🚀 Quick Start

Run the simulation directly (plays the full 1-minute soundtrack):

```bash
python3 bloom.py
```

Or execute directly:

```bash
./bloom.py
```

### Options:

```bash
# Automatically loop animation and song every 1 minute
python3 bloom.py --loop

# Customize overall duration (e.g., 60 seconds)
python3 bloom.py --duration 60.0

# Keep music playing continuously through the full uncut track
python3 bloom.py --continuous-audio

# Top-Down perspective looking into the lily throats
python3 bloom.py --pov "TOP-DOWN"

# Lower Pot-Level perspective looking up
python3 bloom.py --pov "POT-LEVEL"

# Subtle natural camera breathing
python3 bloom.py --pov "GENTLE SWAY"

# Pure continuous block density shading (the pixelated style)
python3 bloom.py --mode shaded

# High-contrast vibrant color grading
python3 bloom.py --color vibrant
```

---

## 🎮 Interactive Controls

While running, interact live using your keyboard:

| Key | Action |
|---|---|
| **`Space`** | **Pause / Resume** (animation + audio) |
| **`p` / `P`** | **Cycle Camera POV** (`STEADY 3D` [Default - No 360° spin], `GENTLE SWAY`, `TOP-DOWN`, `POT-LEVEL`) |
| **`m` / `M`** | **Toggle Character Style** (`floral` [Default - non-pixelated ceramic pot], `shaded` [Solid block pixelated style], `botanical`, `density`, `matrix`, `running`) |
| **`c` / `C`** | **Cycle Color Palette** (`truecolor` [Default], `vibrant` [High-contrast saturated], `sakura`, `sunset`, `monochrome`) |
| **`w` / `W`** | **Cycle Wind Setting** (`CALM`, `BREEZY`, `SUBTLE`, `STILL`) |
| **`b` / `B`** | **Toggle Background Mode** (`off` [Default clean terminal], `dim`, `full`) |
| **`r` / `R`** | **Replay** animation and audio from the very beginning |
| **`[` / `]`** | Adjust audio synchronization offset (-50ms / +50ms) |
| **`q` / `ESC`** | **Quit** and restore terminal cleanly |
