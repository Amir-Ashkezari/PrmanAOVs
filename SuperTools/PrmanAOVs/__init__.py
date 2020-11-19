from Node import PrmanAOVsNode

def GetEditor():
    from Editor import PrmanAOVsEditor
    return PrmanAOVsEditor

PluginRegistry = [
	("SuperTool", 2, "PrmanAOVs", (PrmanAOVsNode, GetEditor)),
]
