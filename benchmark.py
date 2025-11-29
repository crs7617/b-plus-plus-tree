import time
import random
from bplustree import BPlusTree
from bpptree import BPPTree
from bpptree_v2 import BPPTreeV2

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
    print(f"  Insert time: {elapsed:.2f} ms")
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
    
    # Model stats for v2
    if hasattr(tree, 'model_hits'):
        total = tree.model_hits + tree.model_misses
        accuracy = (tree.model_hits / total * 100) if total > 0 else 0
        print(f"  Model accuracy: {accuracy:.1f}%")
    
    return elapsed

def analyze_tree_structure(tree, name):
    """Analyze tree structure and efficiency"""
    print(f"\n{name} Structure:")
    
    if hasattr(tree, 'get_stats'):
        stats = tree.get_stats()
        print(f"  Total capacity: {stats['total_capacity']}")
        print(f"  Total filled: {stats['total_filled']}")
        print(f"  Space utilization: {stats['utilization']:.1f}%")
        print(f"  Total compactions: {stats['total_compacts']}")
        print(f"  Leaves with models: {stats['leaves_with_models']}")


if __name__ == "__main__":
    # Test parameters
    NUM_INSERTS = 2000
    ORDER = 4
    LEAF_CAPACITY = 16
    
    print("╔" + "═" * 58 + "╗")
    print(f"║  B++ Tree Benchmark: {NUM_INSERTS} insertions (order={ORDER})" + " " * 13 + "║")
    print("╚" + "═" * 58 + "╝")
    
    # Generate random data
    random.seed(42)
    data = [(random.randint(1, 10000), f"val_{i}") for i in range(NUM_INSERTS)]
    search_keys = [key for key, _ in random.sample(data, 200)]
    
    print("\n" + "─" * 60)
    print("PHASE 1: BASELINE B+ TREE")
    print("─" * 60)
    
    bplus = BPlusTree(order=ORDER)
    bplus_time = benchmark_insertions(bplus, data, "B+ Tree (baseline)")
    bplus_search = benchmark_searches(bplus, search_keys, "B+ Tree")
    
    print("\n" + "─" * 60)
    print("PHASE 2: B++ TREE WITH FIXED GAPS")
    print("─" * 60)
    
    bpp = BPPTree(order=ORDER, leaf_capacity=LEAF_CAPACITY)
    bpp_time = benchmark_insertions(bpp, data, "B++ Tree (fixed gaps)")
    bpp_search = benchmark_searches(bpp, search_keys, "B++ Tree")
    
    print("\n" + "─" * 60)
    print("PHASE 3: B++ TREE V2 (ADAPTIVE + MODELS)")
    print("─" * 60)
    
    bpp_v2 = BPPTreeV2(order=ORDER, initial_leaf_capacity=LEAF_CAPACITY)
    bpp_v2_time = benchmark_insertions(bpp_v2, data, "B++ Tree v2 (adaptive + models)")
    bpp_v2_search = benchmark_searches(bpp_v2, search_keys, "B++ Tree v2")
    analyze_tree_structure(bpp_v2, "B++ Tree v2")
    
    # Final comparison
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 20 + "FINAL RESULTS" + " " * 25 + "║")
    print("╚" + "═" * 58 + "╝")
    
    insert_speedup_v1 = ((bplus_time - bpp_time) / bplus_time) * 100
    insert_speedup_v2 = ((bplus_time - bpp_v2_time) / bplus_time) * 100
    search_speedup_v2 = ((bplus_search - bpp_v2_search) / bplus_search) * 100
    
    print(f"\nInsertion Performance:")
    print(f"  B+ Tree (baseline):      {bplus_time:.2f} ms")
    print(f"  B++ v1 (fixed gaps):     {bpp_time:.2f} ms  ({insert_speedup_v1:+.1f}%)")
    print(f"  B++ v2 (adaptive+model): {bpp_v2_time:.2f} ms  ({insert_speedup_v2:+.1f}%)")
    
    print(f"\nSearch Performance:")
    print(f"  B+ Tree (baseline):      {bplus_search:.2f} ms")
    print(f"  B++ v1 (fixed gaps):     {bpp_search:.2f} ms")
    print(f"  B++ v2 (adaptive+model): {bpp_v2_search:.2f} ms  ({search_speedup_v2:+.1f}%)")
    
    print(f"\nMemory Efficiency:")
    if hasattr(bpp_v2, 'get_stats'):
        stats = bpp_v2.get_stats()
        print(f"  Adaptive utilization: {stats['utilization']:.1f}%")
        print(f"  vs Fixed gaps: ~50-60% (typical)")
    
    print("\n" + "─" * 60)