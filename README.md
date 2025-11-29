# B++ Tree

A high-performance Python implementation of an optimized B+ tree with adaptive gapped arrays and learned index models.

## Overview

The B++ tree extends the traditional B+ tree with two key optimizations:

1. **Adaptive Gapped Arrays**: Leaves maintain gaps between keys to reduce insertion costs
2. **Linear Predictive Models**: Each leaf uses linear regression to predict key positions

These optimizations provide significant performance improvements for write-heavy workloads while maintaining efficient search operations.

## Performance

Benchmark results (2000 random insertions):

```
                        Insert Time    Search Time    Memory Utilization
B+ Tree (baseline)      85.99 ms      12.01 ms       100%
B++ v1 (fixed gaps)     31.00 ms      3.99 ms        50-60%
B++ v2 (adaptive)       36.99 ms      4.00 ms        71.4%
```

- **57-64% faster insertions** than standard B+ tree
- **67% faster searches** with 93.5% model prediction accuracy
- **71% space utilization** with adaptive capacity management

## Implementation

### Files

- `bplustree.py` - Standard B+ tree implementation (baseline)
- `bpptree.py` - B++ tree with fixed gapped arrays (v1)
- `bpptree_v2.py` - B++ tree with adaptive gaps and learned models (v2)
- `benchmark.py` - Performance comparison suite

### Key Features

**Adaptive Gapped Arrays**
- Pre-allocates space with intentional gaps in leaf nodes
- Inserts into gaps without shifting existing elements
- Compacts only when capacity is exceeded
- Dynamically adjusts capacity based on access patterns

**Linear Predictive Models**
- Trains simple linear regression per leaf: `position = a × key + b`
- Predicts key position with O(1) lookup
- Falls back to local search around predicted position
- Retrains periodically to adapt to data distribution

**Standard B+ Tree Properties**
- All values stored in leaf nodes
- Internal nodes contain only routing keys
- Leaves linked horizontally for range scans
- Logarithmic height for efficient traversal

## Usage

```python
from bpptree_v2 import BPPTreeV2

# Create tree with order=4, initial leaf capacity=16
tree = BPPTreeV2(order=4, initial_leaf_capacity=16)

# Insert key-value pairs
tree.insert(10, "value_10")
tree.insert(20, "value_20")
tree.insert(15, "value_15")

# Search for values
result = tree.search(15)  # Returns "value_15"

# Get statistics
stats = tree.get_stats()
print(f"Space utilization: {stats['utilization']:.1f}%")
print(f"Leaves with trained models: {stats['leaves_with_models']}")
```

## Running Benchmarks

```bash
python benchmark.py
```

This compares all three implementations across insertion and search workloads, providing detailed performance metrics and memory utilization statistics.

## Algorithm Details

### Insertion

1. Traverse tree to find target leaf
2. Attempt insertion into available gap (O(1) if gap exists)
3. If no gaps available, compact leaf and split if necessary
4. Propagate splits up the tree as needed
5. Retrain linear model every 10 insertions

### Search

1. Traverse internal nodes to target leaf
2. Use linear model to predict key position
3. Check predicted position and ±3 neighboring positions
4. Fall back to linear scan if model prediction fails

### Adaptive Capacity

Leaves track their compaction frequency. When compaction rate exceeds 30%, capacity grows by 50%. This allows frequently-updated leaves to maintain more gaps while cold leaves stay compact.

## Trade-offs

**Advantages**
- Significant insertion speedup for random workloads
- Reduced array shifting during inserts
- Fast searches with learned models
- Adaptive memory usage

**Disadvantages**
- 20-30% memory overhead compared to tight packing
- Model training cost (amortized over insertions)
- Less effective for disk-based storage (wasted I/O)
- Prediction accuracy depends on data distribution

## Use Cases

Best suited for:
- In-memory databases with frequent updates
- Real-time indexing systems
- Streaming data ingestion
- Write-heavy workloads with < 10M keys

Not recommended for:
- Disk-based storage systems
- Extremely large datasets (billions of keys)
- Read-only or read-mostly workloads
- Highly skewed key distributions

## References

This implementation draws inspiration from:
- ALEX (Adaptive Learned Index)
- BS-tree (Buffered Segment tree)
- Research on learned index structures

## License

MIT License
