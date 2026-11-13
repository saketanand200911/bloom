#!/usr/bin/env python3
"""
Terminal 3D Potted Plant & Lily Blooming Simulation with Steady POV & Synced Audio
==================================================================================
A high-fidelity botanical 3D simulation in ASCII/Unicode terminal art featuring:
- A modern two-tone ceramic planter modeled directly on Image 2:
  * Non-pixelated sleek ceramic character styling in character/botanical modes
    (smooth porcelain lines ━, ─, ┄ for white band; turned bamboo ribbing ═, ━, ─, ┈ for base)
  * Solid density block styling (█, ▓, ▒, ░) retained exclusively in shaded mode
  * Realistic 3D cylindrical lighting with specular ceramic gloss & ambient occlusion
  * Foliage canopy cast shadow cast realistically across the pot rim and body
  * Subtle ground contact shadow grounding the planter
- A dense, lush potted plant (Peace Lily habit) growing from scratch:
  * 20 broad arching lanceolate leaves across 3 distinct tiers
  * Realistic leaf normals with transverse V-gutter shading
  * Pale spring-green midrib veins running down each leaf
  * Multi-layer shadow casting (upper leaves shadow lower leaves)
- Multiple magnificent Pink Hybrid Lilies modeled directly on Image 1:
  * Sturdy upright stalks pushing high above the dense foliage
  * Swelling tapered spindle buds blushing with color
  * 6 recurved star-shaped tepals (3 inner + 3 outer) opening tier-by-tier
  * Deep throat self-shadowing & ambient occlusion
  * Woven delicately from the falling flower glyphs (❀, ✿, ❁, ✽, ✾)
  * Vibrant chartreuse / lime-yellow star throat
  * Intense hot magenta / ruby-fuchsia midrib rays
  * Speckled dark crimson papillae / throat freckles
  * Soft glowing blush-pink body fading to crisp snow-white wavy margins & tips
  * 6 arching filaments topped with prominent dark chocolate / mahogany anthers (━)
  * Single central pale-green style with a 3-lobed emerald stigma (✦)
- Upright steady 3D perspective (+Y is UP, NO 360° spinning) keeping the view clean,
  stable, and focused on botanical growth.
- Continuous 3D span interpolation eliminating all vertical barcode striations and pixelation.
- Default clean terminal background with gentle ambient falling petals drifting in the breeze.
- Synced audio from "Golden Brown" (starting at 21s) using native macOS afplay.
"""

import sys
import os
import time
import math
import random
import signal
import shutil
import argparse
import subprocess

try:
    import select
except ImportError:
    select = None

try:
    import termios
    import tty
except ImportError:
    termios = None
    tty = None

try:
    import msvcrt
except ImportError:
    msvcrt = None

try:
    import winsound
except ImportError:
    winsound = None

# ---------------------------------------------------------------------------
# Character & Style Palettes
# ---------------------------------------------------------------------------
MODES = ["floral", "shaded", "botanical", "density", "matrix", "running"]
COLOR_MODES = ["truecolor", "vibrant", "sakura", "sunset", "monochrome"]
BG_MODES = ["off", "dim", "full"]
POV_MODES = ["STEADY 3D", "GENTLE SWAY", "TOP-DOWN", "POT-LEVEL"]

FLORAL_GLYPHS = ["❀", "✿", "❁", "✽", "✾"]

# ---------------------------------------------------------------------------
# Audio Player
# ---------------------------------------------------------------------------
class AudioPlayer:
    """Manages audio playback using native macOS afplay, Linux aplay/paplay, Windows winsound, or ffplay/mpv."""

    def __init__(self, audio_path, volume=1.0):
        self.audio_path = audio_path
        self.volume = volume
        self.proc = None
        self.is_paused = False

    def start(self):
        self.stop()
        if not self.audio_path or not os.path.exists(self.audio_path):
            return

        cmd = None
        if shutil.which("afplay"):
            cmd = ["afplay", "-v", str(self.volume), self.audio_path]
        elif shutil.which("ffplay"):
            cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", self.audio_path]
        elif shutil.which("mpv"):
            cmd = ["mpv", "--no-video", "--really-quiet", self.audio_path]
        elif shutil.which("aplay") and self.audio_path.endswith(".wav"):
            cmd = ["aplay", "-q", self.audio_path]
        elif shutil.which("paplay") and self.audio_path.endswith(".wav"):
            cmd = ["paplay", self.audio_path]

        if cmd:
            try:
                self.proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                self.proc = None
        elif winsound and self.audio_path.endswith(".wav"):
            try:
                winsound.PlaySound(self.audio_path, winsound.SND_ASYNC | winsound.SND_FILENAME)
            except Exception:
                pass

    def pause(self):
        if self.proc and self.proc.poll() is None and not self.is_paused:
            try:
                self.proc.send_signal(signal.SIGSTOP)
                self.is_paused = True
            except Exception:
                pass

    def resume(self):
        if self.proc and self.proc.poll() is None and self.is_paused:
            try:
                self.proc.send_signal(signal.SIGCONT)
                self.is_paused = False
            except Exception:
                pass

    def stop(self):
        if self.proc:
            if self.proc.poll() is None:
                try:
                    self.proc.terminate()
                    self.proc.wait(timeout=0.2)
                except Exception:
                    try:
                        self.proc.kill()
                    except Exception:
                        pass
            self.proc = None
        if winsound:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
        self.is_paused = False

    def restart(self):
        self.stop()
        self.start()


def prepare_audio_assets():
    """Ensures audio_bloom.wav (60-second 1-minute cut) and audio_continuous.wav exist."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bloom_wav = os.path.join(script_dir, "audio_bloom.wav")
    cont_wav = os.path.join(script_dir, "audio_continuous.wav")
    raw_mp3 = os.path.join(script_dir, "Golden-Brown-X-SnapYT.mp3")

    # 1-Minute bloom audio: starts at 21s, ends at 81s (60s length) with gentle 2.5s fadeout
    rebuild_bloom = False
    if not os.path.exists(bloom_wav):
        rebuild_bloom = True
    elif os.path.getsize(bloom_wav) < 5_000_000:
        # File is older 25s cut (~4.4 MB); upgrade to 60s cut (~10.5 MB)
        rebuild_bloom = True

    if rebuild_bloom and os.path.exists(raw_mp3) and shutil.which("ffmpeg"):
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-ss", "21", "-to", "81.0", "-i", raw_mp3,
                 "-af", "afade=t=out:st=57.5:d=2.5", bloom_wav],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
            )
        except Exception:
            pass

    if not os.path.exists(cont_wav) and os.path.exists(raw_mp3) and shutil.which("ffmpeg"):
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-ss", "21", "-to", "112", "-i", raw_mp3,
                 "-af", "afade=t=out:st=89:d=2.0", cont_wav],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
            )
        except Exception:
            pass

    return bloom_wav, cont_wav


# ---------------------------------------------------------------------------
# Smooth Interpolation & Math Helpers
# ---------------------------------------------------------------------------
def smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0 + 1e-9)))
    return t * t * (3.0 - 2.0 * t)


def clamp(val, low, high):
    return max(low, min(high, val))


def vec_len(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]) + 1e-9


def vec_norm(v):
    l = vec_len(v)
    return (v[0]/l, v[1]/l, v[2]/l)


def vec_dot(u, v):
    return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]


def vec_cross(u, v):
    return (
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    )


# ---------------------------------------------------------------------------
# Steady 3D Camera (Upright +Y, NO 360° spinning)
# ---------------------------------------------------------------------------
class SteadyCamera3D:
    """Steady 3D perspective camera focused on upright botanical plant growth."""

    def __init__(self, fov=48.0):
        self.fov = fov
        self.pos = [0.0, 9.5, -27.0]
        self.target = [0.0, 8.2, 0.0]
        self.cur_pos = list(self.pos)
        self.cur_target = list(self.target)

    def set_pov(self, mode_name, t):
        if mode_name == "STEADY 3D":
            self.target = [0.0, 8.2, 0.0]
            self.pos = [0.0, 9.5, -27.0]

        elif mode_name == "GENTLE SWAY":
            sway_x = math.sin(t * 0.35) * 1.1
            sway_y = math.cos(t * 0.25) * 0.4
            self.target = [0.0, 8.2, 0.0]
            self.pos = [sway_x, 9.5 + sway_y, -27.0]

        elif mode_name == "TOP-DOWN":
            self.target = [0.0, 8.5, 0.0]
            self.pos = [0.0, 18.0, -18.0]

        elif mode_name == "POT-LEVEL":
            self.target = [0.0, 9.0, 0.0]
            self.pos = [0.0, 5.0, -23.0]

        lerp_rate = 0.25
        for i in range(3):
            self.cur_pos[i] += (self.pos[i] - self.cur_pos[i]) * lerp_rate
            self.cur_target[i] += (self.target[i] - self.cur_target[i]) * lerp_rate

    def get_view_axes(self):
        fx = self.cur_target[0] - self.cur_pos[0]
        fy = self.cur_target[1] - self.cur_pos[1]
        fz = self.cur_target[2] - self.cur_pos[2]
        F = vec_norm((fx, fy, fz))

        W_up = (0.0, 1.0, 0.0)
        R = vec_norm(vec_cross(W_up, F))
        U = vec_norm(vec_cross(F, R))

        return R, U, F

    def project(self, p, screen_w, screen_h, font_aspect=0.5):
        R, U, F = self.get_view_axes()
        dx = p[0] - self.cur_pos[0]
        dy = p[1] - self.cur_pos[1]
        dz = p[2] - self.cur_pos[2]

        xc = dx * R[0] + dy * R[1] + dz * R[2]
        yc = dx * U[0] + dy * U[1] + dz * U[2]
        zc = dx * F[0] + dy * F[1] + dz * F[2]

        if zc < 0.8:
            return None

        scale_y = (screen_h * 0.5) / math.tan(math.radians(self.fov * 0.5))
        scale_x = scale_y / font_aspect

        sx = int(round((screen_w * 0.5) + (xc / zc) * scale_x))
        sy = int(round((screen_h * 0.5) - (yc / zc) * scale_y))

        return sx, sy, zc


# ---------------------------------------------------------------------------
# 3D Falling Background Petals Particle System
# ---------------------------------------------------------------------------
class FallingBackgroundPetal:
    """A floating petal fragment drifting through ambient background space."""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.phase = 0.0
        self.freq = 1.0
        self.is_pink = True
        self.alpha = 1.0
        self.glyph = "❀"
        self.reset(randomize_y=True)

    def reset(self, randomize_y=False):
        self.x = random.uniform(-18.0, 18.0)
        self.y = random.uniform(1.0, 22.0) if randomize_y else random.uniform(20.0, 24.0)
        self.z = random.uniform(-14.0, 14.0)
        self.vy = random.uniform(0.35, 0.65)
        self.vx = random.uniform(-0.15, 0.15)
        self.vz = random.uniform(-0.12, 0.12)
        self.phase = random.uniform(0, 2 * math.pi)
        self.freq = random.uniform(1.0, 2.2)
        self.is_pink = (random.random() < 0.65)
        self.alpha = random.uniform(0.8, 1.0)
        self.glyph = random.choice(FLORAL_GLYPHS)

    def update(self, dt, wind_x, wind_z):
        self.phase += self.freq * dt
        wobble_x = math.sin(self.phase) * 0.45
        wobble_z = math.cos(self.phase * 1.2) * 0.45

        self.x += (self.vx + wind_x * 0.3 + wobble_x) * dt * 20.0
        self.y -= self.vy * dt * 20.0
        self.z += (self.vz + wind_z * 0.3 + wobble_z) * dt * 20.0

        if self.y <= 0.4 or abs(self.x) > 22.0 or abs(self.z) > 22.0:
            self.reset(randomize_y=False)


# ---------------------------------------------------------------------------
# Shedding Lily Petal (Detaching after full bloom)
# ---------------------------------------------------------------------------
class SheddingLilyPetal:
    """A mature lily petal that detaches after full bloom and flutters down."""

    def __init__(self, flower_idx, detach_time, angle_offset, radius=3.2):
        self.flower_idx = flower_idx
        self.detach_time = detach_time
        self.angle_offset = angle_offset
        self.radius = radius
        self.drift_vx = random.uniform(-0.25, 0.25)
        self.drift_vz = random.uniform(-0.20, 0.20)
        self.wobble_phase = random.uniform(0, 2 * math.pi)
        self.settled_y = 1.0 + random.uniform(-0.2, 0.3)
        self.glyph = random.choice(FLORAL_GLYPHS)

    def get_pos(self, t, flower_head_pos):
        if t < self.detach_time:
            return None

        dt = t - self.detach_time
        hx, hy, hz = flower_head_pos

        descend_dist = dt * 1.6
        cur_y = max(self.settled_y, hy - descend_dist)

        wobble = math.sin(dt * 2.2 + self.wobble_phase) * 0.6
        cur_x = hx + math.cos(self.angle_offset) * self.radius + (self.drift_vx * dt * 2.5) + wobble
        cur_z = hz + math.sin(self.angle_offset) * self.radius + (self.drift_vz * dt * 2.5)

        return (cur_x, cur_y, cur_z)


# ---------------------------------------------------------------------------
# Individual Lily Flower Instance (Morphology & Anatomy matching Image 1)
# ---------------------------------------------------------------------------
class LilyFlowerInstance3D:
    """A single Pink Hybrid Lily matching Image 1."""

    def __init__(self, base_pos, head_pos, F_fl, U_fl, scale=1.0, t_offset=0.0):
        self.base_pos = base_pos
        self.target_head_pos = head_pos
        self.scale = scale
        self.t_offset = t_offset

        f_norm = vec_norm(F_fl)
        u_norm = vec_norm(U_fl)
        r_norm = vec_norm(vec_cross(u_norm, f_norm))
        u_ortho = vec_norm(vec_cross(f_norm, r_norm))

        self.F = f_norm
        self.U = u_ortho
        self.R = r_norm

    def get_growth_factors(self, t, bloom_duration=25.0):
        t_loc = t - self.t_offset
        stalk_g = smoothstep(8.5, 15.0, t_loc)
        bud_g = smoothstep(12.0, 17.5, t_loc)
        bloom_g = smoothstep(17.5, bloom_duration, t_loc)
        return stalk_g, bud_g, bloom_g

    def get_current_head(self, stalk_g, wind_x, wind_z):
        bx, by, bz = self.base_pos
        tx, ty, tz = self.target_head_pos

        flex = (stalk_g ** 1.6) * 1.2
        wx = wind_x * flex
        wz = wind_z * flex

        hx = bx + (tx - bx) * stalk_g + wx
        hy = by + (ty - by) * stalk_g
        hz = bz + (tz - bz) * stalk_g + wz
        return (hx, hy, hz)


# ---------------------------------------------------------------------------
# Complete Potted Plant & Lily 3D Scene (Images 1 & 2 Combined)
# ---------------------------------------------------------------------------
class PottedPlantLilyScene3D:
    """Manages the prominent two-tone ceramic planter, 20-leaf dense foliage,
    3-4 pink lilies, shadow casting, ambient occlusion, and falling petals."""

    def __init__(self, bloom_duration=25.0):
        self.bloom_duration = bloom_duration
        self.camera = SteadyCamera3D()
        self.pov_mode_idx = 0
        self.wind_setting = 0.8

        # 1. Multiple Lily Flowers (Image 1)
        self.flowers = [
            LilyFlowerInstance3D(
                base_pos=(0.0, 4.6, 0.0),
                head_pos=(0.0, 14.8, 0.2),
                F_fl=(0.0, -0.28, -0.96),
                U_fl=(0.0, 0.96, -0.28),
                scale=1.15,
                t_offset=0.0
            ),
            LilyFlowerInstance3D(
                base_pos=(-1.2, 4.6, 0.5),
                head_pos=(-5.8, 13.6, 1.2),
                F_fl=(0.35, -0.25, -0.90),
                U_fl=(-0.10, 0.96, -0.25),
                scale=0.96,
                t_offset=-0.4
            ),
            LilyFlowerInstance3D(
                base_pos=(1.4, 4.6, -0.3),
                head_pos=(5.6, 14.0, -0.6),
                F_fl=(-0.32, -0.26, -0.91),
                U_fl=(0.10, 0.95, -0.26),
                scale=1.00,
                t_offset=0.3
            ),
            LilyFlowerInstance3D(
                base_pos=(-0.6, 4.6, -1.2),
                head_pos=(-2.4, 11.2, -2.4),
                F_fl=(0.20, -0.20, -0.95),
                U_fl=(-0.05, 0.97, -0.20),
                scale=0.82,
                t_offset=0.8
            )
        ]

        # 2. Dense Foliage Leaves (Peace Lily habit in Image 2)
        # Leaves start at soil y=4.6, drape over rim y=4.8
        self.leaves_def = [
            # Tier 1: Cascading over pot rim
            (-145, 8.8, 6.4, 3.8, 1.45, 1, 2.0),
            (-95,  8.4, 6.2, 3.6, 1.35, 1, 2.4),
            (-45,  9.0, 6.6, 4.0, 1.50, 1, 2.8),
            (15,   8.5, 6.3, 3.7, 1.40, 1, 3.2),
            (65,   8.8, 6.5, 3.9, 1.45, 1, 3.6),
            (125,  8.6, 6.4, 3.8, 1.35, 1, 4.0),
            (175,  8.2, 6.2, 3.6, 1.40, 1, 4.4),

            # Tier 2: Mid spreading broad glossy lanceolate leaves
            (-165, 10.8, 8.8, 6.8, 1.75, 2, 4.2),
            (-120, 11.2, 9.0, 7.0, 1.85, 2, 4.6),
            (-70,  11.0, 8.9, 6.9, 1.75, 2, 5.0),
            (-25,  11.4, 9.3, 7.3, 1.90, 2, 5.4),
            (30,   11.2, 9.1, 7.1, 1.80, 2, 5.8),
            (80,   10.8, 8.8, 6.8, 1.70, 2, 6.2),
            (135,  11.0, 8.9, 6.9, 1.80, 2, 6.6),

            # Tier 3: Upper tall upright canopy leaves
            (-80,  10.4, 12.0, 11.0, 1.65, 3, 6.0),
            (-30,  11.2, 12.6, 11.6, 1.75, 3, 6.5),
            (20,   11.0, 12.4, 11.4, 1.75, 3, 7.0),
            (75,   10.2, 11.8, 10.8, 1.65, 3, 7.5),
            (160,  10.0, 11.4, 10.4, 1.55, 3, 8.0),
            (-140,  9.8, 11.0, 10.0, 1.55, 3, 8.5),
        ]

        # 3. Background falling petals
        self.particles = [FallingBackgroundPetal() for _ in range(50)]

        # 4. Shedding lily petals (gracefully staggered across the full 1-minute song)
        self.shedding_petals = [
            SheddingLilyPetal(flower_idx=0, detach_time=25.5, angle_offset=0.3, radius=3.4),
            SheddingLilyPetal(flower_idx=1, detach_time=27.5, angle_offset=2.2, radius=3.0),
            SheddingLilyPetal(flower_idx=2, detach_time=29.5, angle_offset=4.3, radius=3.1),
            SheddingLilyPetal(flower_idx=0, detach_time=32.0, angle_offset=3.6, radius=3.5),
            SheddingLilyPetal(flower_idx=3, detach_time=34.5, angle_offset=1.4, radius=2.6),
            SheddingLilyPetal(flower_idx=1, detach_time=37.5, angle_offset=5.1, radius=2.9),
            SheddingLilyPetal(flower_idx=2, detach_time=40.5, angle_offset=0.9, radius=3.0),
            SheddingLilyPetal(flower_idx=0, detach_time=43.5, angle_offset=2.8, radius=3.3),
            SheddingLilyPetal(flower_idx=3, detach_time=46.5, angle_offset=4.8, radius=2.7),
            SheddingLilyPetal(flower_idx=1, detach_time=49.5, angle_offset=1.1, radius=3.1),
            SheddingLilyPetal(flower_idx=2, detach_time=52.5, angle_offset=3.2, radius=2.8),
            SheddingLilyPetal(flower_idx=0, detach_time=55.0, angle_offset=5.5, radius=3.4),
            SheddingLilyPetal(flower_idx=1, detach_time=57.0, angle_offset=0.7, radius=3.0),
        ]

    def cycle_pov(self):
        self.pov_mode_idx = (self.pov_mode_idx + 1) % len(POV_MODES)
        return POV_MODES[self.pov_mode_idx]

    def render(self, t, width, height, frame_idx, dt=0.033):
        pov_name = POV_MODES[self.pov_mode_idx]
        self.camera.set_pov(pov_name, t)

        w_time = t * 1.15
        wind_x = (math.sin(w_time) * 0.45 + math.sin(w_time * 2.1) * 0.20) * self.wind_setting
        wind_z = (math.cos(w_time * 0.8) * 0.35 + math.sin(w_time * 1.6) * 0.15) * self.wind_setting

        bloom_intensity = smoothstep(17.5, self.bloom_duration + 1.0, t)
        if bloom_intensity > 0.02:
            for p in self.particles:
                p.update(dt, wind_x, wind_z)

        # Key sunlight vector: warm sun from top-right-front
        L_sun = vec_norm((0.68, 1.25, -0.75))

        z_buf = {}
        grid = {}

        def plot_point_3d(sx, sy, depth, normal, base_rgb, tag, py_coord=0.0, shadow_att=1.0, is_glow=False, ch="❀"):
            if not (0 <= sx < width and 0 <= sy < height):
                return

            cur_depth = z_buf.get((sx, sy), float('inf'))
            if depth >= cur_depth:
                return

            if is_glow:
                r_lit, g_lit, b_lit = base_rgb
            else:
                N = normal if normal else (0.0, 1.0, 0.0)
                ndotl = max(0.0, vec_dot(N, L_sun))

                # Specular ceramic / leaf gloss
                V = vec_norm((self.camera.cur_pos[0], self.camera.cur_pos[1], self.camera.cur_pos[2]))
                H = vec_norm((L_sun[0] + V[0], L_sun[1] + V[1], L_sun[2] + V[2]))
                spec_power = 16 if "pot" in tag else 10
                spec_mult = 0.35 if "pot" in tag else 0.20
                spec = (max(0.0, vec_dot(N, H)) ** spec_power) * spec_mult * shadow_att

                # Ambient illumination (cool sky from above + warm ground fill)
                sky_amb = 0.30 * max(0.0, N[1] * 0.5 + 0.5)
                bounce_amb = 0.15 * max(0.0, -N[1] * 0.5 + 0.5)
                amb = sky_amb + bounce_amb

                total_light = ndotl * shadow_att + amb

                r_lit = clamp(base_rgb[0] * total_light + 255 * spec, 0, 255)
                g_lit = clamp(base_rgb[1] * total_light + 255 * spec, 0, 255)
                b_lit = clamp(base_rgb[2] * total_light + 255 * spec, 0, 255)

            # Atmospheric depth fog
            fog = clamp((depth - 18.0) / 32.0, 0.0, 0.40)
            fog_r, fog_g, fog_b = (18, 20, 28)
            r_final = int((1.0 - fog) * r_lit + fog * fog_r)
            g_final = int((1.0 - fog) * g_lit + fog * fog_g)
            b_final = int((1.0 - fog) * b_lit + fog * fog_b)

            lum = 0.299 * r_final + 0.587 * g_final + 0.114 * b_final
            z_buf[(sx, sy)] = depth
            grid[(sx, sy)] = (r_final, g_final, b_final, lum, depth, tag, ch, py_coord)

        def draw_span_3d(p0, p1, norm0, norm1, rgb0, rgb1, tag, ch_func, shadow_att=1.0, is_glow=False):
            proj0 = self.camera.project(p0, width, height)
            proj1 = self.camera.project(p1, width, height)
            if not proj0 and not proj1:
                return
            if not proj0: proj0 = proj1
            if not proj1: proj1 = proj0

            x0, y0, d0 = proj0
            x1, y1, d1 = proj1
            dist = max(abs(x1 - x0), abs(y1 - y0))
            steps = max(1, dist * 2)

            for s in range(steps + 1):
                f = s / steps
                sx = int(round(x0 + (x1 - x0) * f))
                sy = int(round(y0 + (y1 - y0) * f))
                sd = d0 + (d1 - d0) * f
                py_mid = p0[1] + (p1[1] - p0[1]) * f
                r = int(rgb0[0] + (rgb1[0] - rgb0[0]) * f)
                g = int(rgb0[1] + (rgb1[1] - rgb0[1]) * f)
                b = int(rgb0[2] + (rgb1[2] - rgb0[2]) * f)
                nx = norm0[0] + (norm1[0] - norm0[0]) * f
                ny = norm0[1] + (norm1[1] - norm0[1]) * f
                nz = norm0[2] + (norm1[2] - norm0[2]) * f
                norm = vec_norm((nx, ny, nz))
                ch = ch_func(sx, sy, f)
                plot_point_3d(sx, sy, sd, norm, (r, g, b), tag, py_coord=py_mid, shadow_att=shadow_att, is_glow=is_glow, ch=ch)

        # -------------------------------------------------------------------
        # 1. Ground Contact Shadow (Soft Elliptical Grounding under Pot)
        # -------------------------------------------------------------------
        for gr in range(1, 14):
            r_g = (gr / 13.0) * 4.8
            for ga in range(36):
                gang = ga * (2.0 * math.pi / 36)
                gx = math.cos(gang) * r_g * 1.15
                gz = math.sin(gang) * r_g * 0.75 - 0.3
                proj = self.camera.project((gx, 0.05, gz), width, height)
                if proj:
                    shadow_dark = int(35 * (1.0 - gr / 13.0))
                    plot_point_3d(
                        proj[0], proj[1], proj[2], (0.0, 1.0, 0.0),
                        (shadow_dark, shadow_dark, shadow_dark + 5),
                        "ground_shadow", py_coord=0.0, ch="·", is_glow=True
                    )

        # -------------------------------------------------------------------
        # 2. Render Two-Tone Ceramic Pot (Image 2 - Prominent, Fully Lit)
        # -------------------------------------------------------------------
        # Pot: base y=0.0 to rim y=4.8.
        # Upper band: white porcelain y in [3.2, 4.8].
        # Lower section: warm tan bamboo ribbed ceramic y in [0.0, 3.2].
        pot_base_y = 0.0
        pot_rim_y = 4.8
        pot_white_split_y = 3.2

        num_y_slices = max(42, int(height * 1.3))
        for yi in range(num_y_slices + 1):
            y_prog = yi / num_y_slices
            py = pot_base_y + y_prog * (pot_rim_y - pot_base_y)

            # Upward conical flare (radius 3.5 at base, 4.3 at rim)
            r_pot = 3.5 + y_prog * 0.70
            is_white_band = (py >= pot_white_split_y)

            rib_slope = 0.0
            if not is_white_band:
                rib = math.sin(py * 14.0) * 0.09
                r_pot += rib
                rib_slope = math.cos(py * 14.0) * 0.09 * 14.0

            num_arc_pts = 64
            row_pts = []
            for ai in range(num_arc_pts + 1):
                ang = -math.pi * 0.52 + (ai / num_arc_pts) * (math.pi * 1.04)
                px = math.cos(ang) * r_pot
                pz = math.sin(ang) * r_pot

                # True cylindrical surface normal with rib inclination
                nx = math.cos(ang)
                nz = math.sin(ang)
                ny = -rib_slope * 0.18 + 0.06
                norm = vec_norm((nx, ny, nz))

                if is_white_band:
                    # White porcelain ceramic
                    base_rgb = (252, 252, 255)
                    tag = "pot_white"
                else:
                    # Warm bamboo/sandstone tan with rib groove crevice self-shadowing
                    groove_dark = 1.0 - 0.18 * max(0.0, -math.sin(py * 14.0))
                    ridge_bright = 1.0 + 0.12 * max(0.0, math.sin(py * 14.0))
                    tan_r = int(215 * groove_dark * ridge_bright)
                    tan_g = int(172 * groove_dark * ridge_bright)
                    tan_b = int(135 * groove_dark * ridge_bright)
                    base_rgb = (clamp(tan_r, 0, 255), clamp(tan_g, 0, 255), clamp(tan_b, 0, 255))
                    tag = "pot_tan"

                # Foliage canopy cast shadow onto upper pot:
                if py > 2.8:
                    h_ratio = (py - 2.8) / 2.0
                    pot_shadow = 0.35 + 0.30 * (1.0 - h_ratio)
                    if px > 0.5:
                        pot_shadow += 0.25 * (px / 4.3)
                else:
                    # Lower pot catches warm direct sunlight on lit side
                    pot_shadow = 0.70 + 0.30 * max(0.0, px / 4.3)

                row_pts.append(((px, py, pz), norm, base_rgb, tag, pot_shadow))

            for i in range(len(row_pts) - 1):
                p0, n0, rgb0, tag0, sh0 = row_pts[i]
                p1, n1, rgb1, tag1, sh1 = row_pts[i+1]
                sh_avg = (sh0 + sh1) * 0.5
                # Non-pixelated character line styling default
                ch_f = lambda sx, sy, f: ("─" if is_white_band else "═")
                draw_span_3d(p0, p1, n0, n1, rgb0, rgb1, tag0, ch_f, shadow_att=sh_avg)

        # Potting soil surface at y=4.6
        soil_y = 4.6
        soil_rad = 3.9
        for sr in range(1, 14):
            r_s = (sr / 13.0) * soil_rad
            for sa in range(36):
                sang = sa * (2.0 * math.pi / 36)
                spx = math.cos(sang) * r_s
                spz = math.sin(sang) * r_s
                proj = self.camera.project((spx, soil_y, spz), width, height)
                if proj:
                    soil_dark = 0.45 + 0.35 * (sr / 13.0)
                    sr_c = int(45 * soil_dark)
                    sg_c = int(30 * soil_dark)
                    sb_c = int(20 * soil_dark)
                    plot_point_3d(
                        proj[0], proj[1], proj[2],
                        (0.0, 1.0, 0.0), (sr_c, sg_c, sb_c), "soil",
                        py_coord=soil_y, shadow_att=soil_dark, ch="•"
                    )

        # Early sprout stage (t < 3.5s)
        if t < 3.5:
            sprout_prog = smoothstep(1.0, 3.5, t)
            num_sprouts = 8
            for si in range(num_sprouts):
                sa = si * (2.0 * math.pi / num_sprouts) + 0.3
                sr = 1.4
                sx = math.cos(sa) * sr
                sz = math.sin(sa) * sr
                sh = sprout_prog * 2.0
                for sh_step in range(1, 6):
                    spy = soil_y + (sh_step / 5.0) * sh
                    proj = self.camera.project((sx, spy, sz), width, height)
                    if proj:
                        plot_point_3d(
                            proj[0], proj[1], proj[2], (0.0, 1.0, 0.0),
                            (102, 187, 106), "sprout", py_coord=spy, ch="│"
                        )

        # -------------------------------------------------------------------
        # 3. Render Dense Foliage (20 Leaves with Shadow Casting)
        # -------------------------------------------------------------------
        total_leaf_growth = 0.0

        for az_deg, max_len, peak_h, end_h, blade_w, tier, t_delay in self.leaves_def:
            leaf_g = smoothstep(t_delay, t_delay + 4.5, t)
            total_leaf_growth += leaf_g / len(self.leaves_def)

            if leaf_g <= 0.02:
                continue

            az = math.radians(az_deg)
            w_sway = wind_x * (0.4 if tier == 1 else 0.7)
            dir_x = math.cos(az) + w_sway * 0.15
            dir_z = math.sin(az) + wind_z * 0.10
            d_len = math.sqrt(dir_x * dir_x + dir_z * dir_z) + 1e-6
            dir_x /= d_len
            dir_z /= d_len

            perp_x = -dir_z
            perp_z = dir_x

            cur_leaf_len = max_len * leaf_g
            u_steps = 18
            v_steps = 7

            tier_shadow = 0.52 if tier == 1 else (0.80 if tier == 2 else 1.0)

            for ui in range(1, u_steps + 1):
                u = ui / u_steps
                arch_factor = math.sin(u * math.pi * 0.62)
                fall_factor = u ** 2.2
                cur_y = soil_y + (peak_h - soil_y) * arch_factor + (end_h - peak_h) * fall_factor
                cur_r = u * cur_leaf_len * math.cos(math.radians(15.0 if tier < 3 else 35.0))

                cx = dir_x * cur_r
                cy = cur_y
                cz = dir_z * cur_r

                if u < 0.22:
                    w_u = 0.20 * (u / 0.22) * leaf_g
                else:
                    w_u = blade_w * (math.sin((u - 0.22) / 0.78 * math.pi) ** 0.65) * leaf_g

                flower_shadow = 0.72 if (cur_y < 12.0 and cur_r < 4.5 and bloom_intensity > 0.3) else 1.0
                leaf_shadow = tier_shadow * flower_shadow

                row_pts = []
                for vi in range(v_steps):
                    norm_w = -1.0 + 2.0 * (vi / (v_steps - 1))
                    lat = norm_w * w_u
                    px = cx + perp_x * lat
                    py = cy - 0.14 * (1.0 - norm_w * norm_w)
                    pz = cz + perp_z * lat

                    nx = perp_x * norm_w * 0.35 + dir_x * 0.10
                    nz = perp_z * norm_w * 0.35 + dir_z * 0.10
                    ny = 0.90
                    norm = vec_norm((nx, ny, nz))

                    is_midrib = (abs(norm_w) < 0.22)
                    if is_midrib:
                        rgb = (145, 220, 148)
                    else:
                        rgb = (40, 125, 48) if tier >= 2 else (25, 95, 32)

                    row_pts.append(((px, py, pz), norm, rgb, is_midrib))

                for i in range(len(row_pts) - 1):
                    p_a, n_a, rgb_a, mid_a = row_pts[i]
                    p_b, n_b, rgb_b, mid_b = row_pts[i+1]
                    def make_leaf_glyph(sx, sy, f, ma=mid_a, mb=mid_b):
                        if ma and mb:
                            return "║"
                        return FLORAL_GLYPHS[(sx + sy) % len(FLORAL_GLYPHS)]

                    draw_span_3d(
                        p_a, p_b, n_a, n_b, rgb_a, rgb_b, "leaf",
                        make_leaf_glyph, shadow_att=leaf_shadow
                    )

        # -------------------------------------------------------------------
        # 4. Render Multiple Pink Lilies (Image 1 - Throat Ambient Occlusion)
        # -------------------------------------------------------------------
        avg_bloom = 0.0
        flower_heads = []

        for f_idx, fl in enumerate(self.flowers):
            stalk_g, bud_g, bloom_g = fl.get_growth_factors(t, self.bloom_duration)
            avg_bloom += bloom_g / len(self.flowers)

            # Stalk rising out of foliage
            if stalk_g > 0.02:
                head_p = fl.get_current_head(stalk_g, wind_x, wind_z)
                flower_heads.append(head_p)
                head_x, head_y, head_z = head_p

                bx, by, bz = fl.base_pos
                stem_steps = int(round(24 * stalk_g))
                for st in range(stem_steps + 1):
                    sp = st / (stem_steps + 1e-6)
                    s_flex = math.sin(sp * math.pi) * 0.25 * wind_x
                    sx = bx + (head_x - bx) * sp + s_flex
                    sy = by + (head_y - by) * sp
                    sz = bz + (head_z - bz) * sp

                    proj = self.camera.project((sx, sy, sz), width, height)
                    if proj:
                        plot_point_3d(
                            proj[0], proj[1], proj[2],
                            (0.0, 0.2, 1.0), (46, 125, 50),
                            "lily_stalk", py_coord=sy, ch="│"
                        )

            # Lily Flower Head (Bud to Magnificent Star Bloom)
            if bud_g > 0.02 and flower_heads:
                head_x, head_y, head_z = flower_heads[-1]
                fl_scale = fl.scale

                F_fl = fl.F
                U_fl = fl.U
                R_fl = fl.R

                # 6 RECURVED STAR TEPALS
                for t_idx in range(6):
                    is_inner = (t_idx % 2 == 1)
                    ang = t_idx * (math.pi / 3.0) + (0.08 if is_inner else 0.0)
                    p_len = (5.3 if is_inner else 4.8) * fl_scale
                    max_w = (1.90 if is_inner else 1.45) * fl_scale

                    p_dir_r = math.cos(ang)
                    p_dir_u = math.sin(ang)

                    dir_vec = (
                        p_dir_r * R_fl[0] + p_dir_u * U_fl[0],
                        p_dir_r * R_fl[1] + p_dir_u * U_fl[1],
                        p_dir_r * R_fl[2] + p_dir_u * U_fl[2]
                    )
                    side_vec = (
                        -p_dir_u * R_fl[0] + p_dir_r * U_fl[0],
                        -p_dir_u * R_fl[1] + p_dir_r * U_fl[1],
                        -p_dir_u * R_fl[2] + p_dir_r * U_fl[2]
                    )

                    u_steps = 18
                    v_steps = 8

                    if is_inner:
                        tepal_bloom = smoothstep(0.12, 1.0, bloom_g)
                    else:
                        tepal_bloom = smoothstep(0.0, 0.90, bloom_g)

                    for ui in range(1, u_steps + 1):
                        u = ui / u_steps

                        # Bud: spindle cone
                        bud_z = u * 3.6 * fl_scale
                        bud_r = (0.22 + 0.95 * math.sin(u * math.pi * 0.85)) * fl_scale

                        # Bloom: recurving 6-pointed star
                        open_r = u * p_len
                        open_z = (0.65 * math.sin(u * math.pi * 0.70) - 1.35 * (u ** 2.2)) * fl_scale

                        cur_r = (1.0 - tepal_bloom) * bud_r + tepal_bloom * open_r
                        cur_z = (1.0 - tepal_bloom) * bud_z + tepal_bloom * open_z

                        w_bud = bud_r * 0.45
                        w_open = max_w * (math.sin(u * math.pi) ** 0.65)
                        w_actual = (1.0 - tepal_bloom) * w_bud + tepal_bloom * w_open

                        throat_ao = 0.50 + 0.50 * smoothstep(0.0, 0.35, u)

                        row_pts = []
                        for vi in range(v_steps):
                            norm_w = -1.0 + 2.0 * (vi / (v_steps - 1))
                            lat = norm_w * w_actual
                            wave = 0.12 * math.sin(u * 16.0) * abs(norm_w) * fl_scale * tepal_bloom

                            px = head_x + dir_vec[0] * cur_r + side_vec[0] * lat + F_fl[0] * (cur_z + wave)
                            py = head_y + dir_vec[1] * cur_r + side_vec[1] * lat + F_fl[1] * (cur_z + wave)
                            pz = head_z + dir_vec[2] * cur_r + side_vec[2] * lat + F_fl[2] * (cur_z + wave)

                            if tepal_bloom < 0.10:
                                if u < 0.40:
                                    rgb = (76, 175, 80)
                                else:
                                    rgb = (200, 100, 130)
                                tag = "lily_bud"
                            else:
                                if u < 0.22:
                                    rgb = (215, 238, 55)  # Electric lime-chartreuse throat
                                    tag = "lily_throat"
                                elif abs(norm_w) < 0.25:
                                    rgb = (230, 25, 110)  # Fiery carmine-magenta midrib ray
                                    tag = "lily_midrib"
                                elif 0.20 <= u <= 0.58 and abs(norm_w) < 0.58 and (
                                    (int(u * 37) + int(abs(norm_w) * 23) + t_idx) % 4 == 0
                                ):
                                    rgb = (140, 10, 70)   # Deep velvet crimson freckles
                                    tag = "lily_freckles"
                                elif u > 0.82 or abs(norm_w) > 0.72:
                                    rgb = (255, 255, 255) # Pure snow-white edge/tip
                                    tag = "lily_white_edge"
                                else:
                                    rgb = (250, 160, 190) # Soft luminous blush pink
                                    tag = "lily_blush"

                            nx = dir_vec[0] * 0.45 + side_vec[0] * norm_w * 0.25 + F_fl[0] * 0.65
                            ny = dir_vec[1] * 0.45 + side_vec[1] * norm_w * 0.25 + F_fl[1] * 0.65
                            nz = dir_vec[2] * 0.45 + side_vec[2] * norm_w * 0.25 + F_fl[2] * 0.65
                            norm = vec_norm((nx, ny, nz))

                            row_pts.append(((px, py, pz), norm, rgb, tag))

                        for i in range(len(row_pts) - 1):
                            p_a, n_a, rgb_a, tag_a = row_pts[i]
                            p_b, n_b, rgb_b, tag_b = row_pts[i+1]
                            def make_petal_glyph(sx, sy, f, ui=ui, t_a=tag_a):
                                if t_a == "lily_throat":
                                    return "✿" if (sx + sy) % 2 == 0 else "✦"
                                elif t_a == "lily_freckles":
                                    return "▪"
                                return FLORAL_GLYPHS[(sx + sy + ui) % len(FLORAL_GLYPHS)]

                            draw_span_3d(
                                p_a, p_b, n_a, n_b, rgb_a, rgb_b, tag_a,
                                make_petal_glyph, shadow_att=throat_ao
                            )

                # --- 6 STAMEN FILAMENTS & CHOCOLATE ANTHERS ---
                if bloom_g > 0.18:
                    stamen_ext = smoothstep(0.18, 0.95, bloom_g)
                    for si in range(6):
                        s_ang = si * (math.pi / 3.0) + (math.pi / 6.0)
                        p_r = math.cos(s_ang)
                        p_u = math.sin(s_ang)

                        dir_s = (
                            p_r * R_fl[0] + p_u * U_fl[0],
                            p_r * R_fl[1] + p_u * U_fl[1],
                            p_r * R_fl[2] + p_u * U_fl[2]
                        )

                        for st in range(1, 8):
                            su = st / 7.0
                            sr = su * 2.4 * fl_scale * stamen_ext
                            sf = (su * 2.0 + 0.3) * fl_scale * stamen_ext

                            sx = head_x + dir_s[0] * sr + F_fl[0] * sf
                            sy = head_y + dir_s[1] * sr + F_fl[1] * sf
                            sz = head_z + dir_s[2] * sr + F_fl[2] * sf

                            proj = self.camera.project((sx, sy, sz), width, height)
                            if proj:
                                px, py, depth = proj
                                if st == 7:
                                    for ad in (-1, 0, 1):
                                        plot_point_3d(
                                            px + ad, py, depth - 0.15, (0.0, 1.0, 0.0),
                                            (65, 38, 30), "anther", py_coord=sy, ch="━", is_glow=True
                                        )
                                else:
                                    plot_point_3d(
                                        px, py, depth - 0.05, (0.0, 1.0, 0.0),
                                        (215, 240, 205), "filament", py_coord=sy, ch="│"
                                    )

                # --- CENTRAL PISTIL (Style & 3-Lobed Stigma) ---
                if bloom_g > 0.15:
                    pistil_ext = smoothstep(0.15, 0.90, bloom_g)
                    for pt in range(1, 9):
                        pu = pt / 8.0
                        pr = pu * 0.60 * fl_scale * pistil_ext
                        pf = (pu * 3.0 + 0.35) * fl_scale * pistil_ext

                        px = head_x + U_fl[0] * pr + F_fl[0] * pf
                        py = head_y + U_fl[1] * pr + F_fl[1] * pf
                        pz = head_z + U_fl[2] * pr + F_fl[2] * pf

                        proj = self.camera.project((px, py, pz), width, height)
                        if proj:
                            sx, sy, depth = proj
                            if pt == 8:
                                plot_point_3d(
                                    sx, sy, depth - 0.15, (0.0, 1.0, 0.0),
                                    (56, 142, 60), "stigma", py_coord=py, ch="✦", is_glow=True
                                )
                            else:
                                plot_point_3d(
                                    sx, sy, depth - 0.05, (0.0, 1.0, 0.0),
                                    (145, 220, 148), "style", py_coord=py, ch="│"
                                )

        # -------------------------------------------------------------------
        # 5. Render Shedding Petals
        # -------------------------------------------------------------------
        if t >= 25.5 and flower_heads:
            for sp in self.shedding_petals:
                f_idx = min(len(flower_heads) - 1, sp.flower_idx)
                f_head = flower_heads[f_idx]
                pos = sp.get_pos(t, f_head)
                if pos:
                    sp_x, sp_y, sp_z = pos
                    proj = self.camera.project((sp_x, sp_y, sp_z), width, height)
                    if proj:
                        px, py, depth = proj
                        for ad in (-1, 0, 1):
                            plot_point_3d(
                                px + ad, py, depth, (0.0, 1.0, 0.0),
                                (248, 155, 185), "shedding_petal", py_coord=sp_y, ch=sp.glyph
                            )

        # -------------------------------------------------------------------
        # 6. Render 3D Falling Background Petals Shower
        # -------------------------------------------------------------------
        if bloom_intensity > 0.02:
            for p in self.particles:
                if p.y > 0.6:
                    rgb = (248, 155, 185) if p.is_pink else (145, 220, 148)
                    proj = self.camera.project((p.x, p.y, p.z), width, height)
                    if proj:
                        plot_point_3d(
                            proj[0], proj[1], proj[2], (0.0, 1.0, 0.0),
                            rgb, "petal_fall", py_coord=p.y, ch=p.glyph, is_glow=True
                        )

        return grid, avg_bloom, total_leaf_growth


# ---------------------------------------------------------------------------
# ANSI Frame Formatter: Non-Pixelated Ceramic Pot in Character Modes,
# Pixelated Density Blocks exclusively in Shaded Mode
# ---------------------------------------------------------------------------
def format_frame(grid, width, height, frame_idx, mode, color_mode, bg_mode):
    """Translates 3D grid cells into clean, vibrant ANSI string."""
    rows = []

    for y in range(height):
        row = []
        prev_color_code = None
        prev_r, prev_g, prev_b = -999, -999, -999

        for x in range(width):
            cell = grid.get((x, y))

            if cell is None:
                if bg_mode == "off":
                    row.append(" ")
                    prev_color_code = None
                    prev_r, prev_g, prev_b = -999, -999, -999
                    continue
                elif bg_mode == "dim":
                    if (x * 7 + y * 13) % 41 == 0:
                        ch = "·"
                        color_code = "\033[38;2;45;50;70m"
                    else:
                        row.append(" ")
                        prev_color_code = None
                        prev_r, prev_g, prev_b = -999, -999, -999
                        continue
                else:
                    ch = "·"
                    color_code = "\033[38;2;35;40;60m"

                if color_code != prev_color_code:
                    row.append(f"{color_code}{ch}")
                    prev_color_code = color_code
                else:
                    row.append(ch)
                continue

            r, g, b, lum, depth, tag, def_ch, py_coord = cell

            # Character selection based on mode:
            # ONLY 'shaded' is the pixelated block style!
            # In ALL other styles (floral, botanical, etc.), the pot is completely NON-PIXELATED!
            if mode == "shaded":
                # The Pixelated Style (pure solid density blocks):
                if "ground_shadow" in tag:
                    ch = "░"
                elif lum > 170:
                    ch = "█"
                elif lum > 115:
                    ch = "▓"
                elif lum > 65:
                    ch = "▒"
                else:
                    ch = "░"

            else:
                # Non-Pixelated Styles (floral, botanical, density, matrix, running):
                if "pot" in tag:
                    # Non-pixelated smooth ceramic lines following pottery grooves (Image 2):
                    if tag == "pot_white" or py_coord >= 3.2:
                        # Smooth porcelain ceramic upper band:
                        if lum > 175:
                            ch = "━"  # bright specular lip
                        elif lum > 120:
                            ch = "─"  # smooth porcelain face
                        else:
                            ch = "┄"  # soft porcelain shadow
                    else:
                        # Turned bamboo / sandstone ribbed ceramic base:
                        is_ridge = math.sin(py_coord * 14.0) > 0.0
                        if is_ridge:
                            if lum > 150:
                                ch = "═"  # bright lit ridge crest
                            elif lum > 100:
                                ch = "━"  # midtone ridge
                            else:
                                ch = "─"  # shadowed ridge
                        else:
                            if lum > 120:
                                ch = "─"  # lit groove
                            elif lum > 80:
                                ch = "┄"  # midtone groove
                            else:
                                ch = "┈"  # crevice shadow

                elif tag == "soil":
                    ch = "•" if lum > 25 else "·"

                elif tag == "ground_shadow":
                    ch = "·"

                elif mode == "floral":
                    ch = def_ch

                elif mode == "botanical":
                    if "leaf" in tag:
                        ch = "║" if "vein" in tag else "w"
                    elif "anther" in tag:
                        ch = "━"
                    elif tag == "stigma":
                        ch = "✦"
                    elif "lily" in tag:
                        ch = FLORAL_GLYPHS[(x + y) % len(FLORAL_GLYPHS)]
                    elif tag == "petal_fall":
                        ch = "❀"
                    else:
                        ch = "·"

                elif mode == "density":
                    ramp = " .:-=+*#%@"
                    idx = int(clamp(lum / 255.0, 0.0, 1.0) * (len(ramp) - 1))
                    ch = ramp[idx]

                elif mode == "matrix":
                    matrix_chars = "0123456789@#$&!?<>"
                    ch = matrix_chars[(x * 3 + y * 7) % len(matrix_chars)]

                else:  # running
                    keyboard = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-*/=%"
                    ch = keyboard[(x * 3 + y * 7 + frame_idx * 2) % len(keyboard)]

            # Color scheme transforms
            if color_mode == "truecolor":
                target_r, target_g, target_b = r, g, b
            elif color_mode == "vibrant":
                target_r = int(clamp((r - 120) * 1.30 + 130, 0, 255))
                target_g = int(clamp((g - 120) * 1.30 + 130, 0, 255))
                target_b = int(clamp((b - 120) * 1.30 + 130, 0, 255))
                if "lily" in tag:
                    target_r = int(clamp(target_r * 1.15, 0, 255))
                elif "leaf" in tag:
                    target_g = int(clamp(target_g * 1.15, 0, 255))
                elif "pot_tan" in tag:
                    target_r = int(clamp(target_r * 1.10, 0, 255))
                    target_g = int(clamp(target_g * 1.05, 0, 255))
            elif color_mode == "sakura":
                if "lily" in tag or tag == "shedding_petal":
                    target_r = int(clamp(r * 1.05, 230, 255))
                    target_g = int(clamp(g * 1.30, 175, 235))
                    target_b = int(clamp(b * 1.25, 210, 245))
                elif "leaf" in tag or tag in ("sprout", "lily_stalk", "style"):
                    target_r = int(clamp(r * 0.8, 35, 100))
                    target_g = int(clamp(g * 1.1, 140, 210))
                    target_b = int(clamp(b * 0.9, 80, 140))
                else:
                    target_r, target_g, target_b = r, g, b
            elif color_mode == "sunset":
                target_r = int(clamp(r * 1.25 + 15, 0, 255))
                target_g = int(clamp(g * 0.85 + 25, 0, 255))
                target_b = int(clamp(b * 0.55, 0, 255))
            elif color_mode == "monochrome":
                ilum = int(lum)
                target_r, target_g, target_b = ilum, ilum, ilum
            else:
                target_r, target_g, target_b = r, g, b

            diff = abs(target_r - prev_r) + abs(target_g - prev_g) + abs(target_b - prev_b)
            if diff < 14 and prev_color_code:
                color_code = prev_color_code
            else:
                color_code = f"\033[38;2;{target_r};{target_g};{target_b}m"
                prev_r, prev_g, prev_b = target_r, target_g, target_b

            if color_code != prev_color_code:
                row.append(f"{color_code}{ch}")
                prev_color_code = color_code
            else:
                row.append(ch)

        rows.append("".join(row))

    return "\n".join(rows) + "\033[0m"


# ---------------------------------------------------------------------------
# Main Orchestration Loop
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Terminal 3D Potted Plant & Lily Blooming Simulation with Steady POV & Synced Audio"
    )
    parser.add_argument(
        "--mode",
        choices=MODES,
        default="floral",
        help="Character mode (default: floral - non-pixelated ceramic pot & floral weave flowers)"
    )
    parser.add_argument(
        "--color",
        choices=COLOR_MODES,
        default="truecolor",
        help="Color scheme (default: truecolor)"
    )
    parser.add_argument(
        "--bg-mode",
        choices=BG_MODES,
        default="off",
        help="Background mode: off, dim, or full (default: off - clean default terminal)"
    )
    parser.add_argument(
        "--pov",
        choices=POV_MODES,
        default="STEADY 3D",
        help="3D Camera POV (default: STEADY 3D - fixed upright, no 360 rotation)"
    )
    parser.add_argument(
        "--audio-delay",
        type=float,
        default=0.0,
        help="Audio offset calibration in seconds (adjust live with [ and ])"
    )
    parser.add_argument(
        "--no-sound",
        action="store_true",
        help="Disable audio playback"
    )
    parser.add_argument(
        "--continuous-audio",
        action="store_true",
        help="Keep music playing continuously past the bloom stage into the shedding phase"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Target framerate (default: 30 FPS)"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=60.0,
        help="Total duration in seconds of the music and bloom animation (default: 60.0s = 1 minute)"
    )
    parser.add_argument(
        "--bloom-duration",
        type=float,
        default=25.0,
        help="Duration in seconds for the lilies to reach 100%% bloom (default: 25.0s)"
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Automatically loop animation and song when the 1 minute completes"
    )
    args = parser.parse_args()

    # Audio assets preparation
    bloom_wav, cont_wav = prepare_audio_assets()
    chosen_audio = cont_wav if args.continuous_audio else bloom_wav
    if not os.path.exists(chosen_audio):
        chosen_audio = bloom_wav if os.path.exists(bloom_wav) else "Golden-Brown-X-SnapYT.mp3"

    audio = AudioPlayer(chosen_audio) if not args.no_sound else None

    # State parameters
    mode_idx = MODES.index(args.mode)
    color_idx = COLOR_MODES.index(args.color)
    bg_idx = BG_MODES.index(args.bg_mode)
    audio_offset = args.audio_delay
    fps = max(15, min(60, args.fps))
    frame_interval = 1.0 / fps

    scene = PottedPlantLilyScene3D(bloom_duration=args.bloom_duration)
    scene.pov_mode_idx = POV_MODES.index(args.pov)

    # Enable ANSI terminal processing in Windows console
    if sys.platform == "win32":
        os.system("")

    # Terminal interactive setup
    is_interactive = sys.stdin.isatty() and sys.stdout.isatty()
    old_term_settings = None
    if is_interactive and termios and tty:
        fd = sys.stdin.fileno()
        try:
            old_term_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)
        except Exception:
            old_term_settings = None

    # Enter alternate screen buffer and hide cursor
    os.write(1, b"\033[?1049h\033[?25l\033[2J")

    def cleanup(sig=None, frame=None):
        if audio:
            audio.stop()
        if is_interactive and old_term_settings and termios:
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_term_settings)
            except Exception:
                pass
        try:
            os.write(1, b"\033[?1049l\033[?25h\033[0m")
        except Exception:
            pass
        if sig:
            sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        while True:
            for p in scene.particles:
                p.reset(randomize_y=True)
            if audio:
                audio.start()

            start_time = time.perf_counter()
            current_frame_idx = 0
            is_paused = False
            pause_start = 0.0
            total_paused_time = 0.0
            wind_levels = [0.8, 1.4, 0.3, 0.0]
            wind_names = ["CALM", "BREEZY", "SUBTLE", "STILL"]
            wind_idx = 0

            while True:
                # 1. Interactive Key Events
                key = None
                if is_interactive:
                    if msvcrt and msvcrt.kbhit():
                        try:
                            key = msvcrt.getch().decode("utf-8", errors="ignore")
                        except Exception:
                            key = None
                    elif select and select.select([sys.stdin], [], [], 0)[0]:
                        try:
                            key = sys.stdin.read(1)
                        except Exception:
                            key = None

                if key:
                    if key in ('q', 'Q', '\x1b'):
                        cleanup()
                        return
                    elif key == ' ':
                        is_paused = not is_paused
                        if is_paused:
                            pause_start = time.perf_counter()
                            if audio:
                                audio.pause()
                        else:
                            total_paused_time += time.perf_counter() - pause_start
                            if audio:
                                audio.resume()
                    elif key in ('p', 'P'):
                        scene.cycle_pov()
                    elif key in ('m', 'M'):
                        mode_idx = (mode_idx + 1) % len(MODES)
                    elif key in ('c', 'C'):
                        color_idx = (color_idx + 1) % len(COLOR_MODES)
                    elif key in ('b', 'B', "'"):
                        bg_idx = (bg_idx + 1) % len(BG_MODES)
                    elif key in ('w', 'W'):
                        wind_idx = (wind_idx + 1) % len(wind_levels)
                        scene.wind_setting = wind_levels[wind_idx]
                    elif key in ('[', '-'):
                        audio_offset -= 0.05
                    elif key in (']', '+', '='):
                        audio_offset += 0.05
                    elif key in ('r', 'R'):
                        break

                if is_paused:
                    time.sleep(0.02)
                    continue

                # 2. Master Clock Synchronization
                now = time.perf_counter()
                elapsed = (now - start_time) - total_paused_time - audio_offset

                if elapsed < 0:
                    time.sleep(0.005)
                    continue

                # Auto-loop support
                if args.loop and elapsed >= args.duration:
                    break

                target_frame = int(elapsed * fps)

                if target_frame >= current_frame_idx:
                    current_frame_idx += 1

                    cols, lines = shutil.get_terminal_size((80, 24))
                    render_w = cols
                    render_h = max(5, lines - 2)

                    grid, avg_bloom, leaf_g = scene.render(
                        elapsed, render_w, render_h, current_frame_idx, dt=frame_interval
                    )

                    curr_mode = MODES[mode_idx]
                    curr_color = COLOR_MODES[color_idx]
                    curr_bg = BG_MODES[bg_idx]
                    curr_pov = POV_MODES[scene.pov_mode_idx]

                    frame_str = format_frame(
                        grid, render_w, render_h, current_frame_idx,
                        curr_mode, curr_color, curr_bg
                    )

                    # Stage Lifecycle Status Label
                    if elapsed < 3.5:
                        phase_label = "🌱 [POTTED SOIL & GREEN SPROUTS EMERGING]"
                    elif elapsed < 12.0:
                        phase_label = f"🌿 [DENSE FOLIAGE UNFURLING & ARCHING OVER RIM {int(leaf_g*100)}%]"
                    elif elapsed < 17.5:
                        phase_label = "🌷 [LILY STALKS RISING & TAPERED BUDS SWELLING]"
                    elif elapsed < args.bloom_duration:
                        phase_label = f"🌸 [PINK STARGAZER LILIES BLOOMING {int(avg_bloom*100)}%]"
                    elif elapsed < args.bloom_duration + 8.0:
                        phase_label = "✨ [FULL BLOOM - MAGENTA MIDRIBS, LIME THROATS & CHOCOLATE ANTHERS]"
                    elif elapsed < args.duration:
                        phase_label = "🍃 [GENTLE BREEZE SWAY & FALLING PETAL CASCADE]"
                    else:
                        phase_label = "🌸 [1-MINUTE BLOOM COMPLETE - r: Replay | q: Quit]"

                    dur_min = int(args.duration // 60)
                    dur_sec = int(args.duration % 60)
                    disp_time = min(elapsed, args.duration) if not args.loop else elapsed
                    el_min = int(disp_time // 60)
                    el_sec = int(disp_time % 60)

                    status_bar_content = (
                        f" {phase_label} | [{curr_pov}] [{curr_mode.upper()}] [{curr_color.upper()}] "
                        f"{el_min:02d}:{el_sec:02d}/{dur_min:02d}:{dur_sec:02d} | "
                        f"Space: Pause | m: Style | c: Color | w: Wind | p: POV | r: Replay | q: Quit "
                    )
                    if len(status_bar_content) > cols:
                        status_bar_content = status_bar_content[:cols]
                    else:
                        status_bar_content = status_bar_content.ljust(cols)
                    status_bar = f"\033[7m{status_bar_content}\033[0m"

                    full_output = f"\033[H{frame_str}\n{status_bar}"
                    os.write(1, full_output.encode("utf-8", errors="replace"))

                else:
                    next_time = (current_frame_idx + 1) * frame_interval
                    rem = next_time - elapsed
                    if rem > 0.001:
                        time.sleep(min(rem, 0.01))

    finally:
        cleanup()


if __name__ == "__main__":
    main()
