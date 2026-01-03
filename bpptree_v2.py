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
        
        # Enhanced linear model for search prediction
        self.model_a = 0.0  # Slope
        self.model_b = 0.0  # Intercept
        self.model_trained = False
        self.model_accuracy = 0.0
        self.model_predictions = 0
        self.model_hits_local = 0
        self.model_avg_error = 3  # Average prediction error
        
        # Optimization: cache min/max for bounds checking
        self.min_key = None
        self.max_key = None
    
    def train_model(self):
        """Train enhanced linear model with error tracking"""
        filled_keys = []
        positions = []
        
        for i, k in enumerate(self.keys):
            if k is not None:
                positions.append(i)
                filled_keys.append(k)
        
        if len(filled_keys) < 2:
            self.model_trained = False
            return
        
        # Update bounds for fast range checks
        self.min_key = filled_keys[0]
        self.max_key = filled_keys[-1]
        
        # Optimized linear regression (least squares)
        n = len(filled_keys)
        sum_x = sum(filled_keys)
        sum_y = sum(positions)
        sum_xy = sum(k * p for k, p in zip(filled_keys, positions))
        sum_xx = sum(k * k for k in filled_keys)
        
        # Calculate slope and intercept
        denominator = n * sum_xx - sum_x * sum_x
        if denominator != 0:
            self.model_a = (n * sum_xy - sum_x * sum_y) / denominator
            self.model_b = (sum_y - self.model_a * sum_x) / n
            self.model_trained = True
            
            # Calculate average prediction error for adaptive search window
            errors = [abs(int(self.model_a * k + self.model_b) - p) 
                     for k, p in zip(filled_keys, positions)]
            self.model_avg_error = sum(errors) / len(errors) if errors else 3
        else:
            self.model_trained = False
    
    def predict_position(self, key):
        """Use linear model to predict key position with bounds checking"""
        if not self.model_trained:
            return None
        
        # Fast bounds check - avoids expensive prediction
        if self.min_key and key < self.min_key:
            return 0
        if self.max_key and key > self.max_key:
            return self.capacity - 1
        
        predicted = int(self.model_a * key + self.model_b)
        # Clamp to valid range
        return max(0, min(self.capacity - 1, predicted))
    
    def exponential_search(self, key, start_pos):
        """Exponential search from predicted position - O(log n) instead of O(n)"""
        # Check start position
        if self.keys[start_pos] == key:
            return self.values[start_pos]
        
        # Determine direction based on key comparison
        if self.keys[start_pos] is not None and key < self.keys[start_pos]:
            # Search left with exponentially growing steps
            step = 1
            while start_pos - step >= 0:
                if self.keys[start_pos - step] == key:
                    return self.values[start_pos - step]
                if self.keys[start_pos - step] is not None and self.keys[start_pos - step] < key:
                    break
                step *= 2
        else:
            # Search right with exponentially growing steps
            step = 1
            while start_pos + step < self.capacity:
                if self.keys[start_pos + step] == key:
                    return self.values[start_pos + step]
                if self.keys[start_pos + step] is not None and self.keys[start_pos + step] > key:
                    break
                step *= 2
        
        return None
    
    def binary_search_filled(self, key):
        """Binary search on filled positions only - O(log n) fallback"""
        filled = [(i, self.keys[i]) for i in range(self.capacity) if self.keys[i] is not None]
        
        if not filled:
            return None
        
        left, right = 0, len(filled) - 1
        while left <= right:
            mid = (left + right) // 2
            idx, k = filled[mid]
            
            if k == key:
                return self.values[idx]
            elif k < key:
                left = mid + 1
            else:
                right = mid - 1
        
        return None
    
    def search_with_model(self, key):
        """Enhanced search: model prediction + exponential search + binary fallback"""
        self.model_predictions += 1
        
        if self.model_trained:
            # Predict position using ML model
            pos = self.predict_position(key)
            
            # Use exponential search from predicted position (adapts to model error)
            result = self.exponential_search(key, pos)
            
            if result is not None:
                self.model_hits_local += 1
                return result
        
        # Fallback: binary search on filled positions (much faster than linear)
        return self.binary_search_filled(key)
    
    def find_slot_binary(self, key):
        """Binary search to find insertion slot - O(log n) instead of O(n)"""
        # Collect filled positions
        filled = []
        for i in range(self.capacity):
            if self.keys[i] is not None:
                filled.append((i, self.keys[i]))
        
        if not filled:
            return 0
        
        # Binary search for insertion point
        left, right = 0, len(filled) - 1
        
        if key < filled[0][1]:
            return 0
        if key > filled[-1][1]:
            # Find first empty slot after last key
            last_idx = filled[-1][0]
            for i in range(last_idx + 1, self.capacity):
                if self.keys[i] is None:
                    return i
            return last_idx + 1
        
        while left <= right:
            mid = (left + right) // 2
            idx, k = filled[mid]
            
            if k == key:
                return idx
            elif k < key:
                left = mid + 1
            else:
                right = mid - 1
        
        # Find insertion point between filled[right] and filled[left]
        if left < len(filled):
            return filled[left][0]
        return filled[-1][0] + 1
    
    def find_nearest_gap(self, start_pos):
        """Bidirectional gap search - finds closest gap efficiently"""
        left = start_pos
        right = start_pos
        
        while left >= 0 or right < self.capacity:
            if left >= 0 and self.keys[left] is None:
                return left
            if right < self.capacity and self.keys[right] is None:
                return right
            left -= 1
            right += 1
        
        return None
    
    def insert_into_gap(self, key, value):
        """Optimized insert with binary search and bidirectional gap finding"""
        self.insert_count += 1
        
        # Use binary search to find slot (much faster)
        slot = self.find_slot_binary(key)
        
        # If slot is empty, just write (no shifting needed)
        if slot < self.capacity and self.keys[slot] is None:
            self.keys[slot] = key
            self.values[slot] = value
            self.size += 1
            return True
        
        # Find nearest gap using bidirectional search
        gap = self.find_nearest_gap(slot)
        
        if gap is None:
            return False  # No gap available, need compaction
        
        # Optimized shifting: shift in direction of gap
        if gap > slot:
            # Shift right to fill gap
            for j in range(gap, slot, -1):
                self.keys[j] = self.keys[j-1]
                self.values[j] = self.values[j-1]
        else:
            # Shift left to fill gap
            for j in range(gap, slot - 1):
                self.keys[j] = self.keys[j+1]
                self.values[j] = self.values[j+1]
            slot -= 1
        
        self.keys[slot] = key
        self.values[slot] = value
        self.size += 1
        return True
    
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
    
    def get_model_accuracy(self):
        """Calculate model prediction accuracy percentage"""
        if self.model_predictions > 0:
            return (self.model_hits_local / self.model_predictions) * 100
        return 0.0


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
        """Search using enhanced model prediction with exponential search"""
        node = self.root
        
        # Traverse to leaf
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        
        # Search in leaf using enhanced model + exponential/binary search
        result = node.search_with_model(key)
        
        # Track global model accuracy
        if node.model_trained:
            if result is not None:
                self.model_hits += 1
            else:
                self.model_misses += 1
        
        return result
    
    def insert(self, key, value):
        """Insert with optimized gapped array operations"""
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
        
        # Try optimized gap insertion
        if node.insert_into_gap(key, value):
            # Adaptive model retraining based on accuracy and frequency
            if node.insert_count % 20 == 0:  # Less frequent retraining
                node.train_model()
            elif node.model_trained and node.insert_count % 50 == 0:
                # Periodic accuracy check - retrain if accuracy drops
                accuracy = node.get_model_accuracy()
                if accuracy < 70:  # Retrain if accuracy below 70%
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
        """Get enhanced statistics including model accuracy"""
        total_capacity = 0
        total_filled = 0
        total_compacts = 0
        leaves_with_models = 0
        total_model_accuracy = 0
        leaf_count = 0
        
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
        
        while node:
            total_capacity += node.capacity
            total_filled += node.size
            total_compacts += node.compact_count
            if node.model_trained:
                leaves_with_models += 1
                total_model_accuracy += node.get_model_accuracy()
            leaf_count += 1
            node = node.next
        
        utilization = (total_filled / total_capacity * 100) if total_capacity > 0 else 0
        avg_model_accuracy = (total_model_accuracy / leaves_with_models) if leaves_with_models > 0 else 0
        
        return {
            'total_capacity': total_capacity,
            'total_filled': total_filled,
            'utilization': utilization,
            'total_compacts': total_compacts,
            'leaves_with_models': leaves_with_models,
            'leaf_count': leaf_count,
            'avg_model_accuracy': avg_model_accuracy,
            'global_model_accuracy': (self.model_hits / (self.model_hits + self.model_misses) * 100) if (self.model_hits + self.model_misses) > 0 else 0
        }
