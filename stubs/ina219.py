"""INA219 stub for unit tests and demos without hardware.

This module mimics the subset of the ``ina219`` driver used by this
project. It stores voltage, current and shunt readings which can be
updated via :py:meth:`set_values`.

Example::

    from ina219 import INA219
    ina = INA219(0.1)
    ina.configure()  # no-op in stub
    ina.set_values(voltage=4.2, current=150, shunt=5)
    print(ina.voltage(), ina.current(), ina.shunt_voltage())

To make ``import ina219`` resolve to this stub when running the
MicroPython binary, prefix ``MICROPYPATH`` with ``stubs``::

    MICROPYPATH=stubs:lib ./bin/micropython src/main.py
"""

# Constants used by ``src`` modules (values match the real driver)
RANGE_16V = 0
RANGE_32V = 1
GAIN_1_40MV = 0
GAIN_2_80MV = 1
GAIN_4_160MV = 2
GAIN_8_320MV = 3
GAIN_AUTO = -1
ADC_9BIT = 0
ADC_10BIT = 1
ADC_11BIT = 2
ADC_12BIT = 3
ADC_2SAMP = 9
ADC_4SAMP = 10
ADC_8SAMP = 11
ADC_16SAMP = 12
ADC_32SAMP = 13
ADC_64SAMP = 14
ADC_128SAMP = 15

class INA219:
    """Very small emulation of :class:`ina219.INA219`."""

    # expose constants as class attributes like the real driver
    RANGE_16V = RANGE_16V
    RANGE_32V = RANGE_32V
    GAIN_1_40MV = GAIN_1_40MV
    GAIN_2_80MV = GAIN_2_80MV
    GAIN_4_160MV = GAIN_4_160MV
    GAIN_8_320MV = GAIN_8_320MV
    GAIN_AUTO = GAIN_AUTO
    ADC_9BIT = ADC_9BIT
    ADC_10BIT = ADC_10BIT
    ADC_11BIT = ADC_11BIT
    ADC_12BIT = ADC_12BIT
    ADC_2SAMP = ADC_2SAMP
    ADC_4SAMP = ADC_4SAMP
    ADC_8SAMP = ADC_8SAMP
    ADC_16SAMP = ADC_16SAMP
    ADC_32SAMP = ADC_32SAMP
    ADC_64SAMP = ADC_64SAMP
    ADC_128SAMP = ADC_128SAMP

    def __init__(self, shunt_ohms, i2c=None, max_expected_amps=None, values=None):
        self.shunt_ohms = shunt_ohms
        self.i2c = i2c
        self.max_expected_amps = max_expected_amps
        self._values = {
            "voltage": 0.0,
            "current": 0.0,
            "shunt": 0.0,
        }
        if values:
            self._values.update(values)

    def configure(self, *args, **kwargs):
        """No-op to mirror the real driver's ``configure``."""
        return None

    def set_values(self, voltage=None, current=None, shunt=None):
        """Update stored measurement values."""
        if voltage is not None:
            self._values["voltage"] = voltage
        if current is not None:
            self._values["current"] = current
        if shunt is not None:
            self._values["shunt"] = shunt

    def voltage(self):
        return self._values["voltage"]

    def current(self):
        return self._values["current"]

    def shunt_voltage(self):
        return self._values["shunt"]
