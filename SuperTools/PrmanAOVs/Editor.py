from Katana import QtCore, QtGui, UI4, Utils, QT4Widgets
from Katana import FormMaster, QtWidgets
from Katana import NodegraphAPI
import ScriptActions as SA
import re


class TreeWidget(QT4Widgets.SortableTreeWidget):
    """
    A class for preset / display tree widgets
    """

    def __init__(self, parent, node, selectionModel):

        QT4Widgets.SortableTreeWidget.__init__(self, parent)
        self.__node = node
        self.__selectionModel = selectionModel

        self.setSortingEnabled(False)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setSelectionMode(self.__selectionModel)
        self.setHeaderHidden(True)
        self.setAllColumnsShowFocus(True)

    def mousePressEvent(self, event):
        """
        Suppress right click from any action to the tree
        including selecting any items
        """
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.RightButton:
                return
            else:
                super(TreeWidget, self).mousePressEvent(event)

    def addTreeItems(self, **kwargs):
        """ Add items to tree widget, displays will have channel as their childs """
        # itemPairList, parentItem, editable, selectedItem
        treeWidgetItem = QT4Widgets.SortableTreeWidgetItem
        itemFlags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
            QtCore.Qt.ItemIsEditable

        for itemPair in kwargs.get('itemPairList'):
            displayName = str(itemPair.keys()[0])
            self.__displayItem = treeWidgetItem(kwargs.get('parentItem'))
            self.__displayItem.setText(0, displayName)
            self.__displayItem.setData(
                0, QtCore.Qt.UserRole, (1, displayName))
            if kwargs.get('editable'):
                self.__displayItem.setFlags(itemFlags)
            else:
                self.__displayItem.setFlags(QtCore.Qt.ItemIsEnabled)
            self.__displayItem.setExpanded(True)
            if itemPair.values()[0]:
                for itemList in itemPair.values():
                    for item in itemList:
                        self.__channelItem = treeWidgetItem(
                            self.__displayItem)
                        self.__channelItem.setText(0, str(item))
                        self.__channelItem.setData(
                            0, QtCore.Qt.UserRole, (0, str(item)))
                        if kwargs.get('editable'):
                            self.__channelItem.setFlags(itemFlags)

        # Decorate tree items based on their attributes
        bypassedChannels, bypassedDisplays = [], []
        bypassedChannels.extend(self.__node.findNode('', 0)[1])
        bypassedDisplays.extend(self.__node.findNode('', 1)[1])

        brush = QtGui.QBrush(QtGui.QColor(110, 110, 110))
        brush.setStyle(QtCore.Qt.NoBrush)
        iteratorClass = QtWidgets.QTreeWidgetItemIterator
        iterator = iteratorClass(kwargs['parentItem'], iteratorClass.All)
        while iterator.value():
            font = QtGui.QFont()
            item = iterator.value()
            try:
                itemData = item.data(0, QtCore.Qt.UserRole)
                itemType = itemData[0]
            except TypeError:
                break
            else:
                if kwargs.get('itemToSelect') is not None and \
                        itemData == kwargs.get('itemToSelect'):
                    item.setSelected(True)
                if itemType == 0:
                    font.setItalic(True)
                    if item.text(0) in bypassedChannels:
                        item.setForeground(0, brush)
                        font.setStrikeOut(True)
                    item.setFont(0, font)
                elif itemType == 1:
                    if item.text(0) in bypassedDisplays:
                        item.setForeground(0, brush)
                        font.setStrikeOut(True)
                        item.setFont(0, font)
            iterator += 1
        return self.__displayItem, self.__channelItem


class AOVWidgets(QtWidgets.QWidget):
    '''
    This class holds the aovs widgets
    '''

    def __init__(self, parent, node):

        QtWidgets.QWidget.__init__(self, parent)
        self.__node = node

        self.preset = SA.getJSON('config/preset.json')

        #######################################################################
        # creating layout for preset side
        presetLblQHLayout = QtWidgets.QHBoxLayout()
        presetSendBtnQHLayout = QtWidgets.QHBoxLayout()

        # preset side widgets
        presetLabel = self.addLabel('AvailableChannels')

        presetLabelSpacerItem = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)

        self.presetFilterLineEdit = self.addLineEdit('Search...')

        self.presetTreeWidget = TreeWidget(
            self, self.__node,
            QT4Widgets.SortableTreeWidget.ExtendedSelection)

        self.sendPresetBtn = self.addPushButton(
            False, 'Create a new Channel from preset', '>>')

        # set layout for preset side
        presetLblQHLayout.addWidget(presetLabel)
        presetLblQHLayout.addItem(presetLabelSpacerItem)
        presetSendBtnQHLayout.addWidget(self.sendPresetBtn)

        #######################################################################
        # creating layout for display tree
        displayLblQHLayout = QtWidgets.QHBoxLayout()
        displayBtnsQHLayout = QtWidgets.QHBoxLayout()

        displayLabel = self.addLabel('Displays')

        displayLabelSpacerItem = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)

        self.displayFilterLineEdit = self.addLineEdit('Search...')

        self.displayTreeWidget = TreeWidget(
            self, self.__node, QT4Widgets.SortableTreeWidget.ExtendedSelection)

        self.addDisplayBtn = self.addPushButton(
            True, 'Create a new display/channel', '+')

        self.removeDisplayBtn = self.addPushButton(
            False, 'Remove selected display/channel(s)', '-')

        # set layout for display side
        displayLblQHLayout.addWidget(displayLabel)
        displayLblQHLayout.addItem(displayLabelSpacerItem)
        displayBtnsQHLayout.addWidget(self.addDisplayBtn)
        displayBtnsQHLayout.addWidget(self.removeDisplayBtn)

        # main layout
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addLayout(presetLblQHLayout, 0, 0, 1, 1)
        mainLayout.addWidget(self.presetFilterLineEdit, 1, 0, 1, 1)
        mainLayout.addWidget(self.presetTreeWidget, 2, 0, 1, 1)
        mainLayout.addLayout(presetSendBtnQHLayout, 3, 0, 1, 1)
        mainLayout.addLayout(displayLblQHLayout, 0, 1, 1, 1)
        mainLayout.addWidget(self.displayFilterLineEdit, 1, 1, 1, 1)
        mainLayout.addWidget(self.displayTreeWidget, 2, 1, 1, 1)
        mainLayout.addLayout(displayBtnsQHLayout, 3, 1, 1, 1)
        self.setLayout(mainLayout)

    def addLabel(self, labelText):
        label = QtWidgets.QLabel(self)
        label.setEnabled(False)
        label.setText(labelText)
        return label

    def addLineEdit(self, linePlcHldText):
        lineEdit = QtWidgets.QLineEdit(self)
        lineEdit.setPlaceholderText(linePlcHldText)
        return lineEdit

    def addPushButton(self, btnEnableMode, btnToolTip, btnText):
        pushButton = QtWidgets.QPushButton(self)
        pushButton.setEnabled(btnEnableMode)
        pushButton.setToolTip(btnToolTip)
        pushButton.setText(str(btnText))
        return pushButton


class DisplayParametersWidget(QtWidgets.QWidget):
    '''
    Class for display settings
    '''

    def __init__(self, parent, node, itemData):

        QtWidgets.QWidget.__init__(self, parent)

        self.preset = SA.getJSON('config/preset.json')

        self.__node = node
        itemType, self.itemName = itemData[0], itemData[1]
        self.rodNode = self.__node.findNode(self.itemName, itemType)[1]

        rodOutputName = 'args.renderSettings.outputs.outputName'
        self.rodOutputName = self.rodNode.getParameter(rodOutputName)

        # Setup parameters
        CreateParameterPolicy = UI4.FormMaster.CreateParameterPolicy

        self.dspGrpParam = self.__node.getParameter('display')
        displayGrpPolicy = CreateParameterPolicy(None, self.dspGrpParam)

        self.updateParameters()

        self.nodeParamsPolicy = {}
        for paramName in self.preset['displayParams']:
            nodeParam = self.dspGrpParam.getChild(paramName)
            paramPolicy = CreateParameterPolicy(None, nodeParam)
            paramPolicy.addCallback(self.paramsChangedCallback)
            self.nodeParamsPolicy[nodeParam] = paramPolicy

        # Update parameter hints
        self.setParamsHints()

        # Build widgets out of the parameters policy
        widgetFactory = UI4.FormMaster.KatanaWidgetFactory
        self.displayGrpWidget = widgetFactory.buildWidget(
            self, displayGrpPolicy)

        # Set layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.displayGrpWidget)
        self.setLayout(mainLayout)

    def updateParameters(self):
        """ Get and set parameters from rod to UI """
        Utils.UndoStack.DisableCapture()
        try:
            nameParam = self.dspGrpParam.getChild('displayName')
            nameParam.setValue(self.itemName, 0)

            nodeParamNames = self.preset['displayParams']
            rodParamNames = self.preset['rodParams']
            for nodeParamName, rodParamName in zip(
                    nodeParamNames, rodParamNames):
                nodeParam = self.dspGrpParam.getChild(nodeParamName)
                rodParam = self.rodOutputName.getChild(rodParamName)
                if nodeParamName == 'enable':
                    nodeParam.setValue(not self.rodNode.isBypassed(), 0)
                    continue
                try:
                    if rodParam.getNumChildren():
                        for i, childParam in enumerate(
                                rodParam.getChildren()):
                            paramValue = childParam.getValue(0)
                            child = nodeParam.getChildByIndex(i)
                            child.setValue(paramValue, 0)
                        continue
                except Exception:
                    return
                nodeParam.setValue(rodParam.getValue(0), 0)
        finally:
            Utils.UndoStack.EnableCapture()

    def setParamsHints(self):
        """ Reseting parameter hints """
        Utils.UndoStack.DisableCapture()
        try:
            dspDriverParam = self.dspGrpParam.getChild('displayDriver')
            formatParam = self.dspGrpParam.getChild('parameters.format')
            typeParam = self.dspGrpParam.getChild('parameters.type')
            compParam = self.dspGrpParam.getChild('parameters.compression')

            typeHints = {'options': ['half', 'float']}
            compHints = {'options': [
                'none', 'rle', 'zip', 'zips', 'piz', 'pixar',
                'b44', 'b44a', 'dwaa', 'dwab']}
            formatHints = {'options': ['uint8', 'uint16', 'float32']}

            dDriverValue = dspDriverParam.getValue(0)

            if dDriverValue == 'deepexr':
                compHints = {'options': ['none', 'rle', 'zips']}
            elif dDriverValue == 'tiff':
                compHints = {'options': [
                    'none', 'lzw', 'packbits', 'deflate', 'pixarlog']}
            elif dDriverValue == 'texture':
                formatHints = {'options': ['pixar', 'openexr', 'tiff']}
                if formatParam.getValue(0) != 'openexr':
                    typeHints = {'options': ['byte', 'short', 'float']}
                    if formatParam.getValue(0) == 'pixar':
                        compHints = {'options': ['none', 'lossless', 'lossy']}
                    else:
                        compHints = {'options': ['lzw']}

            formatParam.setHintString(repr(formatHints))
            typeParam.setHintString(repr(typeHints))
            compParam.setHintString(repr(compHints))
        finally:
            Utils.UndoStack.EnableCapture()

    def updateDenoiserChannels(self, paramValue):
        """ Add or remove denoiser channels to display """
        Utils.UndoStack.DisableCapture()
        try:
            denoiserList = self.preset['presetTreeItems'][3]['Denoiser']
            channalParam = self.rodOutputName.getChild(
                'rendererSettings.channel.value').getValue(0)
            channelList = channalParam.split(',') if channalParam else []
            if paramValue:
                for channel in denoiserList:
                    if channel not in channelList:
                        channelList.append(channel)
            else:
                channelList = [ch for ch in channelList
                               if ch not in denoiserList]
            self.__node.setDisplayChannelParam(self.rodNode, channelList)
        finally:
            Utils.UndoStack.EnableCapture()

    def paramsChangedCallback(self, *args, **kwargs):
        """ Set a display type """
        Utils.UndoStack.DisableCapture()
        try:
            policy = args[0].getPolicy()
            paramName = policy.getName()
            paramValue = policy.getValue()

            if paramName == 'enable':
                self.rodNode.setBypassed(not paramValue)
                return

            self.setParamsHints()

            rodEnableParam = 'rendererSettings.%s.enable' % paramName
            rodValueParam = 'rendererSettings.%s.value' % paramName
            if paramName == 'denoise':
                rodValueParam = 'rendererSettings.%s' % paramName
                self.updateDenoiserChannels(paramValue)
                rodParamValue = self.rodOutputName.getChild(rodValueParam)
                rodParamValue.setValue(paramValue, 0)
                return
            elif paramName == 'renderLocation':
                rodEnableParam = 'locationSettings.%s.enable' % paramName
                rodValueParam = 'locationSettings.%s.value' % paramName

            rodEnable = self.rodOutputName.getChild(rodEnableParam)
            rodEnable.setValue(True, 0)
            rodValue = self.rodOutputName.getChild(rodValueParam)

            if policy.getArrayChildren():
                for i, childParam in enumerate(policy.getArrayChildren()):
                    paramValue = childParam.getValue()
                    rodValue.getChildByIndex(i).setValue(paramValue, 0)
                return

            rodValue.setValue(paramValue, 0)
        finally:
            Utils.UndoStack.EnableCapture()


class ChannelParametersWidget(QtWidgets.QWidget):
    '''
    Class for channel settings
    '''

    def __init__(self, parent, node, itemData):

        QtWidgets.QWidget.__init__(self, parent)

        self.preset = SA.getJSON('config/preset.json')

        self.__node = node
        itemType, self.itemName = itemData[0], itemData[1]
        self.pocdNode = self.__node.findNode(self.itemName, itemType)[1]
        self.pocdRootParam = self.pocdNode.getParameters()

        # create parameters policy
        CreateParameterPolicy = UI4.FormMaster.CreateParameterPolicy

        self.chGrpParam = self.__node.getParameter('channel')
        channelGrpPolicy = CreateParameterPolicy(None, self.chGrpParam)

        self.updateParameters()

        self.nodeParamsPolicy = {}
        for paramName in self.preset['channelParams']:
            nodeParam = self.chGrpParam.getChild(paramName)
            paramPolicy = CreateParameterPolicy(None, nodeParam)
            paramPolicy.addCallback(self.paramsChangedCallback)
            self.nodeParamsPolicy[nodeParam] = paramPolicy

        # build widget out of parameters policy
        widgetFactory = UI4.FormMaster.KatanaWidgetFactory
        channelGrpWidget = widgetFactory.buildWidget(
            self, channelGrpPolicy)

        # layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(channelGrpWidget)
        self.setLayout(mainLayout)

    def updateParameters(self):
        """ Get and set parameters from channel to UI """
        Utils.UndoStack.DisableCapture()
        try:
            channelNameParam = self.chGrpParam.getChild('channelName')
            channelNameParam.setValue(self.itemName, 0)

            nodeParamNames = self.preset['channelParams']
            pocdParamNames = self.preset['pocdParams']
            for nodeParamName, pocdParamName in zip(
                    nodeParamNames, pocdParamNames):
                nodeParam = self.chGrpParam.getChild(nodeParamName)
                pocdParam = self.pocdRootParam.getChild(pocdParamName)
                if nodeParamName == 'enable':
                    nodeParam.setValue(not self.pocdNode.isBypassed(), 0)
                    continue
                if pocdParam:
                    if pocdParam.getNumChildren():
                        for i, childParam in enumerate(
                                pocdParam.getChildren()):
                            paramValue = childParam.getValue(0)
                            child = nodeParam.getChildByIndex(i)
                            child.setValue(paramValue, 0)
                        continue
                    paramValue = pocdParam.getValue(0)
                else:
                    paramValue = ''
                    if nodeParam.getName() == 'filter':
                        paramValue = 'inherit from display'
                    elif nodeParam.getName() == 'relativepixelvariance':
                        paramValue = -1
                    elif nodeParam.getNumChildren():
                        for i, childParam in enumerate(nodeParam.getChildren()):
                            nodeParam.getChildByIndex(i).setValue(
                                -1 if nodeParam.getName() == 'filterwidth' else 0, 0)
                        continue
                nodeParam.setValue(paramValue, 0)
        finally:
            Utils.UndoStack.EnableCapture()

    def paramsChangedCallback(self, *args, **kwargs):
        """ Set channel specific param """
        Utils.UndoStack.DisableCapture()
        try:
            policy = args[0].getPolicy()
            paramName = policy.getName()
            paramValue = policy.getValue()

            if paramName == 'enable':
                self.pocdNode.setBypassed(not paramValue)
                return

            if paramName == 'filter':
                if paramValue == 'inherit from display':
                    paramValue = None
            elif paramName == 'filterwidth':
                if (paramValue[0] < 0 or paramValue[1] < 0):
                    paramValue = None
            elif paramName == 'relativepixelvariance':
                if paramValue < 0:
                    paramValue = None
            elif paramName == 'remap':
                if paramValue == [0, 0, 0]:
                    paramValue = None
            paramPair = {paramName: paramValue}
            self.__node.setupChannelParams(self.pocdNode, **paramPair)
        finally:
            Utils.UndoStack.EnableCapture()


class PrmanAOVsEditor(QtWidgets.QWidget):
    """
    This is main UI containg katana factory widgets and Qt custom widgets
    """

    def __init__(self, parent, node):

        QtWidgets.QWidget.__init__(self, parent)

        self.__frozen = True
        self.__updateTreeOnIdle = False
        self.__itemToSelect = None
        self.__node = node
        self.preset = SA.getJSON('config/preset.json')

        self.__rodOutputName = 'args.renderSettings.outputs.outputName'
        self.__iteratorClass = QtWidgets.QTreeWidgetItemIterator

        # create custom widgets
        self.__AOVWidgets = AOVWidgets(self, self.__node)

        self.__presetFilter = self.__AOVWidgets.presetFilterLineEdit
        self.__presetTree = self.__AOVWidgets.presetTreeWidget
        self.__presetTree.addTreeItems(
            itemPairList=self.preset['presetTreeItems'],
            parentItem=self.__presetTree, editable=False,
            itemToSelect=None)
        self.__sendPreset = self.__AOVWidgets.sendPresetBtn

        self.__displayFilter = self.__AOVWidgets.displayFilterLineEdit
        self.__displayTree = self.__AOVWidgets.displayTreeWidget

        treeList = self.__node.getOutputSetup()
        self.__displayTree.addTreeItems(
            itemPairList=treeList, parentItem=self.__displayTree,
            editable=True, itemToSelect=None)
        self.__addDisplay = self.__AOVWidgets.addDisplayBtn
        self.__removeDisplay = self.__AOVWidgets.removeDisplayBtn

        self.__rootItem = self.__displayTree.invisibleRootItem()

        #######################################################################
        # signals
        #######################################################################
        self.__presetFilter.textChanged.connect(
            lambda: self.searchTreeItemsEvent(
                self.__presetTree, self.__presetFilter.text()))

        self.__presetTree.itemSelectionChanged.connect(
            lambda: self.treeSelChangedEvent(
                self.__presetTree, self.__sendPreset))

        self.__presetTree.customContextMenuRequested.connect(
            lambda: self.treeContextMenu(self.__presetTree))

        self.__sendPreset.clicked.connect(self.sendButtonEvent)

        self.__displayFilter.textChanged.connect(
            lambda: self.searchTreeItemsEvent(
                self.__displayTree, self.__displayFilter.text()))

        self.__displayTree.itemSelectionChanged.connect(
            lambda: self.treeSelChangedEvent(
                self.__displayTree, self.__removeDisplay))

        self.__displayTree.itemChanged.connect(self.itemChangedEvent)

        self.__displayTree.customContextMenuRequested.connect(
            lambda: self.treeContextMenu(self.__displayTree))

        self.__addDisplay.clicked.connect(self.addButtonEvent)
        self.__removeDisplay.clicked.connect(self.removeButtonEvent)

        # Create a layout and add the parameter widgets
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.__AOVWidgets)
        mainLayout.addWidget(UI4.Widgets.VBoxLayoutResizer(
            self.__AOVWidgets, 300, 200))
        mainLayout.addSpacing(1)
        # display or channel layout
        self.__parameterWidgetLayout = QtWidgets.QVBoxLayout()
        self.__updateParametersWidget()
        mainLayout.addLayout(self.__parameterWidgetLayout)
        mainLayout.addStretch()
        # Apply the layout to the widget
        self.setLayout(mainLayout)

    #######################################################################
    # **Editor methods
    #######################################################################
    def __updateTreeContents(self):
        """ Update tree contents based on user actions """
        treeWidget = self.__displayTree
        treeWidget.clear()
        treeList = self.__node.getOutputSetup()
        treeWidget.addTreeItems(itemPairList=treeList,
                                parentItem=treeWidget, editable=True,
                                itemToSelect=self.__itemToSelect)
        self.__itemToSelect = None

    #######################################################################
    def __updateParametersWidget(self):
        """ Reconstruct parameter widget """
        treeWidget = self.__displayTree
        while self.__parameterWidgetLayout.count():
            layoutItem = self.__parameterWidgetLayout.takeAt(0)
            if isinstance(layoutItem, QtWidgets.QWidgetItem):
                widget = layoutItem.widget()
                widget.deleteLater()

        selectedItems = treeWidget.selectedItems()
        if selectedItems:
            itemData = selectedItems[0].data(0, QtCore.Qt.UserRole)
            if itemData[0] == 0:
                parametersWidget = ChannelParametersWidget(
                    self, self.__node, itemData)
            else:
                parametersWidget = DisplayParametersWidget(
                    self, self.__node, itemData)
        else:
            CreateParameterPolicy = UI4.FormMaster.CreateParameterPolicy
            noSelParam = self.__node.getParameter('noSelection')
            noSelParamPolicy = CreateParameterPolicy(None, noSelParam)
            widgetFactory = UI4.FormMaster.KatanaWidgetFactory
            parametersWidget = widgetFactory.buildWidget(
                self, noSelParamPolicy)

        self.__parameterWidgetLayout.addWidget(parametersWidget)

    #######################################################################
    def __itemVisibility(self, treeWidget, hide):
        """
        Iterate throught treeWidget items and
        set visiblity according to args
        """
        iteratorFlag = self.__iteratorClass.All
        iterator = self.__iteratorClass(treeWidget, iteratorFlag)
        while iterator.value():
            item = iterator.value()
            item.setHidden(hide)
            iterator += 1

    #######################################################################
    def __uniquifyName(self, name, type):
        """
        type 0 means search the channel groupstack
        and 1 means search display groupstack
        """
        name = name.replace(' ', '_')
        if re.match("[a-zA-Z0-9_]+$", name):
            found = self.__node.findNode(name, type)[0]
            if found:
                text = '{}_dup'.format(name)
                return self.__uniquifyName(text, type)
            else:
                return name
        else:
            return self.__uniquifyName('untitled', type)

    #######################################################################
    # thaw/freeze UI, Event handlers
    #######################################################################
    def showEvent(self, event):
        QtWidgets.QWidget.showEvent(self, event)
        if self.__frozen:
            self.__frozen = False
            self._thaw()

    def hideEvent(self, event):
        QtWidgets.QWidget.hideEvent(self, event)
        if not self.__frozen:
            self.__frozen = True
            self._freeze()

    def _thaw(self):
        self.__setupEventHandlers(True)

    def _freeze(self):
        self.__setupEventHandlers(False)

    def __setupEventHandlers(self, enabled):
        Utils.EventModule.RegisterEventHandler(
            self.__idle_callback, 'event_idle', enabled=enabled)

        Utils.EventModule.RegisterCollapsedHandler(
            self.__updateCB, 'port_connect', enabled=enabled)
        Utils.EventModule.RegisterCollapsedHandler(
            self.__updateCB, 'parameter_finalizeValue', enabled=enabled)
        Utils.EventModule.RegisterCollapsedHandler(
            self.__updateCB, 'node_setBypassed', enabled=enabled)

    #######################################################################
    def __updateCB(self, args):
        if self.__updateTreeOnIdle:
            return

        for arg in args:
            if arg[0] in ('port_connect'):
                for nodeNameKey in 'nodeNameA', 'nodeNameB':
                    nodeName = arg[2][nodeNameKey]
                    node = NodegraphAPI.GetNode(nodeName)
                    try:
                        parentNode = node.getParent().getParent()
                    except Exception:
                        return
                    else:
                        if node is not None and parentNode == self.__node:
                            self.__updateTreeOnIdle = True
                            return

            if arg[0] in ('parameter_finalizeValue'):
                node = arg[2].get('node')
                param = arg[2].get('param')
                if node is not self.__node:
                    try:
                        parentNode = node.getParent().getParent()
                    except Exception:
                        return
                    else:
                        paramNameList = ['name', 'outputName', 'channel']
                        paramName = param.getName()
                        if parentNode == self.__node and \
                                paramName in paramNameList:
                            if node.getType() == 'RenderOutputDefine':
                                nodeType = 1
                                nameParam = 'outputName'
                            else:
                                nodeType = 0
                                nameParam = 'name'
                            paramValue = node.getParameter(
                                nameParam).getValue(0)
                            self.__itemToSelect = (nodeType, paramValue)
                            self.__updateTreeOnIdle = True
                            return

            if arg[0] in ('node_setBypassed'):
                node = arg[2].get('node')
                try:
                    parentNode = node.getParent().getParent()
                except Exception:
                    return
                else:
                    if parentNode == self.__node:
                        if node.getType() == 'RenderOutputDefine':
                            nodeType = 1
                            nameParam = 'outputName'
                        else:
                            nodeType = 0
                            nameParam = 'name'
                        paramValue = node.getParameter(nameParam).getValue(0)
                        self.__itemToSelect = (nodeType, paramValue)
                        self.__updateTreeOnIdle = True
                        return

    #######################################################################
    def __idle_callback(self, *args, **kwargs):
        if self.__updateTreeOnIdle:
            self.__updateTreeContents()
            self.__updateTreeOnIdle = False

    #######################################################################
    # Custom widgets events
    #######################################################################
    @QtCore.pyqtSlot(QtWidgets.QTreeWidget, str)
    def searchTreeItemsEvent(self, treeWidget, text):
        if text:
            # hide all items
            self.__itemVisibility(treeWidget, True)
            # founded items
            foundItems = treeWidget.findItems(
                text, QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive)
            if foundItems:
                for item in foundItems:
                    parentItem = item.parent()
                    if parentItem:
                        item.setHidden(False)
                        parentItem.setHidden(False)
        else:
            # show all items
            self.__itemVisibility(treeWidget, False)

    @QtCore.pyqtSlot()
    def addButtonEvent(self):
        selectedItems = self.__displayTree.selectedItems()
        if selectedItems:
            # Channel node
            parentItem = selectedItems[0].parent()
            uniqueName = self.__uniquifyName('untitled_channel', 0)
            if parentItem is None:
                parentItem = selectedItems[0]
            parentItemName = str(parentItem.text(0))
            rodNode = self.__node.findNode(parentItemName, 1)[1]
            channelParam, channelList = \
                self.__node.getDisplayChannelParam(rodNode)
            channelList.append(uniqueName)
            self.__node.setDisplayChannelParam(rodNode, channelList)
            self.__node.initNewChannel(uniqueName)
        else:
            # Display node
            uniqueName = self.__uniquifyName('untitled_display', 1)
            rodNode = self.__node.initNewDisplay(uniqueName)

    @QtCore.pyqtSlot()
    def removeButtonEvent(self):
        channelSet = set()
        displaySet = set()
        selectedItems = self.__displayTree.selectedItems()
        for item in selectedItems:
            itemName = str(item.text(0))
            if item.parent():
                channelSet.add(itemName)
            else:
                displaySet.add(itemName)
                if item.childCount():
                    for child in item.takeChildren():
                        channelSet.add(str(child.text(0)))
        self.__node.deleteNodes(channelSet, displaySet)

    @QtCore.pyqtSlot()
    def sendButtonEvent(self):
        selectedItems = self.__presetTree.selectedItems()
        selDisplayItems = self.__displayTree.selectedItems()

        presetChList = [str(selectedItem.text(0))
                        for selectedItem in selectedItems]
        uniqueNames = [self.__uniquifyName(str(selectedItem.text(0)), 0)
                       for selectedItem in selectedItems]
        self.__node.createNewChannelFromPreset(presetChList, uniqueNames)

        if selDisplayItems:
            parentItem = selDisplayItems[0].parent()
            if parentItem is None:
                parentItem = selDisplayItems[0]
            parentItemName = str(parentItem.text(0))
            rodNode = self.__node.findNode(parentItemName, 1)[1]
            channelParam, channelList = \
                self.__node.getDisplayChannelParam(rodNode)
            channelList.extend(uniqueNames)
            self.__node.setDisplayChannelParam(rodNode, channelList)
        else:
            for channel, uniqueName in zip(presetChList, uniqueNames):
                parentItemName = self.__uniquifyName(channel, 1)
                rodNode = self.__node.initNewDisplay(parentItemName)
                self.__node.setDisplayChannelParam(rodNode, [uniqueName])

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem)
    def itemChangedEvent(self, item):
        try:
            itemType = item.data(0, QtCore.Qt.UserRole)[0]
            prevItemName = str(item.data(0, QtCore.Qt.UserRole)[1])
        except TypeError:
            return
        else:
            curItemName = str(item.text(0))
            if curItemName != prevItemName:
                uniqueName = self.__uniquifyName(curItemName, itemType)
                node = self.__node.findNode(prevItemName, itemType)[1]
                if itemType == 0:
                    parentItem = item.parent()
                    parentItemName = str(parentItem.text(0))
                    rodNode = self.__node.findNode(parentItemName, 1)[1]
                    self.__node.renameNode(
                        nodeToRename=node, nodeNameParam=uniqueName,
                        parent=rodNode, prevName=prevItemName)
                else:
                    self.__node.renameNode(
                        nodeToRename=node, nodeNameParam=uniqueName)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidget, QtWidgets.QPushButton)
    def treeSelChangedEvent(self, treeWidget, button):
        if treeWidget.selectedItems():
            button.setEnabled(True)
            if treeWidget == self.__presetTree:
                return
        else:
            button.setEnabled(False)
        self.__updateParametersWidget()

    @QtCore.pyqtSlot(QtWidgets.QTreeWidget)
    def treeContextMenu(self, treeWidget):
        menu = QtWidgets.QMenu()
        deselectAction = menu.addAction('Deselect')
        deselectAction.triggered.connect(
            lambda: self.deselectAll(treeWidget))
        collapseAllAction = menu.addAction('CollapseAll')
        collapseAllAction.triggered.connect(
            lambda: self.collapseOrExpandAll(treeWidget, False))
        expandAllAction = menu.addAction('ExpandAll')
        expandAllAction.triggered.connect(
            lambda: self.collapseOrExpandAll(treeWidget, True))
        cursor = QtGui.QCursor()
        menu.exec_(cursor.pos())

    @QtCore.pyqtSlot(QtWidgets.QTreeWidget)
    def deselectAll(self, treeWidget):
        [i.setSelected(False) for i in treeWidget.selectedItems()]

    @QtCore.pyqtSlot(QtWidgets.QTreeWidget, bool)
    def collapseOrExpandAll(self, treeWidget, expandMode):
        rootItem = treeWidget.invisibleRootItem()
        topLevelItems = rootItem.childCount()
        if topLevelItems:
            for idx in range(topLevelItems):
                item = rootItem.child(idx)
                item.setExpanded(expandMode)
