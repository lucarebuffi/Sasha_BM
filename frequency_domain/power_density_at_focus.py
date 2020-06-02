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

def get_intensity(wfr):
    dim_x = wfr.mesh.nx
    dim_y = wfr.mesh.ny

    arI = array('f', [0] * wfr.mesh.nx * wfr.mesh.ny)
    srwl.CalcIntFromElecField(arI, wfr, 6, 0, 3, wfr.mesh.eStart, 0, 0)

    return numpy.linspace(wfr.mesh.xStart, wfr.mesh.xFin, wfr.mesh.nx),\
           numpy.linspace(wfr.mesh.yStart, wfr.mesh.yFin, wfr.mesh.ny),\
           numpy.array(arI).reshape((dim_y, dim_x)).T

from scipy.interpolate import RectBivariateSpline
from PyQt5.QtWidgets import QApplication
import sys

if __name__=="__main__":
    if not srwl_uti_proc_is_master(): exit()

    app = QApplication(sys.argv)

    energies = numpy.linspace(1, 51, 50)
    delta_energy = energies[1] - energies[0]
    electron_beam = get_electron_beam()
    magnetic_field_container = get_magnetic_field_container(magnetic_field_file_name)

    dim_x = 201
    dim_y = 201

    plot_coordinates_x = numpy.linspace(-0.0002, 0.0002, dim_x)
    plot_coordinates_y = numpy.linspace(-0.0002, 0.0002, dim_y)

    total_power_density = numpy.zeros((dim_x, dim_y))

    for energy in energies:
        wfr = calculate_initial_single_energy_radiation(electron_beam, magnetic_field_container, energy=energy)
        wfr = calculate_single_energy_radiation_at_focus(wfr, get_beamline(parameters=get_parameters(energy)))

        x_coord, y_coord, intensity = get_intensity(wfr)

        interpolator = RectBivariateSpline(x_coord, y_coord, intensity)

        intensity                = interpolator(plot_coordinates_x, plot_coordinates_y) * delta_energy / (0.001 * energy)
        intensity[numpy.where(numpy.isnan(intensity))] = 0.0

        power                    = intensity * 1000 * delta_energy * codata.e # power in the interval E + dE
        probability_distribution = intensity / intensity.sum()

        power_density            = power * probability_distribution

        total_power_density += power_density

    outdir = os.path.join(os.getcwd().split("frequency_domain")[0], "output/frequency_domain")
    if not os.path.exists(outdir): os.mkdir(outdir)

    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus_coord_x.txt"), plot_coordinates_x)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus_coord_y.txt"), plot_coordinates_y)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus.txt"), power_density)

    plot_power_density(plot_coordinates_x, plot_coordinates_y, total_power_density)

    app.exec_()

