class Pin:
    IN = 0
    OUT = 1
    PULL_UP = 2
    IRQ_RISING = 1
    IRQ_FALLING = 2

    def __init__(self, id, mode=-1, pull=None, value=0):
        self.id = id
        self.mode = mode
        self.pull = pull
        self._value = value
        self._irq_handler = None
        print(f"[stub] Pin({id}, mode={mode}, pull={pull}, value={value})")

    def value(self, val=None):
        if val is None:
            print(f"[stub] Pin{self.id}.value() -> {self._value}")
            return self._value
        self._value = val
        print(f"[stub] Pin{self.id}.value({val})")

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def irq(self, handler=None, trigger=None):
        self._irq_handler = handler
        print(f"[stub] Pin{self.id}.irq(trigger={trigger})")

class SoftI2C:
    def __init__(self, scl=None, sda=None, freq=400000):
        self.scl = scl
        self.sda = sda
        self.freq = freq
        print(f"[stub] SoftI2C init scl={scl} sda={sda} freq={freq}")

    def writeto(self, addr, buf):
        print(f"[stub] I2C.writeto(addr=0x{addr:02X}, len={len(buf)})")

    def writevto(self, addr, vec):
        total = sum(len(b) for b in vec)
        print(f"[stub] I2C.writevto(addr=0x{addr:02X}, total_len={total})")

    def writeto_mem(self, addr, memaddr, data):
        print(f"[stub] I2C.writeto_mem(addr=0x{addr:02X}, memaddr=0x{memaddr:02X}, len={len(data)})")

    def readfrom_mem(self, addr, memaddr, n):
        print(f"[stub] I2C.readfrom_mem(addr=0x{addr:02X}, memaddr=0x{memaddr:02X}, n={n})")
        return bytes([0]*n)

class ADC:
    ATTN_11DB = 0

    def __init__(self, pin):
        self.pin = pin
        print(f"[stub] ADC({pin})")

    def atten(self, val):
        print(f"[stub] ADC.atten({val})")

    def read_u16(self):
        print("[stub] ADC.read_u16() -> 0")
        return 0
