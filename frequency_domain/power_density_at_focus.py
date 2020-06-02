from core.electron_beam import get_electron_beam
from core.magnetic_structure import get_magnetic_field_container
from core.ideal_optical_system import *
from core.default_values import magnetic_field_file_name

from frequency_domain.single_energy_radiation_from_source import calculate_initial_single_energy_radiation
from frequency_domain.single_energy_radiation_at_focus import calculate_single_energy_radiation_at_focus
from frequency_domain.plot_results import plot_power_density, plot_spectrum

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
    # um in mm
    return numpy.array(arI).reshape((dim_y, dim_x)).T

from scipy.interpolate import RectBivariateSpline
from PyQt5.QtWidgets import QApplication
import sys

if __name__=="__main__":
    if not srwl_uti_proc_is_master(): exit()

    if len(sys.argv) == 4:
        e_in  = float(sys.argv[1])
        e_fin = float(sys.argv[2])
        n_e   = float(sys.argv[3])
    else:
        e_in  = 1
        e_fin = 81
        n_e   = 81

    app = QApplication(sys.argv)

    energies      = numpy.linspace(e_in, e_fin, n_e)
    delta_energy  = energies[1] - energies[0]
    electron_beam = get_electron_beam()
    magnetic_field_container = get_magnetic_field_container(magnetic_field_file_name)

    dim_x = 201
    dim_y = 201

    # um in mm
    plot_coordinates_x = numpy.linspace(-0.1, 0.1, dim_x)
    plot_coordinates_y = numpy.linspace(-0.1, 0.1, dim_y)

    total_power_density = numpy.zeros((dim_x, dim_y))
    spectrum            = numpy.zeros((n_e, 2))
    spectrum[:, 0]      = energies

    for energy, ie in zip(energies, range(n_e)):
        wfr = calculate_initial_single_energy_radiation(electron_beam, magnetic_field_container, energy=energy)
        wfr = calculate_single_energy_radiation_at_focus(wfr, get_beamline(parameters=get_parameters(energy)))

        x_coord    = numpy.linspace(wfr.mesh.xStart, wfr.mesh.xFin, wfr.mesh.nx) * 1000 # mm
        y_coord    = numpy.linspace(wfr.mesh.yStart, wfr.mesh.yFin, wfr.mesh.ny) * 1000 # mm
        pixel_area = (x_coord[1] - x_coord[0]) * (y_coord[1] - y_coord[0])              # mm^2

        intensity     = get_intensity(wfr)                                    # photons/s/mm^2/0.1%BW
        spectral_flux = intensity.sum() * pixel_area                          # photons/s/0.1%BW
        power         = (spectral_flux * 1e3 * delta_energy * codata.e) * 1e9 # power in nW in the interval E + dE
        power_density = (intensity * 1e3 * delta_energy * codata.e) * 1e9     # nW/mm^2

        # cumulative quantities ##################################
        spectrum[ie, 1]   = spectral_flux

        # to cumulate we need the same spatial mesh
        interpolator  = RectBivariateSpline(x_coord, y_coord, power_density)
        power_density = interpolator(plot_coordinates_x, plot_coordinates_y)
        power_density[numpy.where(numpy.logical_or(numpy.isnan(power_density), power_density < 0.0))] = 0.0

        total_power_density += power_density

        print("Energy", round(energy, 1), ", S.F.", round(spectral_flux, 2), "ph/s/0.1%BW, Power", round(power, 6), "nW, Peak P.D.", round(numpy.max(power_density), 4), "nW/mm^2")

    outdir = os.path.join(base_output_dir, "frequency_domain")
    if not os.path.exists(outdir): os.mkdir(outdir)

    numpy.savetxt(os.path.join(outdir, "Spectrum_at_focus.txt"),                       spectrum)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus_coord_x.txt"), plot_coordinates_x)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus_coord_y.txt"), plot_coordinates_y)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus.txt"),         total_power_density)

    plot_spectrum(spectrum)
    plot_power_density(plot_coordinates_x, plot_coordinates_y, total_power_density)

    app.exec_()

