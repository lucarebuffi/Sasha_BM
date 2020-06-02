from core.srw_importer import *
from core.default_values import *
from core.electron_beam import get_electron_beam
from core.magnetic_structure import get_magnetic_field_container

def calculate_initial_single_energy_radiation(part_beam, magnetic_field_container,
                                              aperturex=oe1_aperturex,
                                              aperturey=oe1_aperturey,
                                              nx=oe1_aperture_nx,
                                              ny=oe1_aperture_ny,
                                              zAperture=src_to_oe1,
                                              energy=20):
    mesh = SRWLRadMesh(_eStart=energy,
                       _eFin=energy,
                       _ne=1,
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

def plot_single_energy_radiation(wfr, energy=None, where="Before", show=True):
    energy = get_central_energy(wfr, energy)
    
    arI = array('f', [0] * wfr.mesh.nx * wfr.mesh.ny)
    srwl.CalcIntFromElecField(arI, wfr, 6, 0, 3, energy, 0, 0)

    plotMesh0x = [1000 * wfr.mesh.xStart, 1000 * wfr.mesh.xFin, wfr.mesh.nx]
    plotMesh0y = [1000 * wfr.mesh.yStart, 1000 * wfr.mesh.yFin, wfr.mesh.ny]
    uti_plot2d1d(arI, plotMesh0x, plotMesh0y, labels=['Horizontal Position [mm]', 'Vertical Position [mm]', 'Intensity ' + where + ' Propagation, E=' + str(energy)])

    if show: uti_plot_show()

import sys
if __name__=="__main__":
    if not srwl_uti_proc_is_master(): exit()

    try:    energy = float(sys.argv[1])
    except: energy = 20

    wfr = calculate_initial_single_energy_radiation(get_electron_beam(),
                                                    get_magnetic_field_container(magnetic_field_file_name),
                                                    energy=energy)

    plot_single_energy_radiation(wfr)
