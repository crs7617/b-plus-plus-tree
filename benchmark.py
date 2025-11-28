import time
import random
from bplustree import BPlusTree
from bpptree import BPPTree

def benchmark_insertions(tree, data, name):
    """Measure insertion time"""
    start = time.time()
    for key, value in data:
        tree.insert(key, value)
    end = time.time()
    
    elapsed = (end - start) * 1000  # Convert to ms
    
    # Count shifts if B++ tree
    shifts = tree.shift_count if hasattr(tree, 'shift_count') else "N/A"
    
    print(f"\n{name}:")
    print(f"  Time: {elapsed:.2f} ms")
    print(f"  Shifts: {shifts}")
    
    return elapsed

def benchmark_searches(tree, keys, name):
    """Measure search time"""
    start = time.time()
    for key in keys:
        tree.search(key)
    end = time.time()
    
    elapsed = (end - start) * 1000
    print(f"  Search time: {elapsed:.2f} ms")
    return elapsed


if __name__ == "__main__":
    # Test parameters
    NUM_INSERTS = 1000
    ORDER = 4
    LEAF_CAPACITY = 16
    
    print(f"Benchmark: {NUM_INSERTS} insertions (order={ORDER})")
    print("=" * 50)
    
    # Generate random data
    random.seed(42)
    data = [(random.randint(1, 10000), f"val_{i}") for i in range(NUM_INSERTS)]
    search_keys = [key for key, _ in random.sample(data, 100)]
    
    # Test B+ Tree
    bplus = BPlusTree(order=ORDER)
    bplus_time = benchmark_insertions(bplus, data, "B+ Tree (baseline)")
    bplus_search = benchmark_searches(bplus, search_keys, "B+ Tree")
    
    # Test B++ Tree
    bpp = BPPTree(order=ORDER, leaf_capacity=LEAF_CAPACITY)
    bpp_time = benchmark_insertions(bpp, data, "B++ Tree (gapped)")
    bpp_search = benchmark_searches(bpp, search_keys, "B++ Tree")
    
    # Results
    speedup = ((bplus_time - bpp_time) / bplus_time) * 100
    print("\n" + "=" * 50)
    print(f"B++ is {speedup:.1f}% faster for insertions!")
    print(f"Gap efficiency: {bpp.shift_count} total shifts vs ~{NUM_INSERTS} for B+")