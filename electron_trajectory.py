from lib.srw_importer import *
from lib.electron_beam import get_electron_beam
from lib.magnetic_structure import get_magnetic_field_container
from lib.default_values import magnetic_field_file_name, gamma_angle, gamma
import numpy
from scipy.constants import c, e

def calculate_trajectory(part_beam, magnetic_field_container):

    npTraj          = 10001 #Number of Points for Trajectory calculation
    arPrecPar       = [1] #General Precision parameters for Trajectory calculation:

    partTraj = SRWLPrtTrj()
    partTraj.partInitCond = part_beam.partStatMom1 #part
    partTraj.allocate(npTraj, True)
    partTraj.ctStart = 0 #Start Time for the calculation
    partTraj.ctEnd = 0

    partTraj = srwl.CalcPartTraj(partTraj, magnetic_field_container, arPrecPar)

    arXp = numpy.array(partTraj.arXp)
    cursor = numpy.where(numpy.logical_and(arXp >= -0.5*gamma_angle, arXp <= 0.5*gamma_angle))

    zz  = numpy.array(partTraj.arZ)[cursor]
    xx  = numpy.array(partTraj.arX)[cursor]
    zzp = numpy.array(partTraj.arZp)[cursor]
    xxp = numpy.array(partTraj.arXp)[cursor]

    velocity = c*numpy.sqrt(1-(1/gamma**2))*numpy.average(numpy.sqrt(zzp**2 + xxp**2))
    distance = 0.0
    for i in range(1, len(zz)): distance += numpy.sqrt((xx[i]-xx[i-1])**2 + (zz[i]-zz[i-1])**2)
    time = distance/velocity

    print("Distance:", distance * 100, "cm,\nVelocity:", velocity, "m/s,\n=>Time:", time*1e9, "ns")
    print("=>Current of 1 electron (e/time):", e/time, "A")

    return partTraj

def plot_trajectory(partTraj, show=True):
    for i in range(len(partTraj.arZ)):
        partTraj.arBy[i] *= 1e4
        partTraj.arZ[i]  *= 1e2
        partTraj.arX[i]  *= 1e2

    uti_plot1d_ir(partTraj.arBy, partTraj.arZ, labels=['z', 'Vertical Magnetic Field'], units=['cm', 'G', ''])
    uti_plot1d_ir(partTraj.arX,  partTraj.arZ, labels=['z', 'Horizontal Position'],     units=['cm', 'cm', ''])
    uti_plot1d_ir(partTraj.arXp, partTraj.arZ, labels=['z', 'Horizontal Angle'],        units=['cm', 'rad', ''])

    if show: uti_plot_show()

if __name__=="__main__":
    if not srwl_uti_proc_is_master(): exit()

    partTraj = calculate_trajectory(get_electron_beam(),
                                    get_magnetic_field_container(magnetic_field_file_name))

    plot_trajectory(partTraj)
