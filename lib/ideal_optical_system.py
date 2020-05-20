from lib.srw_importer import *
from lib.default_values import *

def get_beamline(f1=src_to_oe1, drift=oe1_to_oe2, f2=oe2_to_focus):
    srw_oe_array = []
    srw_pp_array = []

    oe_0 =SRWLOptL(_Fx=f1, _Fy=f1, _x=0.0, _y=0.0)
    pp_oe_0 = [0, 0, 1.0, 1, 0, 1.0, 1.0, 1.0, 1.0, 0, 0.0, 0.0]

    srw_oe_array.append(oe_0)
    srw_pp_array.append(pp_oe_0)

    drift_before_oe_1 = SRWLOptD(drift)
    pp_drift_before_oe_1 = [0, 0, 1.0, 1, 0, 1.0, 1.0, 1.0, 1.0, 0, 0.0, 0.0]

    srw_oe_array.append(drift_before_oe_1)
    srw_pp_array.append(pp_drift_before_oe_1)

    oe_2 =SRWLOptL(_Fx=f2, _Fy=f2, _x=0.0, _y=0.0)
    pp_oe_2 = [0, 0, 1.0, 1, 0, 1.0, 5.0, 1.0, 5.0, 0, 0.0, 0.0]

    srw_oe_array.append(oe_2)
    srw_pp_array.append(pp_oe_2)

    drift_before_oe_3 = SRWLOptD(f2)

    pp_drift_before_oe_3 = [0, 0, 1.0, 1, 0, 0.75, 2.0, 0.5, 2.0, 0, 0.0, 0.0]

    srw_oe_array.append(drift_before_oe_3)
    srw_pp_array.append(pp_drift_before_oe_3)

    return SRWLOptC(srw_oe_array, srw_pp_array)
