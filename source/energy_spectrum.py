from core.srw_importer import *
from core.default_values import *
from core.electron_beam import get_electron_beam
from core.magnetic_structure import get_magnetic_field_container

def calculate_spectrum(part_beam, magnetic_field_container,
                       eStart=spectrum_energy_from, eFin=spectrum_energy_to, ne=spectrum_energy_ne, x0=0.0, y0=0.0, zAperture=src_to_oe1,
                       show=True):

    mesh_spectrum = SRWLRadMesh(_eStart=eStart,
                                _eFin  =eFin,
                                _ne    =ne,
                                _xStart= x0,
                                _xFin  = x0,
                                _nx    = 1,
                                _yStart= -y0,
                                _yFin  = y0,
                                _ny    = 1,
                                _zStart= zAperture)

    wfr_spectrum = SRWLWfr()
    wfr_spectrum.allocate(mesh_spectrum.ne, mesh_spectrum.nx, mesh_spectrum.ny)
    wfr_spectrum.mesh = mesh_spectrum
    wfr_spectrum.partBeam = part_beam

    srwl.CalcElecFieldSR(wfr_spectrum, 0, magnetic_field_container, [2,0.01,0.0,0.0,50000,1,0.0])

    mesh0 = deepcopy(wfr_spectrum.mesh)

    arIe = array('f', [0]*mesh0.ne)
    srwl.CalcIntFromElecField(arIe, wfr_spectrum, 6, 0, 0, mesh0.eStart, x0, y0)

    uti_plot1d(arIe,
               [wfr_spectrum.mesh.eStart, wfr_spectrum.mesh.eFin, wfr_spectrum.mesh.ne],
               labels=['Photon Energy', 'Intensity', 'Spectrum at (' + str(x0) + "," + str(y0) + ")"],
               units=['eV', 'ph/s/.1%bw/mm^2'])

    arReEe = array('f', [0]*mesh0.ne)
    srwl.CalcIntFromElecField(arReEe, wfr_spectrum, 0, 5, 0, mesh0.eStart, x0, y0)

    # IT IS IMPORTANT TO CHECK IF THE ELECTRIC FIELD IS RESOLVED EVERYWHERE

    uti_plot1d(arReEe,
               [wfr_spectrum.mesh.eStart, wfr_spectrum.mesh.eFin, wfr_spectrum.mesh.ne],
               labels=['Photon Energy', 'Re(E)', 'Electric Field at (' + str(x0) + "," + str(y0) + ")"],
               units=['eV', '(ph/s/.1%bw/mm^2)^-1/2'])

    if show: uti_plot_show()

if __name__=="__main__":
    if not srwl_uti_proc_is_master(): exit()

    x0 = oe1_aperturex/2

    calculate_spectrum(get_electron_beam(),
                       get_magnetic_field_container(magnetic_field_file_name),
                       x0=0.0)
