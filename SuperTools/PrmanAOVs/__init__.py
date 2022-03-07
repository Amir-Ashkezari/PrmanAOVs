from .Node import PrmanAOVsNode

def GetEditor():
    from .Editor import PrmanAOVsEditor
    return PrmanAOVsEditor

print("===============================loading prman aovs...")
PluginRegistry = [
	("SuperTool", 2, "PrmanAOVs", (PrmanAOVsNode, GetEditor)),
]
