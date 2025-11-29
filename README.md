# B++ Tree

A high-performance Python implementation of an optimized B+ tree with adaptive gapped arrays and learned index models.

## Overview

The B++ tree extends the traditional B+ tree with two key optimizations:

1. **Adaptive Gapped Arrays**: Leaves maintain gaps between keys to reduce insertion costs
2. **Linear Predictive Models**: Each leaf uses linear regression to predict key positions

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

## Files

- `bplustree.py` - Standard B+ tree (baseline)
- `bpptree.py` - B++ tree with fixed gaps (v1)
- `bpptree_v2.py` - B++ tree with adaptive gaps and models (v2)
- `benchmark.py` - Performance comparison suite

## Usage

```python
from bpptree_v2 import BPPTreeV2

# Create tree
tree = BPPTreeV2(order=4, initial_leaf_capacity=16)

# Insert and search
tree.insert(10, "value_10")
tree.insert(20, "value_20")
result = tree.search(15)

# Get statistics
stats = tree.get_stats()
print(f"Space utilization: {stats['utilization']:.1f}%")
```

## Benchmarks

```bash
python benchmark.py
```

## How It Works

**Adaptive Gapped Arrays**: Leaves pre-allocate space with gaps. Insertions use gaps without shifting (O(1)). When full, compact and grow capacity by 50% if compaction rate exceeds 30%.

**Linear Models**: Each leaf trains a simple regression model (`position = a × key + b`). Search predicts position and checks ±3 neighbors. Retrains every 10 insertions.

## Use Cases

Best for: In-memory databases, real-time indexing, write-heavy workloads with < 10M keys

Not for: Disk-based storage, billions of keys, read-only workloads, skewed distributions

## License

MIT
