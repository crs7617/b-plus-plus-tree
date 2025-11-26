
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
        # Find the correct leaf (track path for splits)
        path = []  # Stack of (node, parent, index)
        node = self.root
        parent = None
        parent_index = 0
        
        while not node.is_leaf:
            path.append((node, parent, parent_index))
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
        
        # Check if split needed and propagate up
        if len(node.keys) > self.order:
            promoted = self._split_leaf(node, parent, parent_index)
            self._handle_promotion(promoted, path)
    
    def _split_leaf(self, leaf, parent, parent_index):
        """Split a leaf node and return promoted key info"""
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
        
        # Return promotion info
        promoted_key = new_leaf.keys[0]
        return (promoted_key, leaf, new_leaf, parent, parent_index)
    
    def _handle_promotion(self, promotion, path):
        """Handle promoted key, potentially splitting internal nodes"""
        promoted_key, left_child, right_child, parent, parent_index = promotion
        
        # If no parent, create new root
        if parent is None:
            new_root = InternalNode()
            new_root.keys = [promoted_key]
            new_root.children = [left_child, right_child]
            self.root = new_root
            return
        
        # Insert into parent
        parent.keys.insert(parent_index, promoted_key)
        parent.children.insert(parent_index + 1, right_child)
        
        # Check if parent needs split
        if len(parent.keys) > self.order:
            self._split_internal(parent, path)
    
    def _split_internal(self, node, path):
        """Split an internal node and propagate up"""
        mid = len(node.keys) // 2
        
        # Middle key gets promoted (not kept in either child)
        promoted_key = node.keys[mid]
        
        # Create new right internal node
        new_node = InternalNode()
        new_node.keys = node.keys[mid + 1:]
        new_node.children = node.children[mid + 1:]
        
        # Update old node (keep left half)
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]
        
        # Find parent from path
        if not path:
            # Splitting root, create new root
            new_root = InternalNode()
            new_root.keys = [promoted_key]
            new_root.children = [node, new_node]
            self.root = new_root
        else:
            # Get parent info
            parent_node, grandparent, parent_idx = path.pop()
            
            # Find where to insert in parent
            i = 0
            while i < len(parent_node.keys) and promoted_key > parent_node.keys[i]:
                i += 1
            
            parent_node.keys.insert(i, promoted_key)
            parent_node.children.insert(i + 1, new_node)
            
            # Recursively check if parent needs split
            if len(parent_node.keys) > self.order:
                self._split_internal(parent_node, path)


# Test with internal node splits
if __name__ == "__main__":
    tree = BPlusTree(order=3)  # Max 3 keys per node
    
    # Insert many values to trigger multiple splits
    print("Inserting values 10 through 100 (step 10)...")
    for i in range(10, 110, 10):
        tree.insert(i, f"Val_{i}")
    
    # Test searches
    print("\nSearch tests:")
    print(f"Search 30: {tree.search(30)}")
    print(f"Search 70: {tree.search(70)}")
    print(f"Search 100: {tree.search(100)}")
    print(f"Search 999: {tree.search(999)}")
    
    # Analyze tree structure
    def count_levels(node, level=0):
        if node.is_leaf:
            return level
        return max(count_levels(child, level + 1) for child in node.children)
    
    def count_leaves(node):
        if node.is_leaf:
            return 1
        return sum(count_leaves(child) for child in node.children)
    
    height = count_levels(tree.root)
    num_leaves = count_leaves(tree.root)
    
    print(f"\nTree statistics:")
    print(f"Height: {height}")
    print(f"Number of leaves: {num_leaves}")
    print(f"Root keys: {tree.root.keys}")
    
    # Verify linked list integrity
    print("\nLinked list verification (first 3 leaves):")
    node = tree.root
    while not node.is_leaf:
        node = node.children[0]
    
    count = 0
    while node and count < 3:
        print(f"Leaf {count + 1}: {node.keys}")
        node = node.next
        count += 1
