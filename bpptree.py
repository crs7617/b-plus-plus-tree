# B++ Tree with Gapped Arrays Optimization

class GappedLeafNode:
    def __init__(self, capacity=8):
        self.capacity = capacity
        self.keys = [None] * capacity    # Pre-allocated with gaps
        self.values = [None] * capacity
        self.size = 0  # Number of filled slots
        self.next = None
        self.is_leaf = True
    
    def find_slot(self, key):
        """Find insertion slot (may be a gap)"""
        for i in range(self.capacity):
            if self.keys[i] is None or key < self.keys[i]:
                return i
        return self.capacity - 1
    
    def insert_into_gap(self, key, value):
        """Insert without shifting if gap available"""
        slot = self.find_slot(key)
        
        # If slot is empty, just write
        if self.keys[slot] is None:
            self.keys[slot] = key
            self.values[slot] = value
            self.size += 1
            return True
        
        # If slot occupied, try to find nearby gap
        # Check right
        for i in range(slot, self.capacity):
            if self.keys[i] is None:
                # Shift minimally
                for j in range(i, slot, -1):
                    self.keys[j] = self.keys[j-1]
                    self.values[j] = self.values[j-1]
                self.keys[slot] = key
                self.values[slot] = value
                self.size += 1
                return True
        
        # Check left
        for i in range(slot - 1, -1, -1):
            if self.keys[i] is None:
                # Shift minimally
                for j in range(i, slot - 1):
                    self.keys[j] = self.keys[j+1]
                    self.values[j] = self.values[j+1]
                self.keys[slot - 1] = key
                self.values[slot - 1] = value
                self.size += 1
                return True
        
        return False  # No gaps, need compaction
    
    def compact(self):
        """Remove gaps, pack keys tightly (only when necessary)"""
        new_keys = []
        new_values = []
        for i in range(self.capacity):
            if self.keys[i] is not None:
                new_keys.append(self.keys[i])
                new_values.append(self.values[i])
        
        self.keys = new_keys + [None] * (self.capacity - len(new_keys))
        self.values = new_values + [None] * (self.capacity - len(new_values))
    
    def get_filled_keys(self):
        """Return only non-None keys"""
        return [k for k in self.keys if k is not None]
    
    def get_filled_values(self):
        """Return only non-None values"""
        return [v for v in self.values if v is not None]


class InternalNode:
    def __init__(self):
        self.keys = []
        self.children = []
        self.is_leaf = False


class BPPTree:
    def __init__(self, order=4, leaf_capacity=8):
        self.root = GappedLeafNode(capacity=leaf_capacity)
        self.order = order
        self.leaf_capacity = leaf_capacity
        self.shift_count = 0  # Track shifts for benchmark
    
    def search(self, key):
        """Search (same as B+ tree)"""
        node = self.root
        
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        
        # Search in gapped leaf
        for i in range(node.capacity):
            if node.keys[i] == key:
                return node.values[i]
        return None
    
    def insert(self, key, value):
        """Insert with gapped array optimization"""
        path = []
        node = self.root
        parent = None
        parent_index = 0
        
        # Traverse to leaf
        while not node.is_leaf:
            path.append((node, parent, parent_index))
            parent = node
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            parent_index = i
            node = node.children[i]
        
        # Try to insert into gap (fast path!)
        if node.insert_into_gap(key, value):
            # Success! No split needed
            return
        
        # No gaps available, compact and split
        node.compact()
        self.shift_count += node.size  # Count compaction cost
        
        # Now split
        if node.size > self.order:
            promoted = self._split_leaf(node, parent, parent_index)
            self._handle_promotion(promoted, path)
    
    def _split_leaf(self, leaf, parent, parent_index):
        """Split gapped leaf"""
        filled_keys = leaf.get_filled_keys()
        filled_values = leaf.get_filled_values()
        
        mid = len(filled_keys) // 2
        
        # Create new right leaf
        new_leaf = GappedLeafNode(capacity=self.leaf_capacity)
        for i, (k, v) in enumerate(zip(filled_keys[mid:], filled_values[mid:])):
            new_leaf.keys[i] = k
            new_leaf.values[i] = v
            new_leaf.size += 1
        
        # Update old leaf
        leaf.keys = filled_keys[:mid] + [None] * (self.leaf_capacity - mid)
        leaf.values = filled_values[:mid] + [None] * (self.leaf_capacity - mid)
        leaf.size = mid
        
        # Linked list
        new_leaf.next = leaf.next
        leaf.next = new_leaf
        
        promoted_key = filled_keys[mid]
        return (promoted_key, leaf, new_leaf, parent, parent_index)
    
    def _handle_promotion(self, promotion, path):
        """Same as B+ tree"""
        promoted_key, left_child, right_child, parent, parent_index = promotion
        
        if parent is None:
            new_root = InternalNode()
            new_root.keys = [promoted_key]
            new_root.children = [left_child, right_child]
            self.root = new_root
            return
        
        parent.keys.insert(parent_index, promoted_key)
        parent.children.insert(parent_index + 1, right_child)
        
        if len(parent.keys) > self.order:
            self._split_internal(parent, path)
    
    def _split_internal(self, node, path):
        """Same as B+ tree"""
        mid = len(node.keys) // 2
        promoted_key = node.keys[mid]
        
        new_node = InternalNode()
        new_node.keys = node.keys[mid + 1:]
        new_node.children = node.children[mid + 1:]
        
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]
        
        if not path:
            new_root = InternalNode()
            new_root.keys = [promoted_key]
            new_root.children = [node, new_node]
            self.root = new_root
        else:
            parent_node, grandparent, parent_idx = path.pop()
            i = 0
            while i < len(parent_node.keys) and promoted_key > parent_node.keys[i]:
                i += 1
            parent_node.keys.insert(i, promoted_key)
            parent_node.children.insert(i + 1, new_node)
            
            if len(parent_node.keys) > self.order:
                self._split_internal(parent_node, path)
