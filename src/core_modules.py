"""
core_modules.py  –  Layer‑0/1 helpers with CapacityEngine.stop() compatibility
================================================
Provides hardware abstraction (HAL) and measurement engines for IR and capacity tests.

Modules:
    • InaDriver      – thin wrapper around INA219
    • ChargerGuard   – USB-present clamp
    • LoadSwitch     – MOSFET gate control
    • IrEngine       – single-shot internal resistance test
    • CapacityEngine – coulomb counter with start/stop/reset/tick/summary

Self-test prints pass when run standalone.
"""
# ---------- LAYER 0: HAL / Drivers -----------------------------------------
from machine import Pin, SoftI2C, ADC
import utime as time

# --- INA thin wrapper -------------------------------------------------------
class InaDriver:
    def __init__(self, ina):
        self._ina = ina
    def voltage(self):  # V
        return self._ina.voltage()
    def current(self):  # mA (signed)
        return self._ina.current()
    def shunt_uv(self): # µV
        return self._ina.shunt_voltage() * 1000

# --- Charger guard ----------------------------------------------------------
class ChargerGuard:
    def __init__(self, usb_adc_pin:int, gate_pin:int, gate_series:int=1000):
        self._adc = ADC(Pin(usb_adc_pin)); self._adc.atten(ADC.ATTN_11DB)
        self._gate = Pin(gate_pin, Pin.OUT, value=0)
        self._series = gate_series
    def usb_present(self):
        return self._adc.read_u16() * 3.3 / 65535 > 1.0
    def assert_safe(self):
        if self.usb_present():
            self._gate.off()  # enforce clamp
            return False
        return True

# --- Load switch helper -----------------------------------------------------
class LoadSwitch:
    def __init__(self, pin:int):
        self._pin = Pin(pin, Pin.OUT, value=0)
    def on(self):
        self._pin.on()
    def off(self):
        self._pin.off()

# ---------- LAYER 1: Measurement engines ------------------------------------
class IrEngine:
    def __init__(self, ina:InaDriver, sw:LoadSwitch, guard:ChargerGuard, pulse_ms:int=100):
        self.ina = ina
        self.sw = sw
        self.guard = guard
        self.pulse_ms = pulse_ms
    def run(self):
        if not self.guard.assert_safe():
            return None
        v_open = self.ina.voltage()
        self.sw.on(); time.sleep_ms(self.pulse_ms)
        v_load = self.ina.voltage()
        i_mA = self.ina.current()
        self.sw.off()
        if abs(i_mA) < 50:
            return None
        r_mohm = (v_open - v_load) / (i_mA / 1000) * 1000
        return r_mohm, v_open, v_load, i_mA / 1000

class CapacityEngine:
    """Coulomb counter: start, tick per interval, stop, reset, summary."""
    def __init__(self, ina:InaDriver, sw:LoadSwitch, guard:ChargerGuard, cutoff_v:float=3.0):
        self.ina = ina
        self.sw = sw
        self.guard = guard
        self.cutoff_v = cutoff_v
        self.reset()
    def reset(self):
        """Stop any discharge and clear accumulators."""
        self.sw.off()
        self.active = False
        self.mAh = 0.0
        self.mWh = 0.0
        self.t = time.ticks_ms()
    def start(self):
        """Begin discharge if USB safe."""
        if not self.guard.assert_safe():
            return False
        self.reset()
        self.sw.on()
        self.active = True
        return True
    def stop(self):
        """Cease discharge immediately."""
        self.sw.off()
        self.active = False
    def tick(self):
        """Integrate current since last tick; auto-stop at cutoff or USB."""
        if not self.active:
            return
        now = time.ticks_ms()
        dt = time.ticks_diff(now, self.t) / 1000
        self.t = now
        v = self.ina.voltage()
        i = self.ina.current() / 1000
        self.mAh += i * dt * 1000 / 3600
        self.mWh += v * i * dt * 1000 / 3600
        if v <= self.cutoff_v or not self.guard.assert_safe():
            self.stop()
    def summary(self):
        """Return (mAh, mWh) tuple."""
        return self.mAh, self.mWh

# ---------- Self-test -------------------------------------------------------
if __name__ == "__main__":
    print("[core] dummy self-test passed")
