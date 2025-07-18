"""
ui_oled.py – Bi‑colour SSD1306 backend (body helpers added)
===========================================================
Yellow header (rows 0‑19) still shows live **state / V / I**.
Blue body (rows 20‑63) now supports:

    • show_menu(items, idx)          – idle menu with arrow →
    • show_ir_shot(n, total, r_mohm) – live IR pulse feedback
    • show_ir_result(metric, value)  – MIN / MAX / AVG viewer
    • show_cap(v, i, mAh, mWh)       – 1 s capacity ticker

All helpers call `clear_body()` first and draw a subtle 1‑pixel border for
extra style. No core logic touches the display; main.py decides when to call
these.
"""
from machine import SoftI2C
from ssd1306 import SSD1306_I2C

WIDTH, HEIGHT = 128, 64
HEADER_H      = 20   # rows 0‑19 (yellow)
BODY_Y        = 20   # blue starts here

oled: SSD1306_I2C | None = None

# ────────────────── init & basic helpers ──────────────────

def init(i2c: SoftI2C, addr: int = 0x3C):
    global oled
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=addr)
    oled.fill(0)
    oled.show()


def clear_body():
    if oled:
        oled.fill_rect(0, BODY_Y, WIDTH, HEIGHT - BODY_Y, 0)
        oled.show()


def _box():
    """Draw a 1‑px rectangle around blue area for style."""
    if not oled:
        return
    # top & bottom lines
    for x in range(WIDTH):
        oled.pixel(x, BODY_Y, 1)
        oled.pixel(x, HEIGHT - 1, 1)
    # left & right
    for y in range(BODY_Y, HEIGHT):
        oled.pixel(0, y, 1)
        oled.pixel(WIDTH - 1, y, 1)

# ────────────────── header (unchanged) ───────────────────

def show_live(state: str, volts: float, amps: float):
    if not oled:
        return
    oled.fill_rect(0, 0, WIDTH, HEADER_H, 0)
    oled.text(state[:6], 0, 0)
    txt = f"{volts:>4.2f}V {amps:+.2f}A"
    oled.text(txt, WIDTH - len(txt) * 8, 0)
    oled.show()

# ────────────────── body screens ─────────────────────────

def show_menu(items: list[str], idx: int):
    """Idle menu – highlight current selection with arrow."""
    if not oled:
        return
    clear_body()
    _box()
    y = BODY_Y + 4
    for i, text in enumerate(items):
        prefix = "> " if i == idx else "  "
        oled.text(prefix + text, 4, y)
        y += 10
    oled.show()


def show_ir_shot(n: int, total: int, r_mohm: float):
    if not oled:
        return
    clear_body(); _box()
    oled.text(f"IR shot {n}/{total}", 4, BODY_Y + 6)
    oled.text(f"R = {r_mohm:.0f} mOhm", 4, BODY_Y + 18)
    oled.show()


def show_ir_result(metric: str, value: float):
    if not oled:
        return
    clear_body(); _box()
    oled.text("IR results", 4, BODY_Y + 4)
    oled.text(f"{metric}  {value:.0f} mOhm", 4, BODY_Y + 18)
    oled.text("click=exit", 4, BODY_Y + 30)
    oled.show()


def show_cap(volts: float, amps: float, mAh: float, mWh: float):
    if not oled:
        return
    clear_body(); _box()
    oled.text("CAP run", 4, BODY_Y + 4)
    oled.text(f"V {volts:.2f} I {amps:.2f}A", 4, BODY_Y + 16)
    oled.text(f"{mAh:.0f} mAh", 4, BODY_Y + 28)
    oled.text(f"{mWh:.0f} mWh", 4, BODY_Y + 38)
    oled.show()
