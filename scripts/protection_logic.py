"""Behavioural model of the proposed protection enable logic.

This is a state-machine check of the intended control rules, not a circuit
simulation, a timing qualification or a part selection. Thresholds passed to
the model are illustrative parameters until a supervisor part is selected.
"""

# INA300 SBOS613C, Table 6.3 "Operating supply voltage": 2.7 V minimum.
INA300_VS_MIN_V = 2.7


class ProtectionLogic:
    """Switch enable = supply valid AND supervisor released AND no latched fault."""

    def __init__(self, supervisor_fall_v=2.9, release_delay_ms=100.0, buffer_min_v=1.2):
        if supervisor_fall_v <= INA300_VS_MIN_V:
            raise ValueError('supervisor must trip above the detector minimum supply')
        self.supervisor_fall_v = supervisor_fall_v
        self.release_delay_ms = release_delay_ms
        self.buffer_min_v = buffer_min_v
        self.pico_v = 0.0
        self.good_ms = 0.0
        self.latched = False
        self.overcurrent = False

    @property
    def supervisor_released(self):
        return self.good_ms >= self.release_delay_ms

    @property
    def detector_valid(self):
        return self.pico_v >= INA300_VS_MIN_V

    @property
    def enabled(self):
        return (self.pico_v >= self.buffer_min_v and self.supervisor_released
                and not self.latched)

    def set_pico(self, volts):
        self.pico_v = volts
        if volts < self.supervisor_fall_v:
            self.good_ms = 0.0
        self._evaluate()

    def tick(self, ms):
        if self.pico_v >= self.supervisor_fall_v:
            self.good_ms += ms
        self._evaluate()

    def set_overcurrent(self, present):
        self.overcurrent = present
        self._evaluate()

    def press_reset(self):
        """A deliberate reset clears the latch only if the overcurrent has ended."""
        if self.detector_valid and not self.overcurrent:
            self.latched = False

    def _evaluate(self):
        # The detector can latch only while it is powered, and the switch can be on
        # only while the detector is powered, so a fault while enabled is always seen.
        if self.overcurrent and self.detector_valid:
            self.latched = True
