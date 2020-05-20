from lib.srw_importer import *
from lib.default_values import *

import scipy.constants as codata

electron_rest_energy_in_GeV = codata.electron_mass*codata.c**2/codata.e*1e-9

def get_electron_beam(x0=0.0, y0=0.0, z0=0.0, xp0=0.0, yp0=0.0, electron_energy=ring_electron_energy, current=current_1_electron):

    ####################################################
    # LIGHT SOURCE

    part_beam = SRWLPartBeam()
    part_beam.Iavg = current
    part_beam.partStatMom1.x = x0
    part_beam.partStatMom1.y = y0
    part_beam.partStatMom1.z = z0
    part_beam.partStatMom1.xp = xp0
    part_beam.partStatMom1.yp = yp0
    part_beam.partStatMom1.gamma = electron_energy / electron_rest_energy_in_GeV
    part_beam.arStatMom2[0] = 0.0
    part_beam.arStatMom2[1] = 0.0
    part_beam.arStatMom2[2] = 0.0
    part_beam.arStatMom2[3] = 0.0
    part_beam.arStatMom2[4] = 0.0
    part_beam.arStatMom2[5] = 0.0
    part_beam.arStatMom2[10] = 0.0

    return part_beam
