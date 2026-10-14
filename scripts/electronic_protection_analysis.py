"""Arithmetic for an electronic-fuse study, with explicit unqualified limits."""
import itertools


def analyze(copper_mohm, limit_ohm=1430):
    shunt_ohm = .005
    shunt_tolerance = .005
    limit_tolerance = .001
    # INA300 SBOS613C p5 and p12. Use a symmetric 650 uV screening envelope
    # rather than claiming its deliberately negative noise offset is symmetric.
    # Only initial resistor/shunt tolerance: not a completed temperature budget.
    thresholds = [(ilimit*limit_ohm*(1+rl_sign*limit_tolerance)-500e-6+offset) /
                  (shunt_ohm*(1+shunt_sign*shunt_tolerance))
                  for ilimit,rl_sign,shunt_sign,offset in itertools.product(
                      (19.85e-6,20.15e-6),(-1,1),(-1,1),(-650e-6,650e-6))]
    component_without_fuse_mohm = shunt_ohm*1000*(1+shunt_tolerance)+2.8+2
    reference_without_fuse_mV = 5*(component_without_fuse_mohm+copper_mohm)
    return dict(
        evidence_type='engineering study arithmetic; not a circuit qualification or physical measurement',
        authorization='User agreed to study electronic protection; no topology promoted to main CAD',
        target_drop_mV=100, nominal_current_A=5,
        baseline_copper_mohm=copper_mohm,
        accounting_comparison=dict(
            cartridge_reference_mV=reference_without_fuse_mV+47.5,
            tps25982_typical_ron_reference_mV=reference_without_fuse_mV+5*2.7,
            tps25982_maximum_ron_reference_mV=reference_without_fuse_mV+5*4.5,
            shared_shunt_comparator_reference_mV=reference_without_fuse_mV,
            shared_shunt_remaining_mV=100-reference_without_fuse_mV,
            limitations='Accounting on incumbent copper only; removing the fuse changes routing. Header, holder, further heating, tolerances and new routing not qualified. TPS25982 resistance tested at 2A, not 5A.'),
        comparator=dict(candidate_mpn='INA300AIDGSR',shunt_ohm=shunt_ohm,
            limit_resistor_ohm=limit_ohm,limit_resistor_tolerance=limit_tolerance,
            delay_setting='open: 10 us nominal setting',noise_adjustment_V=500e-6,
            nominal_trip_A=(20e-6*limit_ohm-500e-6)/shunt_ohm,
            screening_trip_A=[min(thresholds),max(thresholds)],
            screening_includes='19.85..20.15 uA threshold source; initial 0.1% RLIMIT / 0.5% shunt; conservative +/-650 uV offset envelope',
            qualified_trip_interval=False,
            missing='Temperature/ageing, actual VCM/supply rejection, input wiring/filter error and NAF validation; no maximum response guarantee inferred from a typical delay',
            input_bias_reference_per_pin_uA=10,
            input_bias_spec_condition='25 C table condition; enabled; not a full-temperature or unpowered bound',
            downstream_input_bias_reference_fraction_at_100mA=10e-6/.1,
            supply_owner='Independent Pico 3V3, not the measured DUT rail',
            supply_reference_max_uA=150,
            bias_boundary='IN- is an explicit additional measured-side input current; calibration must retain/characterize it',
            detects='Positive overcurrent only; does not establish reverse-current protection'),
        logic=dict(
            direct_alert_to_shdn_margin_V=.4-.4,
            direct_connection_qualified=False,
            preferred_interface='SN74AUP1G17DBVR buffer plus SHDN pull-down; architecture only',
            reference_low_margin_V=.4-.1,
            low_spec_condition='Buffer VOL max .1 V at 20 uA, or .33 V at 2.7 mA/VCC3 V; verify SHDN loading under actual conditions',
            off_reference_shdn_V=(.6e-6+15e-9)*100e3*1.01,
            off_spec_condition='AUP Ioff max .6 uA at VCC0; LTC SHDN 15nA reference at SHDN10V/VIN60V; not brownout qualification',
            brownout_interlock_required=True,
            startup_arming_required=True,
            manual_latch_reset_required=True,
            slow_shutdown='LTC4367 SHDN uses slow gate discharge: 50..160 uA at stated 12V conditions; do not call it the fast UV/OV path',
            uv_wired_or_rejected='INA300 ALERT leakage up to 1uA would shift the precision UV divider; no direct UV connection adopted'),
        release=dict(design_selected=False,schematic_integrated=False,layout_integrated=False,
                     complete_loss_bound=False,bench_validated=False,
                     korad_current_limit_remains_primary=True))
