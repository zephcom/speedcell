from machine import Pin, SoftI2C
import utime as time
from ina219 import INA219
from encoder import Encoder
from core_modules import InaDriver, ChargerGuard, LoadSwitch, IrEngine, CapacityEngine
import ui_oled as ui

DEBUG = True

SDA_PIN, SCL_PIN = 8, 9
GATE_PIN = 0
USB_ADC_PIN = 3
ENC_CLK, ENC_DT, ENC_SW = 7, 6, 5
PULSE_COUNT = 10
OVER_CURRENT_A = 3.0

i2c = SoftI2C(scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400_000)
ui.init(i2c)
ui.clear_body()

ina_raw = INA219(0.1, i2c, max_expected_amps=3)
ina_raw.configure(voltage_range=ina_raw.RANGE_16V,
                  gain=ina_raw.GAIN_8_320MV,
                  bus_adc=ina_raw.ADC_8SAMP,
                  shunt_adc=ina_raw.ADC_8SAMP)
ina = InaDriver(ina_raw)

guard = ChargerGuard(usb_adc_pin=USB_ADC_PIN, gate_pin=GATE_PIN)
lswitch = LoadSwitch(pin=GATE_PIN)
ir = IrEngine(ina, lswitch, guard)
cap = CapacityEngine(ina, lswitch, guard)
enc = Encoder(clk=ENC_CLK, dt=ENC_DT, sw=ENC_SW)

MENU = ["IR pulse", "Capacity"]
menu_idx = 0
state = "IDLE"

IR_PAUSE_MS = 150
CAP_INTERVAL_MS = 1000
HEADER_INTERVAL_MS = 200
last_cap_ms = time.ticks_ms()
last_header_ms = time.ticks_ms()
last_res_ms = time.ticks_ms()

shots = 0
results = []
metric_idx = 0
METRIC_NAMES = ["MIN", "MAX", "AVG"]


def draw_menu():
    ui.clear_body()
    for i, label in enumerate(MENU):
        prefix = ">" if i == menu_idx else " "
        ui.oled.text(prefix + label, 8, 20 + i * 10)
    ui.oled.show()


def show_ir_shot(n, total, r):
    ui.clear_body()
    ui.oled.text(f"IR shot {n}/{total}", 0, 20)
    ui.oled.text(f"R {r:.0f} mOhm", 0, 30)
    ui.oled.show()


def show_ir_result(metric, val):
    ui.clear_body()
    ui.oled.text("IR results", 0, 20)
    ui.oled.text(f"{metric} {val:.0f} mOhm", 0, 35)
    ui.oled.show()


def show_cap(v, i, mAh, mWh):
    ui.clear_body()
    ui.oled.text("CAP", 0, 20)
    ui.oled.text(f"V {v:.2f} I {i:.2f}", 0, 30)
    ui.oled.text(f"{mAh:.0f}mAh", 0, 40)
    ui.oled.text(f"{mWh:.0f}mWh", 0, 50)
    ui.oled.show()


draw_menu()

while True:
    now = time.ticks_ms()

    # --- Charger guard ------------------------------------------------
    if guard.usb_present():
        if state != "CHG":
            state = "CHG"
            ui.clear_body()
        # live header still updates below even in CHG state
    elif state == "CHG":
        state = "IDLE"
        draw_menu()

    # --- Encoder delta -------------------------------------------------
    d_raw = enc.delta()
    step = 1 if d_raw >= 2 else -1 if d_raw <= -2 else 0

    if state == "IDLE" and step:
        menu_idx = (menu_idx + step) % len(MENU)
        draw_menu()
    elif state == "RES" and step and results:
        metric_idx = (metric_idx + step) % 3
        if metric_idx == 0:
            val = min(results)
        elif metric_idx == 1:
            val = max(results)
        else:
            val = sum(results) / len(results)
        show_ir_result(METRIC_NAMES[metric_idx], val)

    # --- Click actions -------------------------------------------------
    if enc.clicked():
        if state == "IDLE":
            if menu_idx == 0:
                state = "IR"; results = []; shots = 0
            else:
                state = "CAP"; cap.start(); last_cap_ms = now
        elif state == "CAP" and cap.active:
            cap.stop(); state = "IDLE"; draw_menu()
        elif state == "RES":
            state = "IDLE"; draw_menu()

    # --- Safety cut ----------------------------------------------------
    inst_I = ina.current() / 1000
    if abs(inst_I) > OVER_CURRENT_A:
        lswitch.off(); cap.stop(); state = "IDLE"; draw_menu()
        if DEBUG: print("Over-current trip")
        time.sleep_ms(500)
        continue

    # --- IR mode -------------------------------------------------------
    if state == "IR":
        res = ir.run()
        if res:
            r, _, _, _ = res
            shots += 1; results.append(r)
            show_ir_shot(shots, PULSE_COUNT, r)
            if DEBUG: print(f"Shot {shots}/{PULSE_COUNT} R={r:.0f}mOhm")
            time.sleep_ms(IR_PAUSE_MS)
        if shots >= PULSE_COUNT:
            state = "RES" if results else "IDLE"
            if results:
                val = sum(results) / len(results)
                metric_idx = 2; show_ir_result("AVG", val)
            else:
                draw_menu()

    # --- Capacity mode -------------------------------------------------
    if state == "CAP" and cap.active:
        if time.ticks_diff(now, last_cap_ms) >= CAP_INTERVAL_MS:
            last_cap_ms = now
            cap.tick(); v = ina.voltage(); i = ina.current() / 1000
            show_cap(v, i, cap.mAh, cap.mWh)
            if DEBUG: print(f"CAP {cap.mAh:.0f}mAh")
        if not cap.active:
            state = "IDLE"; draw_menu()

    # --- Header update (after state changes) ---------------------------
    if time.ticks_diff(now, last_header_ms) >= HEADER_INTERVAL_MS:
        last_header_ms = now
        v_live = ina.voltage(); i_live = ina.current() / 1000
        ui.show_live(state, v_live, i_live)
        if DEBUG: print(f"LIVE {state} V={v_live:.2f}V I={i_live:.2f}A")

    time.sleep_ms(100)
