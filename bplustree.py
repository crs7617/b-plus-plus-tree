# B+ Tree - Stage 1: Just node structures

class LeafNode:
    def __init__(self):
        self.keys = []      # sorted list of keys
        self.values = []    # corresponding values
        self.next = None    # pointer to next leaf (for range scans)
        self.is_leaf = True

class InternalNode:
    def __init__(self):
        self.keys = []      # sorted list of keys (guides only)
        self.children = []  # pointers to child nodes
        self.is_leaf = False
