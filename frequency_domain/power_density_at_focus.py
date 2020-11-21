import time
from core.electron_beam import get_electron_beam
from core.magnetic_structure import get_magnetic_field_container
from core.ideal_optical_system import *
from core.default_values import magnetic_field_file_name

from frequency_domain.single_energy_radiation_from_source import calculate_initial_single_energy_radiation
from frequency_domain.single_energy_radiation_at_focus import calculate_single_energy_radiation_at_focus
from frequency_domain.plot_results import plot_power_density, plot_spectrum

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

def run_script(argv):
    if not srwl_uti_proc_is_master(): exit()

    if len(argv) == 3:
        e_in  = float(argv[0])
        e_fin = float(argv[1])
        n_e   = int(argv[2])
    else:
        e_in  = 0.1
        e_fin = 200.1
        n_e   = 201

    app = QApplication([])

    energies      = numpy.linspace(e_in, e_fin, n_e)
    delta_energy  = energies[1] - energies[0]
    electron_beam = get_electron_beam(x0=-2e-6)
    magnetic_field_container = get_magnetic_field_container(magnetic_field_file_name)
    beamline = get_beamline(parameters=auto_parameters)

    dim_x = 2001
    dim_y = 2001

    # um in mm
    plot_coordinates_x = numpy.linspace(-0.1, 0.1, dim_x)
    plot_coordinates_y = numpy.linspace(-0.1, 0.1, dim_y)
    plot_pixel_area    = (plot_coordinates_x[1] - plot_coordinates_x[0]) * (plot_coordinates_y[1] - plot_coordinates_y[0])

    total_power_density = numpy.zeros((dim_x, dim_y))
    spectrum            = numpy.zeros((n_e, 2))
    spectrum[:, 0]      = energies
    total_power         = 0.0
    total_power_interp  = 0.0

    source_parameters      = default_source_parameters


    for energy, ie in zip(energies, range(n_e)):
        wfr = calculate_initial_single_energy_radiation(electron_beam, magnetic_field_container,
                                                        energy=energy,
                                                        source_parameters=source_parameters,
                                                        aperturex=0.015,
                                                        aperturey=0.015)
        wfr = calculate_single_energy_radiation_at_focus(wfr, beamline)

        x_coord    = numpy.linspace(wfr.mesh.xStart, wfr.mesh.xFin, wfr.mesh.nx) * 1000 # mm
        y_coord    = numpy.linspace(wfr.mesh.yStart, wfr.mesh.yFin, wfr.mesh.ny) * 1000 # mm

        pixel_area = (x_coord[1] - x_coord[0]) * (y_coord[1] - y_coord[0])              # mm^2

        intensity     = get_intensity(wfr)                   # photons/s/mm^2/0.1%BW

        intensity[numpy.where(numpy.isnan(intensity))] = 0.0
        intensity[numpy.where(intensity < 0.0)]        = 0.0

        integrated_flux = intensity.sum() * pixel_area         # photons/s/0.1%BW

        power_density = (intensity * 1e3 * delta_energy * codata.e) * 1e9     # nW/mm^2
        power         = (integrated_flux * 1e3 * delta_energy * codata.e) * 1e9 # power in nW in the interval E + dE

        print("Energy", round(energy, 2),
              ", S.F.", round(integrated_flux, 2),
              "ph/s/0.1%BW, Max Intensity", round(numpy.max(intensity), 2),
              "ph/s/0.1%BW/mm^2, Power (before fit)", round(power, 6),
              "nW, Max P.D. (before fit)", round(numpy.max(power_density), 4), "nW/mm^2")

        total_power += power

        # cumulative quantities ##################################
        spectrum[ie, 1]   = integrated_flux

        renorm_factor_pd = power

        # to cumulate we need the same spatial mesh
        interpolator  = RectBivariateSpline(x_coord, y_coord, power_density, kx=3, ky=3)
        power_density = interpolator(plot_coordinates_x, plot_coordinates_y)
        power_density[numpy.where(numpy.isnan(power_density))] = 0.0
        power_density[numpy.where(power_density < 0.0)]        = 0.0

        power = power_density.sum() * plot_pixel_area

        renorm_factor_pd /= power

        power_density *= renorm_factor_pd

        total_power_density += power_density
        total_power_interp += power

        print("                                                                                     ",
              "Power (after fit)", round(power, 6),
              "nW, Max P.D. (after fit)", round(numpy.max(power_density), 4), "nW/mm^2\n")

    print("Calculation completed", "Total Power", round(total_power, 6), round(total_power_interp, 6), "nW, Min/Max Total P.D.", round(numpy.min(total_power_density), 4), round(numpy.max(total_power_density), 4), "nW/mm^2\n")

    outdir = os.path.join(base_output_dir, "frequency_domain")
    if not os.path.exists(outdir): os.mkdir(outdir)

    numpy.savetxt(os.path.join(outdir, "Spectrum_at_focus.txt"),                       spectrum)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus_coord_x.txt"), plot_coordinates_x)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus_coord_y.txt"), plot_coordinates_y)
    numpy.savetxt(os.path.join(outdir, "Power_Density_at_Focus.txt"),         total_power_density)

    plot_spectrum(spectrum)

    x_indexes = numpy.where(numpy.logical_and(plot_coordinates_x>= -0.025, plot_coordinates_x <= 0.025))
    y_indexes = numpy.where(numpy.logical_and(plot_coordinates_y>= -0.025, plot_coordinates_y <= 0.025))

    power_density_reduced = numpy.zeros((len(x_indexes[0]), len(y_indexes[0])))

    for i in range(len(x_indexes[0])):
        for j in range(len(y_indexes[0])):
            power_density_reduced[i, j] = total_power_density[x_indexes[0][i], y_indexes[0][j]]

    print(power_density_reduced.shape)

    #plot_power_density(plot_coordinates_x, plot_coordinates_y, total_power_density, total_power)
    plot_power_density(plot_coordinates_x[x_indexes], plot_coordinates_y[y_indexes], power_density_reduced, total_power)

    app.exec_()

if __name__=="__main__":
    run_script(sys.argv[1:])
