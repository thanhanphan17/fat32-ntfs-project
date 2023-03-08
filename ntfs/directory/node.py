"""
    NodeNTFS class represents a node in the NTFS file system tree.
"""

class NodeNTFS():
    def __init__(self, entry=None, parent=None, id=None, path="", name=""):
        path += "\\"
        self.path = path+name
        self.entry = entry
        self.parent = parent 
        self.ID = id
        self.children = []

    def getProperty(self):
        return self.entry.getProperties()

    def isEmpty(self):
        return self.entry == None

    def addChildren(self, child):
        self.children.append(child)

    def isDirectory(self):
        return self.entry.is_directory()

    def getChildrenList(self):
        return self.children

    def getFileName(self):
        return self.entry.getFileName()

    def getID(self):
        return self.ID

    def getPath(self):
        return self.path

    def getParent(self):
        return self.parent
