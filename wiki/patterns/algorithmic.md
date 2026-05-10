---
title: "Algorithmic Patterns"
type: concept
tags: [patterns, algorithms, data-structures, software-engineering]
sources: ["Common Algorithm Patterns Cheat Sheet.md"]
created: 2026-05-06
updated: 2026-05-06
---

# Algorithmic Patterns

15 pattern families that cover ~90% of algorithm problems. For each: problem shape, recognition trigger, complexity, and template.

See also: [[patterns/code-quality]], [[patterns/principles]]

---

## Pattern Recognition Table

| Keyword / Problem Shape | Pattern |
|---|---|
| Contiguous subarray/substring | Sliding Window |
| Find pairs/triplets, sorted array | Two Pointers |
| Cycle detection, find middle of list | Fast & Slow Pointers |
| Sorted data, halving search space | Binary Search |
| Overlapping intervals, scheduling | Merge Intervals |
| Shortest path, level-order traversal | BFS |
| All paths, explore/backtrack, tree/graph | DFS |
| Generate all combinations/permutations | Backtracking |
| Optimal substructure + overlapping subproblems | Dynamic Programming |
| Local optimum leads to global optimum | Greedy |
| Dependencies, prerequisites, ordering | Topological Sort |
| Connectivity, grouping, cycle in graph | Union-Find |
| K largest/smallest/most frequent | Top K Elements (Heap) |
| Next greater/smaller element | Monotonic Stack |

---

## 1. Sliding Window

**Problem shape:** Max/min/count over a contiguous subarray or substring of variable or fixed size.

**Recognize it when:** "longest/shortest subarray where...", "substring with at most K distinct..."

**Complexity:** O(n) time, O(1) or O(k) space

```
left = 0
for right in range(len(arr)):
    add arr[right] to window state

    while window_condition_violated:
        remove arr[left] from window state
        left += 1

    result = max(result, right - left + 1)
```

**Key problems:** Longest Substring Without Repeating Characters, Minimum Window Substring, Max Sum Subarray of Size K.

---

## 2. Two Pointers

**Problem shape:** Pair/triplet search in sorted array, palindrome check, in-place array manipulation.

**Recognize it when:** Sorted input + "find two elements that sum to X", or "remove duplicates in-place".

**Complexity:** O(n) time, O(1) space

```
left, right = 0, len(arr) - 1
while left < right:
    if condition_met:
        record result; left += 1; right -= 1
    elif need_larger:
        left += 1
    else:
        right -= 1
```

**Key problems:** Two Sum (sorted), 3Sum, Container With Most Water, Valid Palindrome.

---

## 3. Fast & Slow Pointers (Floyd's)

**Problem shape:** Linked list cycle, find middle, find k-th from end.

**Recognize it when:** Linked list + "detect cycle" or "find middle without knowing length".

**Complexity:** O(n) time, O(1) space

```
slow, fast = head, head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    if slow == fast:  # cycle detected
        break
# When loop ends normally: slow is at middle
```

**Key problems:** Linked List Cycle, Find Middle, Palindrome Linked List, Happy Number.

---

## 4. Binary Search

**Problem shape:** Sorted data; find a value, boundary, or answer by eliminating half the search space.

**Recognize it when:** "O(log n) search", sorted array, or "find minimum X such that condition holds" (binary search on answer).

**Complexity:** O(log n) time, O(1) space

```
left, right = 0, len(arr) - 1
while left <= right:
    mid = (left + right) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
```

**Binary search on answer:** When the answer is a value in a range and "can we achieve X?" is checkable in O(n) — binary search on X.

**Key problems:** First Bad Version, Search in Rotated Array, Find Peak Element, Koko Eating Bananas (search on answer).

---

## 5. Merge Intervals

**Problem shape:** Overlapping ranges — merge, insert, or count non-overlapping.

**Recognize it when:** Input is a list of `[start, end]` intervals; "merge all overlapping".

**Complexity:** O(n log n) time (sort dominates), O(n) space

```
intervals.sort(key=lambda x: x[0])
merged = [intervals[0]]
for start, end in intervals[1:]:
    if start <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], end)
    else:
        merged.append([start, end])
```

**Key problems:** Merge Intervals, Insert Interval, Meeting Rooms I & II.

---

## 6. BFS (Breadth-First Search)

**Problem shape:** Shortest path in unweighted graph; level-order traversal; "minimum steps to reach".

**Recognize it when:** "minimum number of moves/steps", level-by-level processing, unweighted shortest path.

**Complexity:** O(V + E) time, O(V) space

```python
from collections import deque
queue = deque([start])
visited = {start}
level = 0

while queue:
    for _ in range(len(queue)):   # process one level
        node = queue.popleft()
        if node == target:
            return level
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    level += 1
```

**Key problems:** Binary Tree Level Order Traversal, Word Ladder, Rotting Oranges, Number of Islands.

---

## 7. DFS (Depth-First Search)

**Problem shape:** Explore all paths, tree/graph traversal, detect cycles, find connected components.

**Recognize it when:** "find all paths", "does a path exist", backtracking exploration.

**Complexity:** O(V + E) time, O(V) space (call stack)

```python
# Recursive
def dfs(node, visited):
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(neighbor, visited)

# Iterative (explicit stack)
stack = [start]
visited = {start}
while stack:
    node = stack.pop()
    for neighbor in graph[node]:
        if neighbor not in visited:
            visited.add(neighbor)
            stack.append(neighbor)
```

**DFS vs BFS decision:** Use BFS for shortest path. Use DFS for exhaustive exploration, cycle detection, or when recursion maps naturally to the problem.

**Key problems:** Number of Islands, Course Schedule (cycle detection), Path Sum, Word Search in Grid.

---

## 8. Backtracking

**Problem shape:** Generate all valid combinations, permutations, or arrangements subject to constraints.

**Recognize it when:** "find all...", "generate all...", constraint satisfaction (N-Queens, Sudoku).

**Complexity:** O(2^n) or O(n!) — inherently exponential; pruning reduces constant factor.

```python
def backtrack(state, choices):
    if is_solution(state):
        results.append(state[:])   # copy current state
        return

    for choice in choices:
        if is_valid(choice, state):
            state.append(choice)
            backtrack(state, remaining_choices(choices, choice))
            state.pop()            # undo — the backtrack step
```

**Pruning:** Add `if not is_valid(choice): continue` before recursing. This is where all the performance lives.

**Key problems:** Permutations, Subsets, N-Queens, Generate Parentheses, Palindrome Partitioning.

---

## 9. Dynamic Programming

**Problem shape:** Optimal value (min/max count) where the problem breaks into overlapping subproblems.

**Recognize it when:** "minimum cost to...", "number of ways to...", "longest subsequence/substring".

**Complexity:** O(n²) typical; O(n) for 1D DP; O(n·m) for 2D; space often reducible.

**Two approaches:**

**Top-down (memoization)** — natural recursion + cache:
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def dp(i):
    if base_case(i):
        return base_value
    return combine(dp(subproblem_1(i)), dp(subproblem_2(i)))
```

**Bottom-up (tabulation)** — iterative, fills table from base cases:
```python
dp = [0] * (n + 1)
dp[0] = base_value
for i in range(1, n + 1):
    dp[i] = combine(dp[i-1], ...)
```

**Design steps:**
1. Define `dp[i]` (or `dp[i][j]`) precisely in words.
2. Write the recurrence relation.
3. Identify base cases.
4. Choose top-down or bottom-up.

**Key problems:** Coin Change, Longest Common Subsequence, 0/1 Knapsack, Edit Distance, Longest Increasing Subsequence.

---

## 10. Greedy

**Problem shape:** Optimization where the locally optimal choice at each step yields a globally optimal result.

**Recognize it when:** Sorting by one dimension then greedily selecting; problems where you can prove no future choice can improve a current decision.

**Complexity:** Varies; often O(n log n) due to sort.

**Proof obligation:** Before applying greedy, verify the greedy choice property holds. Greedy fails when future choices can invalidate current ones — use DP in that case.

**Key problems:** Jump Game, Gas Station, Meeting Rooms II, Fractional Knapsack, Interval Scheduling.

---

## 11. Topological Sort

**Problem shape:** Linear ordering of nodes in a DAG respecting directed edges (dependencies before dependents).

**Recognize it when:** "prerequisites", "task ordering", "can you complete all courses".

**Complexity:** O(V + E) time and space

**Kahn's Algorithm (BFS-based):**
```python
from collections import deque

in_degree = {node: 0 for node in graph}
for node in graph:
    for neighbor in graph[node]:
        in_degree[neighbor] += 1

queue = deque([n for n in in_degree if in_degree[n] == 0])
order = []

while queue:
    node = queue.popleft()
    order.append(node)
    for neighbor in graph[node]:
        in_degree[neighbor] -= 1
        if in_degree[neighbor] == 0:
            queue.append(neighbor)

# Cycle exists if len(order) != len(graph)
```

**Key problems:** Course Schedule I & II, Alien Dictionary, Minimum Height Trees.

---

## 12. Union-Find (Disjoint Set Union)

**Problem shape:** Dynamic connectivity — group elements, check if two elements are connected, detect cycles in undirected graph.

**Recognize it when:** "connected components", "are X and Y in the same group", "does adding this edge create a cycle".

**Complexity:** O(α(n)) ≈ O(1) per operation with path compression + union by rank. O(n) space.

```python
parent = list(range(n))
rank = [0] * n

def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])  # path compression
    return parent[x]

def union(x, y):
    px, py = find(x), find(y)
    if px == py:
        return False  # already connected, adding edge = cycle
    if rank[px] < rank[py]:
        px, py = py, px
    parent[py] = px
    if rank[px] == rank[py]:
        rank[px] += 1
    return True
```

**Key problems:** Number of Connected Components, Graph Valid Tree, Accounts Merge, Redundant Connection.

---

## 13. Top K Elements (Heap)

**Problem shape:** Find the k largest, k smallest, or k most frequent elements without full sort.

**Recognize it when:** "k largest/smallest", "k closest", "k most frequent".

**Complexity:** O(n log k) time, O(k) space — better than O(n log n) sort when k << n.

**Strategy:**
- K largest → min-heap of size k (evict smallest when heap exceeds k)
- K smallest → max-heap of size k (evict largest when heap exceeds k)
- K most frequent → count with hash map, then heap on counts

```python
import heapq

# K largest using min-heap
heap = []
for num in nums:
    heapq.heappush(heap, num)
    if len(heap) > k:
        heapq.heappop(heap)
# heap now contains k largest elements
```

**Key problems:** Kth Largest Element, Top K Frequent Elements, K Closest Points to Origin, Merge K Sorted Lists.

---

## 14. Modified Binary Search

**Problem shape:** Search in a sorted-but-modified array (rotated, with duplicates, or searching for a boundary condition).

**Recognize it when:** Sorted array with a twist — rotation, finding first/last occurrence, finding peak.

**Complexity:** O(log n) time, O(1) space

```python
# Rotated sorted array
left, right = 0, len(nums) - 1
while left <= right:
    mid = (left + right) // 2
    if nums[mid] == target:
        return mid
    if nums[left] <= nums[mid]:          # left half is sorted
        if nums[left] <= target < nums[mid]:
            right = mid - 1
        else:
            left = mid + 1
    else:                                 # right half is sorted
        if nums[mid] < target <= nums[right]:
            left = mid + 1
        else:
            right = mid - 1
```

**Key problems:** Search in Rotated Sorted Array, Find Minimum in Rotated Array, Find First and Last Position.

---

## 15. Monotonic Stack / Queue

**Problem shape:** "Next greater/smaller element", "span of prices", "sliding window max/min".

**Recognize it when:** For each element, you need to find the nearest element that is greater or smaller; or sliding window extremes.

**Complexity:** O(n) time — each element pushed and popped at most once. O(n) space.

```python
# Next Greater Element — monotonic decreasing stack
stack = []   # stores indices
result = [-1] * len(nums)

for i in range(len(nums)):
    while stack and nums[i] > nums[stack[-1]]:
        idx = stack.pop()
        result[idx] = nums[i]    # nums[i] is next greater for idx
    stack.append(i)

# Sliding Window Maximum — monotonic deque (indices)
from collections import deque
dq = deque()   # stores indices, decreasing by value
for i in range(len(nums)):
    while dq and dq[0] < i - k + 1:
        dq.popleft()             # evict out-of-window
    while dq and nums[i] >= nums[dq[-1]]:
        dq.pop()                 # evict smaller elements
    dq.append(i)
    if i >= k - 1:
        result.append(nums[dq[0]])
```

**Key problems:** Next Greater Element, Daily Temperatures, Sliding Window Maximum, Largest Rectangle in Histogram, Trapping Rain Water.
