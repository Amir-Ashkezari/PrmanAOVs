from Katana import NodegraphAPI, Utils
from . import ScriptActions as SA


class PrmanAOVsNode(NodegraphAPI.SuperTool):

    def __init__(self):

        self.hideNodegraphGroupControls()
        self.addInputPort('in')
        self.addOutputPort('out')

        preset = SA.getJSON('config/preset.json')
        denoiserList = preset['presetTreeItems'][3]['Denoiser']

        self.buildDisplayParameters()
        self.buildChannelParameters()
        self.getParameters().createChildGroup('noSelection')

        referenceNames = ('os', 'gs_pocd', 'gs_rod')
        internalNodes = ('OpScript', 'GroupStack', 'GroupStack')
        nodeTypes = (
            'OpScript', 'PrmanOutputChannelDefine', 'RenderOutputDefine'
        )
        nodeNames = (
            'PrmanLobesLpe', 'PrmanAOVsChannelDefine', 'AOVsRenderOutputDefine'
        )

        nodes = [NodegraphAPI.CreateNode(n, self) for n in internalNodes]
        for idx, name in enumerate(referenceNames):
            SA.AddNodeReferenceParam(
                self, 'node_{}'.format(name), nodes[idx])

        lastPort = self.getSendPort('in')

        for i, (node, nodeType, nodeName) in \
                enumerate(zip(nodes, nodeTypes, nodeNames)):
            if nodeType == 'OpScript':
                node.setName(nodeName)
                node.getParameter('applyWhere').setValue(
                    'at specific location', 0)
                node.getParameter('location').setValue('/root', 0)
                node.getParameter('script.lua').setValue(SA.lobesLpe, 0)
            else:
                channels = ['Ci', 'a']
                node.setChildNodeType(nodeType)
                node.setName(nodeName)
                if nodeType == 'PrmanOutputChannelDefine':
                    channels.extend(denoiserList)
                    self.createNewChannelFromPreset(channels)
                else:
                    rodNode = self.initNewDisplay('primary')
                    self.setDisplayChannelParam(rodNode, channels)
            NodegraphAPI.SetNodePosition(node, (0, i * -75))
            node.getInputPortByIndex(0).connect(lastPort)
            lastPort = node.getOutputPortByIndex(0)
        lastPort.connect(self.getReturnPort('out'))

    #######################################################################
    # UI parameters
    #######################################################################
    def buildDisplayParameters(self):
        """ Build display parameter """
        displayGrp = self.getParameters().createChildGroup('display')
        displayGrp.createChildString('displayName', '')
        displayGrp.createChildNumber('enable', True)
        displayGrp.createChildString('displayDriver', '')

        dParamGrp = displayGrp.createChildGroup('parameters')
        dParamGrp.createChildNumber('asrgba', True)
        dParamGrp.createChildString('storage', '')
        dParamGrp.createChildString('format', '')
        dParamGrp.createChildString('type', '')
        dParamGrp.createChildString('compression', '')
        dParamGrp.createChildNumber('compressionlevel', 45.0)
        dParamGrp.createChildNumber('quantize', True)
        dParamGrp.createChildString('resolutionunit', '')
        dParamGrp.createChildNumberArray('resolution', 2)
        dParamGrp.createChildString('smode', '')
        dParamGrp.createChildString('tmode', '')

        displayGrp.createChildNumber('denoise', False)
        displayGrp.createChildString('renderLocation', '')

    #######################################################################
    def buildChannelParameters(self):
        """ Build channel parameters """
        channelGrp = self.getParameters().createChildGroup('channel')
        channelGrp.createChildString('channelName', '')
        channelGrp.createChildNumber('enable', True)
        channelGrp.createChildString('type', '')
        channelGrp.createChildString('source', '')

        chAdv = channelGrp.createChildGroup('advanced')
        chAdv.createChildString('filter', '')
        chAdv.createChildNumberArray('filterwidth', 2)
        chAdv.createChildString('statistics', '')
        chAdv.createChildNumber('relativepixelvariance', -1)
        chAdv.createChildNumberArray('remap', 3)

    #######################################################################
    # Internal network
    #######################################################################
    def createNewChannelFromPreset(self, presetChannels, uniqueNames=None):
        """ Create channel from preset """
        preset = SA.getJSON('config/preset.json')

        for idx, channel in enumerate(presetChannels):
            pocdNode = self.initNewChannel(
                uniqueNames[idx] if uniqueNames else channel)
            self.setupChannelParams(
                pocdNode, **preset['channels'][channel])
        return pocdNode

    #######################################################################
    def initNewChannel(self, pocdName):
        """ Initialize new channel """
        Utils.UndoStack.DisableCapture()
        try:
            channelGroupStack = SA.GetRefNode(self, 'gs_pocd')
            pocdNode = channelGroupStack.buildChildNode()
            pocdNode.setName('{}_DisplayChannel'.format(pocdName))
            pocdNode.getParameter('name').setValue(pocdName, 0)
            return pocdNode
        finally:
            Utils.UndoStack.EnableCapture()

    #######################################################################
    def setupChannelParams(self, *args, **kwargs):
        """ Creating and setting parameters """
        Utils.UndoStack.DisableCapture()
        try:
            pocdNode = args[0]
            paramType = {
                'source': 'string', 'filter': 'string', 'filterwidth': 'float',
                'statistics': 'string', 'relativepixelvariance': 'float',
                'remap': 'float'
            }
            for paramName, paramValue in kwargs.items():
                if paramName == 'type':
                    pocdNode.getParameter(paramName).setValue(paramValue, 0)
                    continue
                pocdParams = pocdNode.getParameter('params')
                childParam = pocdParams.getChild(paramName)
                if childParam:
                    pocdParams.deleteChild(childParam)
                if not paramValue:
                    continue
                pocdParam = pocdParams.createChildGroup(paramName)
                pocdParam.createChildString('name', paramName)
                pocdParam.createChildString('type', paramType[paramName])
                if paramName == 'source':
                    pocdParam.createChildString('value', paramValue)
                elif paramName == 'filter':
                    pocdParam.createChildGroup('string')
                    pocdParam.createChildString('value', paramValue)
                elif paramName == 'filterwidth':
                    pocdArrayParm = pocdParam.createChildNumberArray(
                        'value', 2)
                    for idx in xrange(2):
                        childParam = pocdArrayParm.getChildByIndex(idx)
                        childParam.setValue(paramValue[idx], 0)
                elif paramName == 'statistics':
                    pocdParam.createChildGroup('string')
                    pocdParam.createChildString('value', paramValue)
                elif paramName == 'relativepixelvariance':
                    pocdParam.createChildNumber('value', paramValue)
                else:
                    pocdArrayParm = pocdParam.createChildNumberArray(
                        'value', 3)
                    for idx in xrange(3):
                        childParam = pocdArrayParm.getChildByIndex(idx)
                        childParam.setValue(paramValue[idx], 0)
        finally:
            Utils.UndoStack.EnableCapture()

    #######################################################################
    def initNewDisplay(self, rodName):
        """ Initialize new display """
        Utils.UndoStack.DisableCapture()
        try:
            rodGroupStack = SA.GetRefNode(self, 'gs_rod')
            rodNode = rodGroupStack.buildChildNode()
            rodNode.setName('ROD_{}'.format(rodName))
            rodNode.getParameter('outputName').setValue(rodName, 0)

            outputParam = rodNode.getParameter(
                'args.renderSettings.outputs.outputName')
            outputParam.getChild('type.enable').setValue(True, 0)
            outputParam.getChild('type.value').setValue('raw', 0)
            outputParam.getChild('locationType.enable').setValue(True, 0)
            outputParam.getChild('locationType.value').setValue('file', 0)

            rodNode.checkDynamicParameters()

            outputParam.getChild(
                'rendererSettings.channel.enable').setValue(True, 0)
            outputParam.getChild(
                'rendererSettings.channel.value').setValue('', 0)
            outputParam.getChild(
                'rendererSettings.asrgba.enable').setValue(True, 0)

            denoiseParam = outputParam.getChild(
                'rendererSettings').createChildNumber('denoise', 0)
            denoiseParam.setHintString("{'widget': 'null'}")

            return rodNode
        finally:
            Utils.UndoStack.EnableCapture()

    #######################################################################
    def getDisplayChannelParam(self, rodNode):
        """ Get channel parameter of a specific rodNode """
        rootParam = rodNode.getParameter(
            'args.renderSettings.outputs.outputName')
        channelParam = rootParam.getChild('rendererSettings.channel.value')
        channelStr = channelParam.getValue(0)
        channelList = channelStr.split(',') if channelStr else []
        return channelParam, channelList

    #######################################################################
    def setDisplayChannelParam(self, rodNode, channelList):
        """ Set channel parameter of a specific rodNode """
        Utils.UndoStack.DisableCapture()
        try:
            outputParam = rodNode.getParameter(
                'args.renderSettings.outputs.outputName')
            chParam = outputParam.getChild('rendererSettings.channel.value')
            chParam.setValue(str(','.join(channelList)), 0)
        finally:
            Utils.UndoStack.EnableCapture()

    #######################################################################
    def renameNode(self, **kwargs):
        """ Rename node and ites name parameter """
        Utils.UndoStack.OpenGroup(
            'Rename to {}'.format(kwargs.get('nodeNameParam')))
        try:
            node = kwargs.get('nodeToRename')
            uniqueName = kwargs.get('nodeNameParam')
            if node.getType() == 'RenderOutputDefine':
                name = 'outputName'
                node.setName('ROD_{}'.format(uniqueName))
            else:
                name = 'name'
                node.setName('{}_DisplayChannel'.format(uniqueName))

            nameParam = node.getParameter(name)
            nameParam.setValue(uniqueName, 0)

            if kwargs.get('parent'):
                prevNodeName = kwargs.get('prevName')
                channelParam, channelList = \
                    self.getDisplayChannelParam(kwargs['parent'])
                if prevNodeName in channelList:
                    chIdx = channelList.index(prevNodeName)
                    channelList.remove(prevNodeName)
                    channelList.insert(chIdx, uniqueName)
                rodOutputParam = kwargs['parent'].getParameter(
                    'args.renderSettings.outputs.outputName')
                channelParam = rodOutputParam.getChild(
                    'rendererSettings.channel.value')
                paramValue = str(','.join(channelList))
                channelParam.setValue(paramValue, 0)
        finally:
            Utils.UndoStack.CloseGroup()

    #######################################################################
    def findNode(self, nodeName, nodeType):
        """
        Search if a channel/display exist nodeType 0 means search
        the channel groupstack and 1 means search rod groupstack
        """
        if nodeType == 0:
            nameParam = 'name'
            groupStack = SA.GetRefNode(self, 'gs_pocd')
        else:
            nameParam = 'outputName'
            groupStack = SA.GetRefNode(self, 'gs_rod')
        bypassedNodeNames = []
        for child in groupStack.getChildren():
            name = child.getParameter(nameParam).getValue(0)
            if child.isBypassed():
                bypassedNodeNames.append(name)
            if name == nodeName:
                return groupStack, child
        return None, bypassedNodeNames

    #######################################################################
    def deleteNodes(self, channelSet, displaySet):
        """ Delete channel/display nodes """
        Utils.UndoStack.OpenGroup('Delete selected channel/display(s)')
        try:
            pocdGroupStack = SA.GetRefNode(self, 'gs_pocd')
            for pocdNode in pocdGroupStack.getChildren():
                pocdNameParam = pocdNode.getParameter('name').getValue(0)
                if pocdNameParam in channelSet:
                    pocdGroupStack.deleteChildNode(pocdNode)
            rodGroupStack = SA.GetRefNode(self, 'gs_rod')
            for rodNode in rodGroupStack.getChildren():
                rodOutputNameParam = rodNode.getParameter('outputName')
                rodOutputName = rodOutputNameParam.getValue(0)
                if rodOutputName in displaySet:
                    rodGroupStack.deleteChildNode(rodNode)
                else:
                    channelParam, channelList = \
                        self.getDisplayChannelParam(rodNode)
                    if channelList and not channelSet.isdisjoint(channelList):
                        channelList = [
                            channel for channel in channelList
                            if channel not in channelSet]
                        rodOutputParam = rodNode.getParameter(
                            'args.renderSettings.outputs.outputName')
                        channelParam = rodOutputParam.getChild(
                            'rendererSettings.channel.value')
                        paramValue = str(','.join(channelList))
                        channelParam.setValue(paramValue, 0)
        finally:
            Utils.UndoStack.CloseGroup()

    #######################################################################
    def getOutputSetup(self):
        """
        Return a list containing dictionaries of ROD outputName
        and their assigned channels
        """
        preset = SA.getJSON('config/preset.json')
        denoiserList = preset['presetTreeItems'][3]['Denoiser']

        groupStack = SA.GetRefNode(self, 'gs_rod')
        treeList = []
        for child in groupStack.getChildren():
            treeItems = dict()
            key = child.getParameter('outputName').getValue(0)
            rodOutputParam = child.getParameter(
                'args.renderSettings.outputs.outputName')
            channelParm = rodOutputParam.getChild(
                'rendererSettings.channel.value')
            paramValue = channelParm.getValue(0)
            if paramValue:
                treeItems[key] = []
                channelList = paramValue.split(',')
                for channel in channelList:
                    if channel not in denoiserList:
                        treeItems[key].append(channel)
            else:
                treeItems[key] = None
            treeList.append(treeItems)
        return treeList

    #######################################################################
    def addParameterHints(self, attrName, inputDict):
        """ Parameter hints """
        inputDict.update(_ExtraHints.get(attrName, {}))


_ExtraHints = {
    'PrmanAOVs.display': {
        'open': True
    },
    'PrmanAOVs.display.displayName': {
        'widget': 'string', 'readOnly': True
    },
    'PrmanAOVs.display.enable': {
        'widget': 'checkBox', 'constant': True,
        'help': 'Sets the display as renderable or not'
    },
    'PrmanAOVs.display.displayDriver': {
        'widget': 'popup', 'editable': True, 'help': 'Choose '
        'the output file format of the Display Driver, '
        'including Deep Data (DeepEXR)',
        'options': ['openexr', 'deepexr', 'tiff', 'texture',
                    'png', 'targa', 'pointcloud']
    },
    'PrmanAOVs.display.parameters': {
        'open': True,
        'conditionalVisOps':
            {'conditionalVisOp': 'and',
             'conditionalVisLeft': 'conditionalVis1',
             'conditionalVisRight': 'conditionalVis2',
             'conditionalVis1Op': 'notEqualTo',
             'conditionalVis1Path': '../displayDriver',
             'conditionalVis1Value': 'it',
             'conditionalVis2Op': 'notEqualTo',
             'conditionalVis2Path': '../displayDriver',
             'conditionalVis2Value': 'pointcloud'}
    },
    'PrmanAOVs.display.parameters.asrgba': {
        'widget': 'checkBox', 'constant': True,
        'help': 'Orders Channels as RGBA order',
        'conditionalVisOps':
            {'conditionalVisOp': 'or',
             'conditionalVisLeft': 'conditionalVis1',
             'conditionalVisRight': 'conditionalVis2',
             'conditionalVis1Op': 'equalTo',
             'conditionalVis1Path': '../../displayDriver',
             'conditionalVis1Value': 'openexr',
             'conditionalVis2Op': 'equalTo',
             'conditionalVis2Path': '../../displayDriver',
             'conditionalVis2Value': 'deepexr'}
    },
    'PrmanAOVs.display.parameters.storage': {
        'widget': 'popup', 'help': 'Stored as a scanline/tiled format.',
        'options': ['scanline', 'tiled'],
        'conditionalVisOps':
            {'conditionalVisOp': 'or',
             'conditionalVisLeft': 'conditionalVis1',
             'conditionalVisRight': 'conditionalVis2',
             'conditionalVis1Op': 'equalTo',
             'conditionalVis1Path': '../../displayDriver',
             'conditionalVis1Value': 'openexr',
             'conditionalVis2Op': 'equalTo',
             'conditionalVis2Path': '../../displayDriver',
             'conditionalVis2Value': 'deepexr'}
    },
    'PrmanAOVs.display.parameters.type': {
        'widget': 'popup', 'help': 'Typically Half is good enough for color '
        'AOVs and passes. Float is recommended for Data AOVs and passes like '
        'Z depth or P. OpenEXR does not support lower bit depths.',
        'conditionalVisOps':
            {'conditionalVisOp': 'or',
             'conditionalVisLeft': 'conditionalVis1',
             'conditionalVisRight': 'conditionalVis2',
             'conditionalVis1Op': 'or',
             'conditionalVis1Left': 'conditionalVis3',
             'conditionalVis1Right': 'conditionalVis4',
             'conditionalVis2Op': 'equalTo',
             'conditionalVis2Path': '../../displayDriver',
             'conditionalVis2Value': 'openexr',
             'conditionalVis3Op': 'equalTo',
             'conditionalVis3Path': '../../displayDriver',
             'conditionalVis3Value': 'deepexr',
             'conditionalVis4Op': 'equalTo',
             'conditionalVis4Path': '../../displayDriver',
             'conditionalVis4Value': 'texture'}
    },
    'PrmanAOVs.display.parameters.compression': {
        'widget': 'popup', 'help': 'ZIPS is default and recommended for '
        'compositing workflow as it is stored as a single scanline.',
        'conditionalVisOps':
            {'conditionalVisOp': 'and',
             'conditionalVisLeft': 'conditionalVis1',
             'conditionalVisRight': 'conditionalVis2',
             'conditionalVis1Op': 'and',
             'conditionalVis1Left': 'conditionalVis3',
             'conditionalVis1Right': 'conditionalVis4',
             'conditionalVis2Op': 'notEqualTo',
             'conditionalVis2Path': '../../displayDriver',
             'conditionalVis2Value': 'png',
             'conditionalVis3Op': 'notEqualTo',
             'conditionalVis3Path': '../../displayDriver',
             'conditionalVis3Value': 'targa',
             'conditionalVis4Op': 'notEqualTo',
             'conditionalVis4Path': '../../displayDriver',
             'conditionalVis4Value': 'pointcloud'}
    },
    'PrmanAOVs.display.parameters.compressionlevel': {
        'widget': 'number', 'constant': True, 'min': 0,
        'help': 'How much the data is compacted, for lossy '
        'schemes (such as DWAA) this may degrade final images.',
        'conditionalVisOps':
            {'conditionalVisOp': 'or',
             'conditionalVisLeft': 'conditionalVis1',
             'conditionalVisRight': 'conditionalVis2',
             'conditionalVis1Op': 'equalTo',
             'conditionalVis1Path': '../../displayDriver',
             'conditionalVis1Value': 'openexr',
             'conditionalVis2Op': 'equalTo',
             'conditionalVis2Path': '../../displayDriver',
             'conditionalVis2Value': 'texture'}
    },
    'PrmanAOVs.display.parameters.quantize': {
        'widget': 'checkBox', 'constant': True,
        'help': 'This option attempts to compress the '
        'color scheme to shrink the file size.',
        'conditionalVisOps':
            {'conditionalVisOp': 'or',
             'conditionalVisLeft': 'conditionalVis1',
             'conditionalVisRight': 'conditionalVis2',
             'conditionalVis1Op': 'or',
             'conditionalVis1Left': 'conditionalVis3',
             'conditionalVis1Right': 'conditionalVis4',
             'conditionalVis2Op': 'equalTo',
             'conditionalVis2Path': '../../displayDriver',
             'conditionalVis2Value': 'tiff',
             'conditionalVis3Op': 'equalTo',
             'conditionalVis3Path': '../../displayDriver',
             'conditionalVis3Value': 'png',
             'conditionalVis4Op': 'equalTo',
             'conditionalVis4Path': '../../displayDriver',
             'conditionalVis4Value': 'targa'}
    },
    'PrmanAOVs.display.parameters.format': {
        'widget': 'popup', 'help': 'Texture format.',
        'conditionalVisOps':
            {'conditionalVisOp': 'or',
             'conditionalVisLeft': 'conditionalVis1',
             'conditionalVisRight': 'conditionalVis2',
             'conditionalVis1Op': 'equalTo',
             'conditionalVis1Path': '../../displayDriver',
             'conditionalVis1Value': 'tiff',
             'conditionalVis2Op': 'equalTo',
             'conditionalVis2Path': '../../displayDriver',
             'conditionalVis2Value': 'texture'}
    },
    'PrmanAOVs.display.parameters.resolutionunit': {
        'widget': 'popup', 'help': 'Select between inches '
        'and centimeters or none.',
        'options': ['none', 'centimeters', 'inches'],
        'conditionalVisOps':
            {'conditionalVisOp': 'equalTo',
             'conditionalVisPath': '../../displayDriver',
             'conditionalVisValue': 'tiff'}
    },
    'PrmanAOVs.display.parameters.resolution': {
        'widget': 'numberArray', 'constant': True,
        'help': 'The number of pixels per Resolution Unit '
        '(above) in the ImageWidth and ImageHeight direction.',
        'conditionalVisOps':
            {'conditionalVisOp': 'equalTo',
             'conditionalVisPath': '../../displayDriver',
             'conditionalVisValue': 'tiff'}
    },
    'PrmanAOVs.display.parameters.smode': {
        'widget': 'popup', 'help': 'S Wrap Modes.',
        'options': ['black', 'clamp', 'periodic'],
        'conditionalVisOps':
            {'conditionalVisOp': 'equalTo',
             'conditionalVisPath': '../../displayDriver',
             'conditionalVisValue': 'texture'}
    },
    'PrmanAOVs.display.parameters.tmode': {
        'widget': 'popup', 'help': 'T Wrap Modes.',
        'options': ['black', 'clamp', 'periodic'],
        'conditionalVisOps':
            {'conditionalVisOp': 'equalTo',
             'conditionalVisPath': '../../displayDriver',
             'conditionalVisValue': 'texture'}
    },
    'PrmanAOVs.display.denoise': {
        'widget': 'checkBox', 'constant': True,
        'help': 'Enable denoising for this chosen Display.'
    },
    'PrmanAOVs.display.renderLocation': {
        'widget': 'assetIdOutput',
        'help': 'Specify an output location'
    },
    'PrmanAOVs.channel': {
        'open': True
    },
    'PrmanAOVs.channel.channelName': {
        'widget': 'string', 'readOnly': True
    },
    'PrmanAOVs.channel.enable': {
        'widget': 'checkBox', 'constant': True,
        'help': 'Sets the channel as renderable or not.'
    },
    'PrmanAOVs.channel.type': {
        'widget': 'popup', 'help': 'Type of channel output',
        'options': ['color', 'float', 'point', 'normal', 'vector']
    },
    'PrmanAOVs.channel.source': {
        'widget': 'string', 'help': 'This is the source of the AOV, '
        'typically where one would specify an LPE for rendering.'
    },
    'PrmanAOVs.channel.advanced': {
        'open': True
    },
    'PrmanAOVs.channel.advanced.filter': {
        'widget': 'popup', 'help': 'You can use this section to '
        'override the specified filter. For most color data the '
        'inherited filter is best to match the other AOVs, but '
        'for data, you may wish to use one of the listed min, '
        'max, zmin, zmax, etc filters to avoid filtering across '
        'object edges.',
        'options': [
            'inherit from display', 'box', 'triangle', 'catmull-rom',
            'sinc', 'gaussian', 'mitchell', 'separable-catmull-rom',
            'blackman-harris', 'lanczos', 'bessel', 'disk', 'min',
            'max', 'average', 'zmin', 'zmax', 'sum'
        ]
    },
    'PrmanAOVs.channel.advanced.filterwidth': {
        'panelWidget': 'numberArray', 'min': -1,
        'constant': True, 'help': 'Here you '
        'can change the filter width for this channel. Note that '
        'using a different width may mean they will not line up '
        'or match the other AOVs.'
    },
    'PrmanAOVs.channel.advanced.statistics': {
        'widget': 'popup', 'help': 'These options are not meant for '
        'artists specifically, they are useful options for pipeline '
        'considerations or possibly denoise applications outside the '
        'renderer and their usage is not required. They are exposed '
        'as useful tools for the pipeline so that you do not have '
        'to alter RIB files directly.', 'options': [
            '', 'variance', 'mse', 'even', 'odd'
        ]
    },
    'PrmanAOVs.channel.advanced.relativepixelvariance': {
        'widget': 'number', 'constant': True, 'min': -1,
        'help': 'Define a pixel variance for this specific channel.'
    },
    'PrmanAOVs.channel.advanced.remap': {
        'panelWidget': 'numberArray', 'constant': True,
        'help': """
        Break Point, A value below which the color is
        unchanged, must be non-negative (a). Max Value, The
        max value contained, at 0 all remapping is off. This
        cannot be less than the Break Point value. (b)
        Smoothness, A tweak to the second derivative at the
        breakpoint (the function is C(1) unless  a==b , so
        you don't get to specify the first derivative.
        If this parameter is 1, the function is C(2).
        Smaller values make it flatter, larger ones make
        it less flat. If it is bigger than ~2.5, the curve
        has an inflection point - it curves up on the right
        of the breakpoint. It is illegal to set c <= 0,
        and it is not recommended to set it to anything
        other than 1. The default value is 0.
        """
    }
}
