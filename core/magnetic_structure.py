from core.srw_importer import *

def AuxReadInMagFld3D(filePath, sCom):
    f = open(filePath, 'r')
    f.readline()  # 1st line: just pass

    xStart = float(f.readline().split(sCom, 2)[1])  # 2nd line: initial X position [m]; it will not actually be used
    xStep = float(f.readline().split(sCom, 2)[1])  # 3rd line: step vs X [m]
    xNp = int(f.readline().split(sCom, 2)[1])  # 4th line: number of points vs X
    yStart = float(f.readline().split(sCom, 2)[1])  # 5th line: initial Y position [m]; it will not actually be used
    yStep = float(f.readline().split(sCom, 2)[1])  # 6th line: step vs Y [m]
    yNp = int(f.readline().split(sCom, 2)[1])  # 7th line: number of points vs Y
    zStart = float(f.readline().split(sCom, 2)[1])  # 8th line: initial Z position [m]; it will not actually be used
    zStep = float(f.readline().split(sCom, 2)[1])  # 9th line: step vs Z [m]
    zNp = int(f.readline().split(sCom, 2)[1])  # 10th line: number of points vs Z
    totNp = xNp * yNp * zNp
    locArBx = array('d', [0] * totNp)
    locArBy = array('d', [0] * totNp)
    locArBz = array('d', [0] * totNp)

    for i in range(totNp):
        curLineParts = f.readline().split('	')
        if len(curLineParts)==3:
            locArBx[i] = float(curLineParts[0].strip())
            locArBy[i] = float(curLineParts[1].strip())
            locArBz[i] = float(curLineParts[2].strip())
    f.close()
    xRange = xStep
    if xNp > 1: xRange = (xNp - 1) * xStep
    yRange = yStep
    if yNp > 1: yRange = (yNp - 1) * yStep
    zRange = zStep
    if zNp > 1: zRange = (zNp - 1) * zStep

    return SRWLMagFld3D(locArBx, locArBy, locArBz, xNp, yNp, zNp, xRange, yRange, zRange, 1)


def get_magnetic_field_container(filename, from_file=False):
    if from_file:
        magnetic_structure = AuxReadInMagFld3D(filename, "#")

        magnetic_field_container = SRWLMagFldC()
        magnetic_field_container.allocate(1)

        magnetic_field_container.arMagFld[0] = magnetic_structure
        magnetic_field_container.arMagFld[0].interp = 3
        magnetic_field_container.arXc[0] = 0.0
        magnetic_field_container.arYc[0] = 0.0
        magnetic_field_container.arZc[0] = 0.0
    else:
        magnetic_structure = SRWLMagFldM(_G=1.6, _m=1, _n_or_s='n', _Leff=0.129)
        magnetic_field_container = SRWLMagFldC(_arMagFld=[magnetic_structure],
                                               _arXc=array('d', [0.0]),
                                               _arYc=array('d', [0.0]),
                                               _arZc=array('d', [0.0]))

    return magnetic_field_container
