"""polyTessellator.py

    This files provides scripts and functions to call the program Triangle to
     tessellate the polygons from the stimuli. To do so, the polygons must first
     be written in the appropriate format so that Triangle understand the geometry.
"""

import json
import subprocess as sub
import os

def toTriangle(filePath='./'):
    """toTriangle function:

        This function translates a list of polygons written in the TrainingFeedback
        format into the format for Triangle.

        filePath='./': path where a file with the list of polygons is stored.
    """
    with open(os.path.join(filePath, 'polies.json')) as f:
        polygonsList = json.load(f)

    colors, positions = [], []
    for indPoly, poly in enumerate(polygonsList):

        colors.append(poly['color'])
        positions.append(poly['position'])
        points = poly['points']

        # Prepare file and write:
        with open(filePath+'poly'+str(indPoly)+'.poly', 'w') as f:
            f.write(str(len(points))+' 2 0 1\n')            # First line!
            for indPoint, point in enumerate(points):       # Points!
                f.write(str(indPoint+1)+' '+str(point[0])+' '+str(point[1])+' 1\n')
            f.write(str(len(points))+' 1\n')                # Line preceeding the segments!
            for indPoint, point in enumerate(points):       # Segments!
                a = indPoint
                b = indPoint+1
                if (a==0):
                    a = len(points)
                f.write(str(indPoint+1)+' '+str(a)+' '+str(b)+'\n')
            f.write('0\n')                                  # Number of holes (always 0)!
    return colors, positions


def toFeedbackSingle(polyName, polyPath='./'):
    """toFeedbackSingle function:

        This function translates one single polygon written in Triangle format
        into a polygon written for feedback format. Polies written in Triangle
        format make usage of three folders: one contains the elements of the
        tessellation, one contains the vertices and the last one contains the
        info of the edges shaping the outer boundary of the polygon. It reads the
        vertices and the elements of the tessellation from the corresponding
        files. It doesn't care about the edges which shape the outer side because
        the polygons will be solid when displayed and the edges won't be highlighted.

    Input:
        polyName: name of the polygon written in Triangle format.
            The function will use the name to inspect the files polyName+'.1.node'
            and polyName+'.1.ele'.
        polyPath='./': path where the files with the info of the polygon are stored.

    Output:
        poliesList: list of the polygons which make up the tessellation,
        written each one in the Feedback format.
    """

    # Reading the info from the files:
    with open(polyPath+polyName+'.1.node', 'r') as f:
        dataNodes = f.read()
    with open(polyPath+polyName+'.1.ele', 'r') as f:
        dataElems = f.read()

    # Popping out the final lines:
    listNodes = dataNodes.split('\n')
    listElems = dataElems.split('\n')
    listNodes.pop()
    listNodes.pop()
    listElems.pop()
    listElems.pop()

    # Extracting the nodes:
    nodes = []
    for indNode, node in enumerate(listNodes):
        if indNode > 0:
            newNode = [float(row) for row in node.split('  ') if row is not '']
            nodes += [newNode]

    # Extracting the elements.
    elems = []
    for indElem, elem in enumerate(listElems):
        if indElem > 0:
            newElem = [int(row) for row in elem.split('  ') if row is not '']
            elems += [newElem]

    # Building the triangles which make up the tessellation.
    poliesList = []
    for indElem, elem in enumerate(elems):
        # Explicitly writing the vertices:
        v1 = (nodes[elem[1]-1][1], nodes[elem[1]-1][2])
        v2 = (nodes[elem[2]-1][1], nodes[elem[2]-1][2])
        v3 = (nodes[elem[3]-1][1], nodes[elem[3]-1][2])
        newPoly = [v1, v2, v3]
        poliesList += [newPoly]

    return poliesList;


def toFeedbackMany(colorsList, positions_list, polyPath='./'):
    """toFeedbackMany function:

        This function calls toFeedbackSingle() to
        convert back into the Feedback format the many polygons which constitute
        the tilings of the polygons of the decomposition. It supposses that the
        polygons are enumerated beginning with 0 and that the corresponding
        files '.#.ele' and '.#.node' (where # represent an index) exist.
        The color and position list contain information from the original files.
    """

    listPolies = []
    for indColor, newColor in enumerate(colorsList):

        newPoly = []
        for newPoints in toFeedbackSingle('poly'+str(indColor), polyPath=polyPath):
            newPoly.append({'color': newColor,
                            'points': newPoints,
                            'position': positions_list[indColor]})
        listPolies.append(newPoly)
    return listPolies


def transDecomp(namesPath):
    """transDecomp function:

        First: the function reads the corresponding polies.json file to load
            the polygons of each decomposition and translate them into files fit
            for Triangle. This first step is done through the function: toTriangle().
        Second: the function calls the Triangle program to calculate the
            tilings of the polygons. This remains to be solved but shouldn't be a big deal.
        Third: it puts back together the tiling of each polygon of each
            decomposition with its color and outputs the final list of lists of
            polygons into a polies_.json file.
    """

    namesList = sub.os.listdir(namesPath)
    exclude_files = ['.DS_Store', 'conf.json', 'README.txt']
    namesList = [name for name in namesList if not name in exclude_files]

    for imgName in namesList:
        imgPath = os.path.join(namesPath, imgName)

        ## 1: produce the files for Triangle:
        colors, positions = toTriangle(filePath=imgPath);

        ## 2: call Triangle from python:
        for indColor, color in enumerate(colors):
            sub.call(["triangle", "-p", imgPath+'poly'+str(indColor)+'.poly'])

        ## 3: Back to Feedback Format, which includes a loop over the colors itself:
        newPoliesList = toFeedbackMany(colors, positions, polyPath=imgPath)
        with open(os.path.join(imgPath, 'polies_.json'), 'w') as f:
            json.dump(newPoliesList, f)

        ## 4: Removing files which arn't needed anymore!
        for indColor, color in enumerate(colors):
            sub.call(["rm", imgPath+'poly'+str(indColor)+'.1.ele'])
            sub.call(["rm", imgPath+'poly'+str(indColor)+'.1.node'])
            sub.call(["rm", imgPath+'poly'+str(indColor)+'.1.poly'])
            sub.call(["rm", imgPath+'poly'+str(indColor)+'.poly'])


if __name__ == '__main__':
    expPath = '/Users/dedan/projects/bci/out1/270312_133507/'
    transDecomp(expPath);

