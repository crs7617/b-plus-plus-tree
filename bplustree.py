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


class BPlusTree:
    def __init__(self, order=4):
        self.root = LeafNode()  # Start with empty leaf
        self.order = order      # Max keys per node
    
    def search(self, key):
        """Find value for given key, or return None"""
        node = self.root
        
        # Traverse down to leaf
        while not node.is_leaf:
            # Find which child to follow
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        
        # Binary search in leaf
        if key in node.keys:
            idx = node.keys.index(key)
            return node.values[idx]
        return None


# Simple test
if __name__ == "__main__":
    tree = BPlusTree()
    
    # Manually create a tiny tree for testing
    tree.root.keys = [10, 20, 30]
    tree.root.values = ["A", "B", "C"]
    
    print(f"Search 20: {tree.search(20)}")  # Should print "B"
    print(f"Search 99: {tree.search(99)}")  # Should print None
    print(f"Search 10: {tree.search(10)}")  # Should print "A"
