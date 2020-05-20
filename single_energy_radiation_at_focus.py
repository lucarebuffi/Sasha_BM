from lib.electron_beam import get_electron_beam
from lib.magnetic_structure import get_magnetic_field_container
from lib.ideal_optical_system import *
from lib.default_values import magnetic_field_file_name

from single_energy_radiation_from_source import calculate_initial_single_energy_radiation, plot_single_energy_radiation

def calculate_single_energy_radiation_at_focus(wfr, optBL):
    srwl.PropagElecField(wfr, optBL)
    return wfr

if __name__=="__main__":
    if not srwl_uti_proc_is_master(): exit()

    wfr = calculate_initial_single_energy_radiation(get_electron_beam(),
                                                    get_magnetic_field_container(magnetic_field_file_name),
                                                    energy=190)

    plot_single_energy_radiation(wfr, where="Before", show=False)

    wfr = calculate_single_energy_radiation_at_focus(wfr, get_beamline())

    plot_single_energy_radiation(wfr, where="After", show=True)
