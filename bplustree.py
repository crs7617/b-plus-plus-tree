
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
        """Insert key-value pair with splits"""
        # Find the correct leaf
        node = self.root
        parent = None
        parent_index = 0
        
        while not node.is_leaf:
            parent = node
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            parent_index = i
            node = node.children[i]
        
        # Insert in sorted position
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        node.keys.insert(i, key)
        node.values.insert(i, value)
        
        # Check if split needed
        if len(node.keys) > self.order:
            self._split_leaf(node, parent, parent_index)
    
    def _split_leaf(self, leaf, parent, parent_index):
        """Split a leaf node and update parent"""
        mid = len(leaf.keys) // 2
        
        # Create new right leaf
        new_leaf = LeafNode()
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]
        
        # Update old leaf (keep left half)
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]
        
        # Connect linked list: left → new_leaf → old_next
        new_leaf.next = leaf.next
        leaf.next = new_leaf
        
        # Push first key of right leaf up to parent
        promoted_key = new_leaf.keys[0]
        
        # If no parent, create new root
        if parent is None:
            new_root = InternalNode()
            new_root.keys = [promoted_key]
            new_root.children = [leaf, new_leaf]
            self.root = new_root
        else:
            # Insert into parent
            parent.keys.insert(parent_index, promoted_key)
            parent.children.insert(parent_index + 1, new_leaf)


# Test with splits
if __name__ == "__main__":
    tree = BPlusTree(order=3)  # Max 3 keys per node
    
    # Insert enough to cause split
    print("Inserting: 10, 20, 30, 40, 50")
    tree.insert(10, "A")
    tree.insert(20, "B")
    tree.insert(30, "C")
    tree.insert(40, "D")  # This will cause split!
    tree.insert(50, "E")
    
    # Test search after split
    print(f"\nSearch 20: {tree.search(20)}")
    print(f"Search 40: {tree.search(40)}")
    print(f"Search 50: {tree.search(50)}")
    
    # Check tree structure
    print(f"\nRoot is leaf? {tree.root.is_leaf}")
    if not tree.root.is_leaf:
        print(f"Root keys (internal): {tree.root.keys}")
        print(f"Left leaf keys: {tree.root.children[0].keys}")
        print(f"Right leaf keys: {tree.root.children[1].keys}")
        
        # Check linked list
        left = tree.root.children[0]
        right = tree.root.children[1]
        print(f"\nLinked list check:")
        print(f"Left.next == Right? {left.next == right}")
        print(f"Right.next == None? {right.next is None}")
