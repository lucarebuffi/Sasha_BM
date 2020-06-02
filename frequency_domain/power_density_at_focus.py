from core.electron_beam import get_electron_beam
from core.magnetic_structure import get_magnetic_field_container
from core.ideal_optical_system import *
from core.default_values import magnetic_field_file_name

from frequency_domain.single_energy_radiation_from_source import calculate_initial_single_energy_radiation
from frequency_domain.single_energy_radiation_at_focus import calculate_single_energy_radiation_at_focus
from frequency_domain.plot_result import plot_power_density

def get_parameters(energy=None):
    if energy is None: return [[0, 0, 1.0, 1, 0, 1.0, 1.0, 1.0, 1.0, 0, 0.0, 0.0],
                               [0, 0, 1.0, 1, 0, 1.0, 1.0, 1.0, 1.0, 0, 0.0, 0.0],
                               [0, 0, 1.0, 1, 0, 1.0, 5.0, 1.0, 5.0, 0, 0.0, 0.0],
                               [0, 0, 1.0, 1, 0, 0.75, 2.0, 0.5, 2.0, 0, 0.0, 0.0]]

    else:
        return  [[0, 0, 1.0, 1, 0, 1.0, 1.0, 1.0, 1.0, 0, 0.0, 0.0],
                 [0, 0, 1.0, 1, 0, 1.0, 1.0, 1.0, 1.0, 0, 0.0, 0.0],
                 [0, 0, 1.0, 1, 0, 1.0, 5.0, 1.0, 5.0, 0, 0.0, 0.0],
                 [0, 0, 1.0, 1, 0, 0.75, 2.0, 0.5, 2.0, 0, 0.0, 0.0]]

def get_total_intensity(wfr):
    dim_x = wfr.mesh.nx
    dim_y = wfr.mesh.ny

    def get_intensity(srw_electric_field):
        re = numpy.array(srw_electric_field[::2], dtype=numpy.float)
        im = numpy.array(srw_electric_field[1::2], dtype=numpy.float)

        intesity = numpy.abs(re + 1j * im)**2
        intesity.reshape((dim_y, dim_x))

        return intesity

    return numpy.linspace(wfr.mesh.xStart, wfr.mesh.xFin, wfr.mesh.nx),\
           numpy.linspace(wfr.mesh.yStart, wfr.mesh.yFin, wfr.mesh.ny),\
           (get_intensity(wfr.arEx) + get_intensity(wfr.arEy))

from scipy.interpolate import RectBivariateSpline
from PyQt5.QtWidgets import QApplication
import sys

if __name__=="__main__":
    if not srwl_uti_proc_is_master(): exit()

    energies = numpy.linspace(0.1, 80.1, 80)
    electron_beam = get_electron_beam()
    magnetic_field_container = get_magnetic_field_container(magnetic_field_file_name)

    dim_x = 200
    dim_y = 200

    plot_coordinates_x = numpy.linspace[-0.001, 0.001, dim_x]
    plot_coordinates_y = numpy.linspace[-0.001, 0.001, dim_y]

    total_power_density = numpy.zeros((dim_x, dim_y))

    for energy in energies:
        wfr = calculate_initial_single_energy_radiation(electron_beam, magnetic_field_container, energy=energy)
        wfr = calculate_single_energy_radiation_at_focus(wfr, get_beamline(parameters=get_parameters(energy)))

        x_coord, y_coord, intensity = get_total_intensity(wfr)
        interpolator = RectBivariateSpline(x_coord, y_coord, intensity, bbox=[None, None, None, None], kx=1, ky=1, s=0)

        power_density = interpolator(plot_coordinates_x, plot_coordinates_y)
        power_density[numpy.where(numpy.isnan(power_density))] = 0.0
        power_density *= 1000 * energy * codata.e

        total_power_density += power_density

    outdir = os.path.join(os.getcwd(), "output/frequency_domain")

    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus_coord_x.txt"), plot_coordinates_x)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus_coord_y.txt"), plot_coordinates_y)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus.txt"), power_density)

    app = QApplication(sys.argv)

    plot_power_density(plot_coordinates_x, plot_coordinates_y, total_power_density)

    app.exec_()

