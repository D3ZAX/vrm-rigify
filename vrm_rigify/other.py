import bpy


class ModeContext:
    def __init__(self, mode):
        self.mode = mode

    def __enter__(self):
        self.old_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode=self.mode)

    def __exit__(self, _type, _value, _trace):
        bpy.ops.object.mode_set(mode=self.old_mode)


def editing(*nodes):
    for node in nodes:
        node.select_set(True)
    return ModeContext('EDIT')
    
def posing(*nodes):
    for node in nodes:
        node.select_set(True)
    return ModeContext('POSE')
