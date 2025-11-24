
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
    
    def insert(self, key, value):
        """Insert key-value pair (no splits yet)"""
        # Find the correct leaf
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        
        # Insert in sorted position
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        node.keys.insert(i, key)
        node.values.insert(i, value)


# Simple test
if __name__ == "__main__":
    tree = BPlusTree()
    
    # Test insert
    tree.insert(10, "A")
    tree.insert(30, "C")
    tree.insert(20, "B")  # Insert in middle
    tree.insert(5, "Z")   # Insert at start
    
    # Test search
    print(f"Search 20: {tree.search(20)}")  # Should print "B"
    print(f"Search 5: {tree.search(5)}")    # Should print "Z"
    print(f"Search 99: {tree.search(99)}")  # Should print None
    
    # Print all keys to verify sorted order
    print(f"All keys: {tree.root.keys}")    # Should be [5, 10, 20, 30]
