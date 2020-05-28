from lib.srw_importer import *
from lib.default_values import *
from lib.electron_beam import get_electron_beam
from lib.magnetic_structure import get_magnetic_field_container

from single_energy_radiation_from_source import plot_single_energy_radiation

def calculate_initial_multi_energy_radiation(part_beam, magnetic_field_container,
                                              aperturex=oe1_aperturex, aperturey=oe1_aperturex, nx=oe1_aperture_nx, ny=oe1_aperture_ny, zAperture=src_to_oe1,
                                              energy_from=spectrum_energy_from, energy_to=spectrum_energy_to, ne=spectrum_energy_ne):
    mesh = SRWLRadMesh(_eStart=energy_from,
                       _eFin=energy_to,
                       _ne=ne,
                       _xStart=-aperturex / 2,
                       _xFin=aperturex / 2,
                       _nx=nx,
                       _yStart=-aperturey / 2,
                       _yFin=aperturey / 2,
                       _ny=ny,
                       _zStart=zAperture)

    wfr = SRWLWfr()
    wfr.allocate(mesh.ne, mesh.nx, mesh.ny)
    wfr.mesh = mesh
    wfr.partBeam = part_beam

    srwl.CalcElecFieldSR(wfr, 0, magnetic_field_container, source_parameters)

    return wfr


def check_electric_field(wfrEXY, x0=0, y0=0, show=True):
    # IT IS IMPORTANT TO CHECK IF THE ELECTRIC FIELD IS RESOLVED EVERYWHERE

    arIIe  = array('f', [0] * wfrEXY.mesh.ne)

    srwl.CalcIntFromElecField(arIIe, wfrEXY, 0, 5, 0, wfrEXY.mesh.eStart, x0, y0)

    uti_plot1d(arIIe,
               [wfrEXY.mesh.eStart, wfrEXY.mesh.eFin, wfrEXY.mesh.ne],
               labels=['Photon Energy', 'Re(E)', '3D Electric Field at (' + str(x0) + "," + str(y0) + ")"],
               units=['eV', '(ph/s/.1%bw/mm^2)^-1/2'])

    if show: uti_plot_show()

if __name__=="__main__":
    if not srwl_uti_proc_is_master(): exit()

    wfrEXY = calculate_initial_multi_energy_radiation(get_electron_beam(),
                                                      get_magnetic_field_container(magnetic_field_file_name),
                                                      energy_from=1,
                                                      energy_to=121,
                                                      ne=120)

    check_electric_field(wfrEXY, x0=oe1_aperturex/2, show=True)

    plot_single_energy_radiation(wfrEXY)



