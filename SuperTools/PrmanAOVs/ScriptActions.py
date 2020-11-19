from Katana import NodegraphAPI
import json
import os


def AddNodeReferenceParam(destNode, paramName, node):
    param = destNode.getParameter(paramName)
    if not param:
        param = destNode.getParameters().createChildString(paramName, '')

    param.setExpression('getNode(%r).getNodeName()' % node.getName())


def GetRefNode(gnode, key):
    p = gnode.getParameter('node_' + key)
    if not p:
        return None
    return NodegraphAPI.GetNode(p.getValue(0))


def getJSON(relativeFilePath):
    curDir = os.path.dirname(__file__)
    jsonFile = os.path.join(curDir, relativeFilePath)
    with open(jsonFile) as f:
        contents = jsonLoad(f)
    return contents


def jsonLoad(file_handle):
    """
    We use this method mainly to convert json ascii format to
    python string
    """
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )


def _byteify(data, ignore_dicts=False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return dict((
            _byteify(key, ignore_dicts=True),
            _byteify(value, ignore_dicts=True)
        ) for key, value in data.iteritems())
    # if it's anything else, return it in its original form
    return data


lobesLpe = """
Interface.SetAttr('prmanGlobalStatements.options.lpe.diffuse2', StringAttribute("Diffuse,HairDiffuse"))
Interface.SetAttr('prmanGlobalStatements.options.lpe.diffuse3', StringAttribute("Subsurface"))
Interface.SetAttr('prmanGlobalStatements.options.lpe.specular2', StringAttribute("Specular,HairSpecularR"))
Interface.SetAttr('prmanGlobalStatements.options.lpe.specular3', StringAttribute("RoughSpecular,HairSpecularTRT"))
Interface.SetAttr('prmanGlobalStatements.options.lpe.specular4', StringAttribute("Clearcoat"))
Interface.SetAttr('prmanGlobalStatements.options.lpe.specular5', StringAttribute("Iridescence"))
Interface.SetAttr('prmanGlobalStatements.options.lpe.specular6', StringAttribute("Fuzz,HairSpecularGLINTS"))
Interface.SetAttr('prmanGlobalStatements.options.lpe.specular7', StringAttribute("SingleScatter,HairSpecularTT"))
Interface.SetAttr('prmanGlobalStatements.options.lpe.specular8', StringAttribute("Glass"))
Interface.SetAttr('prmanGlobalStatements.options.lpe.user2', StringAttribute("Albedo,DiffuseAlbedo,SubsurfaceAlbedo,HairAlbedo"))
Interface.SetAttr('prmanGlobalStatements.options.lpe.user3', StringAttribute("Position"))
Interface.SetAttr('prmanGlobalStatements.options.lpe.user4', StringAttribute("UserColor"))
Interface.SetAttr('prmanGlobalStatements.options.lpe.user6', StringAttribute("Normal,DiffuseNormal,HairTangent,SubsurfaceNormal,SpecularNormal,RoughSpecularNormal,SingleScatterNormal,FuzzNormal,IridescenceNormal,GlassNormal"))
"""
