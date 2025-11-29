# B++ Tree v2: Adaptive Gaps + Linear Models

class AdaptiveGappedLeafNode:
    def __init__(self, initial_capacity=8):
        self.capacity = initial_capacity
        self.keys = [None] * self.capacity
        self.values = [None] * self.capacity
        self.size = 0
        self.next = None
        self.is_leaf = True
        
        # Adaptive sizing metrics
        self.compact_count = 0
        self.insert_count = 0
        self.target_fill_ratio = 0.75  # Keep 75% full
        
        # Linear model for search prediction
        self.model_a = 0.0  # Slope
        self.model_b = 0.0  # Intercept
        self.model_trained = False
    
    def train_model(self):
        """Train simple linear model: position ≈ a × key + b"""
        filled_keys = [k for k in self.keys if k is not None]
        
        if len(filled_keys) < 2:
            self.model_trained = False
            return
        
        # Find positions of filled keys
        positions = []
        keys_list = []
        for i, k in enumerate(self.keys):
            if k is not None:
                positions.append(i)
                keys_list.append(k)
        
        # Simple linear regression (least squares)
        n = len(keys_list)
        sum_x = sum(keys_list)
        sum_y = sum(positions)
        sum_xy = sum(k * p for k, p in zip(keys_list, positions))
        sum_xx = sum(k * k for k in keys_list)
        
        # Calculate slope and intercept
        denominator = n * sum_xx - sum_x * sum_x
        if denominator != 0:
            self.model_a = (n * sum_xy - sum_x * sum_y) / denominator
            self.model_b = (sum_y - self.model_a * sum_x) / n
            self.model_trained = True
        else:
            self.model_trained = False
    
    def predict_position(self, key):
        """Use linear model to predict key position"""
        if not self.model_trained:
            return None
        
        predicted = int(self.model_a * key + self.model_b)
        # Clamp to valid range
        return max(0, min(self.capacity - 1, predicted))
    
    def search_with_model(self, key):
        """Search using model prediction + local search"""
        if self.model_trained:
            # Predict position
            pos = self.predict_position(key)
            
            # Check predicted position
            if self.keys[pos] == key:
                return self.values[pos]
            
            # Local search around prediction (±3 positions)
            for offset in [1, -1, 2, -2, 3, -3]:
                check_pos = pos + offset
                if 0 <= check_pos < self.capacity and self.keys[check_pos] == key:
                    return self.values[check_pos]
        
        # Fallback: linear search
        for i in range(self.capacity):
            if self.keys[i] == key:
                return self.values[i]
        return None
    
    def find_slot(self, key):
        """Find insertion slot"""
        for i in range(self.capacity):
            if self.keys[i] is None or key < self.keys[i]:
                return i
        return self.capacity - 1
    
    def insert_into_gap(self, key, value):
        """Insert with minimal shifting"""
        self.insert_count += 1
        slot = self.find_slot(key)
        
        # If slot is empty, just write
        if self.keys[slot] is None:
            self.keys[slot] = key
            self.values[slot] = value
            self.size += 1
            return True
        
        # Try to find nearby gap
        for i in range(slot, self.capacity):
            if self.keys[i] is None:
                for j in range(i, slot, -1):
                    self.keys[j] = self.keys[j-1]
                    self.values[j] = self.values[j-1]
                self.keys[slot] = key
                self.values[slot] = value
                self.size += 1
                return True
        
        for i in range(slot - 1, -1, -1):
            if self.keys[i] is None:
                for j in range(i, slot - 1):
                    self.keys[j] = self.keys[j+1]
                    self.values[j] = self.values[j+1]
                self.keys[slot - 1] = key
                self.values[slot - 1] = value
                self.size += 1
                return True
        
        return False
    
    def should_expand(self):
        """Decide if capacity should grow"""
        # If we compact frequently, expand capacity
        if self.insert_count > 0:
            compact_rate = self.compact_count / self.insert_count
            return compact_rate > 0.3  # More than 30% compaction rate
        return False
    
    def expand_capacity(self):
        """Grow capacity adaptively"""
        new_capacity = int(self.capacity * 1.5)
        self.keys.extend([None] * (new_capacity - self.capacity))
        self.values.extend([None] * (new_capacity - self.capacity))
        self.capacity = new_capacity
    
    def compact(self):
        """Remove gaps, pack keys tightly"""
        self.compact_count += 1
        
        new_keys = []
        new_values = []
        for i in range(self.capacity):
            if self.keys[i] is not None:
                new_keys.append(self.keys[i])
                new_values.append(self.values[i])
        
        # Adaptive capacity expansion
        if self.should_expand():
            self.expand_capacity()
        
        self.keys = new_keys + [None] * (self.capacity - len(new_keys))
        self.values = new_values + [None] * (self.capacity - len(new_values))
        
        # Retrain model after compaction
        self.train_model()
    
    def get_filled_keys(self):
        return [k for k in self.keys if k is not None]
    
    def get_filled_values(self):
        return [v for v in self.values if v is not None]


class InternalNode:
    def __init__(self):
        self.keys = []
        self.children = []
        self.is_leaf = False


class BPPTreeV2:
    def __init__(self, order=4, initial_leaf_capacity=8):
        self.root = AdaptiveGappedLeafNode(initial_capacity=initial_leaf_capacity)
        self.order = order
        self.initial_leaf_capacity = initial_leaf_capacity
        self.shift_count = 0
        self.model_hits = 0  # Track model prediction accuracy
        self.model_misses = 0
    
    def search(self, key):
        """Search using model prediction"""
        node = self.root
        
        # Traverse to leaf
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        
        # Search in leaf using model
        result = node.search_with_model(key)
        
        # Track model accuracy
        if node.model_trained:
            if result is not None:
                self.model_hits += 1
            else:
                self.model_misses += 1
        
        return result
    
    def insert(self, key, value):
        """Insert with adaptive gaps"""
        path = []
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
        
        # Try gap insertion
        if node.insert_into_gap(key, value):
            # Retrain model periodically
            if node.insert_count % 10 == 0:
                node.train_model()
            return
        
        # Compact and split
        node.compact()
        self.shift_count += node.size
        
        if node.size > self.order:
            promoted = self._split_leaf(node, parent, parent_index)
            self._handle_promotion(promoted, path)
    
    def _split_leaf(self, leaf, parent, parent_index):
        filled_keys = leaf.get_filled_keys()
        filled_values = leaf.get_filled_values()
        
        mid = len(filled_keys) // 2
        
        new_leaf = AdaptiveGappedLeafNode(initial_capacity=leaf.capacity)
        for i, (k, v) in enumerate(zip(filled_keys[mid:], filled_values[mid:])):
            new_leaf.keys[i] = k
            new_leaf.values[i] = v
            new_leaf.size += 1
        
        leaf.keys = filled_keys[:mid] + [None] * (leaf.capacity - mid)
        leaf.values = filled_values[:mid] + [None] * (leaf.capacity - mid)
        leaf.size = mid
        
        # Train models for both leaves
        leaf.train_model()
        new_leaf.train_model()
        
        new_leaf.next = leaf.next
        leaf.next = new_leaf
        
        promoted_key = filled_keys[mid]
        return (promoted_key, leaf, new_leaf, parent, parent_index)
    
    def _handle_promotion(self, promotion, path):
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
    
    def get_stats(self):
        """Get adaptive sizing statistics"""
        total_capacity = 0
        total_filled = 0
        total_compacts = 0
        leaves_with_models = 0
        
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
        
        while node:
            total_capacity += node.capacity
            total_filled += node.size
            total_compacts += node.compact_count
            if node.model_trained:
                leaves_with_models += 1
            node = node.next
        
        utilization = (total_filled / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            'total_capacity': total_capacity,
            'total_filled': total_filled,
            'utilization': utilization,
            'total_compacts': total_compacts,
            'leaves_with_models': leaves_with_models
        }
