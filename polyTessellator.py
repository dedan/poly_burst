"""polyTessellator.py

    This files provides scripts and functions to call the program Triangle to
    tessellate the polygons from the stimuli. To do so, the polygons must first
     be written in the appropriate format so that Triangle understand the geometry.
     Here are also provided functions to translate polygons into the this format
     and back to the format that the TrainingFeedback uses.

    Functions:
        toTriangle(): function to translate the polygons from the TrainingFeedback
            format into the Triangle format. This function translates all the
            polygons in the file 'polies.json'.
        toFeedbackSingle(): function to translate the tiling of one single polygon
            into the format of the TrainingFeedback.
"""

import json, pickle
import subprocess as sub
import os


def toTriangle(polygonsList=None, filePath='./', fileName='polies.json', flagJson=True, flagColors=False):
    """toTriangle function:

        This function translates a list of polygons written in the TrainingFeedback
        format into the format for Triangle.

    VariableS:
        >> polygonsList=None: list of polygons to be translated.
            If not present, then the polies are read from a file.
        >> filePath='./': path where a file with the list of polygons is stored.
        >> fileName='polies.json': file where the list of polygons is stored.

    """

    # If a list of polygons is not provided, we must read from the corresponding file:
    if not polygonsList:
        if flagJson:
            polygonsList = json.load(open(os.path.join(filePath, fileName), 'r'))
        else:
            fileName = 'drawing.pckl'
            f = open(os.path.join(filePath, fileName))
            loadedPickler = pickle.Unpickler(f).load()
            polygonsList = loadedPickler.polies

    # If colors are required:
    if flagColors:
        colors = []

    # Run over the polygons:
    for indPoly, poly in enumerate(polygonsList):

        if flagColors:
            colors += [poly['color']]
        points = poly['points']

        # Prepare file and write:
        f = open(filePath+'poly'+str(indPoly)+'.poly', 'w')
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
        f.close()

    # If colors: return them:
    if flagColors:
        return colors


def toFeedbackSingle(polyName, polyPath='./'):
    """toFeedbackSingle function:

        This function translates one single polygon written in Triangle format
        into a polygon written for feedback format. It was chosen to write a
        function to solve one single polygon, so solving the many polygons and
        arranging them into a list to json-ize should be done by calling this
        function many times. Polies written in Triangle format make usage of
        three folders: one contains the elements of the tessellation, one
        contains the vertices and the last one contains the info of the edges
        which shape the outer boundary of the polygon. This routine reads the
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
    fNodes = open(polyPath+polyName+'.1.node', 'r')
    fElems = open(polyPath+polyName+'.1.ele', 'r')
    dataNodes = fNodes.read()
    dataElems = fElems.read()
    fNodes.close()
    fElems.read()

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


def toFeedbackMany(colorsList, polyPath='./'):
    """toFeedbackMany function:

        This function calls exhaustivelly the function toFeedbackSingle() to
        convert back into the Feedback format the many polygons which constitute
        the tilings of the polygons of the decomposition. It supposses that the
        polygons are enumerated beginning with 0 and that the corresponding
        files '.#.ele' and '.#.node' (where # represent an index) exist.
        It also makes use of a colorsList which must be provided. This list says
        the color of the corresponding polies and also says how many polygons there must be.

    Input:
        colorsList: list with the colors that each tiling will take in the final display.
        polyPath = './': path to the folder where the different polies are stored.
    """

    listPolies = []
    for indColor, newColor in enumerate(colorsList):

        newPoly = []
        # Run over the tiling:
        for newPoints in toFeedbackSingle('poly'+str(indColor), polyPath=polyPath):
            newPoly += [{'color':newColor, 'points':newPoints}]
        listPolies += [newPoly]
    return listPolies


def transDecomp(namesPath):
    """transDecomp function:

        This function runs over the decomposition of the images given which
        names are given in namesList.
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
    namesList = [name for name in namesList if name != 'README.txt']

    for imgName in namesList:
        imgPath = os.path.join(namesPath, imgName)

        ## 1: produce the files for Triangle:
        colors = toTriangle(polygonsList=None,
                            filePath=imgPath,
                            fileName='polies.json',
                            flagColors=True, flagJson=True);

        ## 2: call Triangle from python:
        # We must call Triangle once for each polygon of the decomposition.
        # To do this, we must know how many polygons there are in the decomposition.
        # Also, later on we will need the colors of each polygon so we can colour
        # the tiling in the right manner. We can solve both problems by reading
        # the colors straightaway from polies.json. Therefore, a flag colors
        # has been added to the 'toTriangle()' function such that if this is True
        # then the colors are returned as well.
        for indColor, color in enumerate(colors):
            sub.call(["triangle", "-p", imgPath+'poly'+str(indColor)+'.poly'])

        ## 3: Back to Feedback Format, which includes a loop over the colors itself:
        newPoliesList = toFeedbackMany(colors, polyPath=imgPath)
        # Writing new polies back into a file:
        f = open(os.path.join(imgPath, 'polies_.json'), 'w')
        json.dump(newPoliesList, f)
        f.close()

        ## 4: Removing files which arn't needed anymore!
        for indColor, color in enumerate(colors):
            sub.call(["rm", imgPath+'poly'+str(indColor)+'.1.ele'])
            sub.call(["rm", imgPath+'poly'+str(indColor)+'.1.node'])
            sub.call(["rm", imgPath+'poly'+str(indColor)+'.1.poly'])
            sub.call(["rm", imgPath+'poly'+str(indColor)+'.poly'])


if __name__ == '__main__':
    expPath = '/Users/dedan/projects/bci/out1/260312_190049/'
    transDecomp(expPath);













