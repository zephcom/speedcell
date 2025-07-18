"""
encoder.py  –  Robust Quadrature Encoder helper (v2.2‑DEADBUG)
=========================================================
User here: it's not perfect but good enough
let's not get stuck at a damn knob...
"""

from machine import Pin
import utime as time
__all__ = ["Encoder"]

# Gray‑code state table (Ben Buxton)
_STATE_TAB = (
    0,  -1,   1,   0,
    1,   0,   0,  -1,
   -1,   0,   0,   1,
    0,   1,  -1,   0,
)

class Encoder:
    def __init__(self, clk:int, dt:int, sw:int,
                 pull=Pin.PULL_UP, hold_ms:int=600):
        self._clk = Pin(clk, Pin.IN, pull)
        self._dt  = Pin(dt,  Pin.IN, pull)
        self._sw  = Pin(sw,  Pin.IN, pull)

        self._delta = 0
        self._state = (self._clk.value() << 1) | self._dt.value()

        # button
        self._click = False; self._held=False; self._t_press=0; self._hold_ms=hold_ms

        # IRQs (note: order positional+keyword triggers TypeError in some ports)
        trig = Pin.IRQ_RISING | Pin.IRQ_FALLING
        # IRQ wiring (MicroPython arg order: handler first, trigger kw‑only)
        self._clk.irq(handler=self._rot_irq, trigger=trig)
        self._dt .irq(handler=self._rot_irq, trigger=trig)
        self._sw .irq(handler=self._sw_irq, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

    # ---------- IRQ handlers -------------------------------------
    def _rot_irq(self, pin):
        s_prev = self._state
        s = ((s_prev << 2) | (self._clk.value()<<1) | self._dt.value()) & 0x0F
        step = _STATE_TAB[s]
        if step:
            self._delta += step
        self._state = s & 0x03

    def _sw_irq(self, pin):
        now = time.ticks_ms()
        if not pin.value():
            self._t_press = now
        else:
            dt = time.ticks_diff(now, self._t_press)
            if dt < self._hold_ms:
                self._click = True
            else:
                self._held = True

    # ---------- Public API ---------------------------------------
    def delta(self):
        d = self._delta
        self._delta = 0
        return d

    def clicked(self):
        c = self._click
        self._click = False
        return c

    def held(self, ms:int=None):
        if ms:
            self._hold_ms = ms
        h = self._held
        self._held = False
        return h
        