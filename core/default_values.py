import numpy
import scipy.constants as codata

magnetic_field_file_name_input = "/Users/lrebuffi/Box Sync/Luca_Xianbo_Share/Sasha/BM/data/monoPoleSquareProfile_8mmGap.dat"
magnetic_field_file_name = "/Users/lrebuffi/Box Sync/Luca_Xianbo_Share/Sasha/BM/data/monoPoleSquareProfile_8mmGap_srw.dat"
magnetic_field_file_name = "/Users/lrebuffi/Box Sync/Luca_Xianbo_Share/Sasha/BM/data/wiggler_1pole_srw.dat"

base_output_dir = "/Users/lrebuffi/Box Sync/Luca_Xianbo_Share/Sasha/BM/output"

ring_electron_energy = 0.147 # GeV
current_1_electron = 1.8125191290905425e-08 # A (current of 1 electron emitting on +-1/gamma)

gamma = ring_electron_energy/(codata.electron_mass*codata.c**2/codata.e*1e-9)
gamma_angle = 1/gamma

print("Gamma angle", gamma_angle*1000, "mrad")

spectrum_energy_from = 1
spectrum_energy_to   = 121#181
spectrum_energy_ne   = 120#180

src_to_oe1 = 4.0915
oe1_to_oe2 = 8.027
oe2_to_focus = 4.0915

oe1_grazing_angle = numpy.radians(3.087)/2
oe2_grazing_angle = numpy.radians(3.087)/2

oe1_aperturex = src_to_oe1*numpy.tan(gamma_angle) #(+- 0.5/gamma)
oe1_aperturey = oe1_aperturex

#mirror_length = 1.2
#oe1_aperturex = mirror_length*numpy.sin(oe1_grazing_angle)
#oe1_aperturey = 0.05

print("Initial Aperture: " + str(oe1_aperturex) + " x " + str(oe1_aperturey) + " mm, at " + str(src_to_oe1) + " m")

oe1_aperture_nx = 284#586#142
oe1_aperture_ny = 284#586#142

default_source_parameters = [2, 1e-2, 0.0, 0.0, 20000, 1, 0.0]

def get_central_energy(wfr, energy=None):
    return 0.5 * (wfr.mesh.eStart + wfr.mesh.eFin) if energy is None else energy

'''
srwl.CalcIntFromElecField(output_array, 
                          wfr, 
                          polarization_component_to_be_extracted, 
                          calculation_type, 
                          type_of_dependence, 
                          fixed_input_photon_energy_or_time, 
                          fixed_horizontal_position, 
                          fixed_vertical_position)

:param polarization_component_to_be_extracted:
               =0 -Linear Horizontal;
               =1 -Linear Vertical;
               =2 -Linear 45 degrees;
               =3 -Linear 135 degrees;
               =4 -Circular Right;
               =5 -Circular Left;
               =6 -Total
:param calculation_type:
               =0 -"Single-Electron" Intensity;
               =1 -"Multi-Electron" Intensity;
               =2 -"Single-Electron" Flux;
               =3 -"Multi-Electron" Flux;
               =4 -"Single-Electron" Radiation Phase;
               =5 -Re(E): Real part of Single-Electron Electric Field;
               =6 -Im(E): Imaginary part of Single-Electron Electric Field;
               =7 -"Single-Electron" Intensity, integrated over Time or Photon Energy (i.e. Fluence)
:param type_of_dependence:
               =0 -vs e (photon energy or time);
               =1 -vs x (horizontal position or angle);
               =2 -vs y (vertical position or angle);
               =3 -vs x&y (horizontal and vertical positions or angles);
               =4 -vs e&x (photon energy or time and horizontal position or angle);
               =5 -vs e&y (photon energy or time and vertical position or angle);
               =6 -vs e&x&y (photon energy or time, horizontal and vertical positions or angles);
:param fixed_input_photon_energy_or_time: input photon energy [eV] or time [s] to keep fixed (to be taken into account for dependences vs x, y, x&y)
:param fixed_horizontal_position: input horizontal position [m] to keep fixed (to be taken into account for dependences vs e, y, e&y)
:param fixed_vertical_position: input vertical position [m] to keep fixed (to be taken into account for dependences vs e, x, e&x)
'''
