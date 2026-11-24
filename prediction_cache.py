"""
prediction_cache.py - Prediction and caching part of the project.

Predictor : Markov-chain model that learns "after file A, file B is opened"
            from the access history and guesses the next file.
Cache     : Small in-memory cache with LRU eviction that can also
            pre-load (prefetch) the predicted file.
"""
from collections import Counter, defaultdict, OrderedDict

CACHE_CAPACITY = 4


class Predictor:
    def __init__(self):
        self.transitions = defaultdict(Counter)

    def train(self, sequence):
        self.transitions = defaultdict(Counter)
        for a, b in zip(sequence, sequence[1:]):
            self.transitions[a][b] += 1

    def predict(self, current, exclude=()):
        counts = self.transitions.get(current, Counter()).copy()
        for p in exclude:
            counts.pop(p, None)
        if not counts:
            return None, 0.0
        path, count = counts.most_common(1)[0]
        return path, count / sum(counts.values())

    def table(self):
        out = []
        for src, counts in sorted(self.transitions.items()):
            total = sum(counts.values())
            for dest, count in counts.most_common():
                out.append((src, dest, f"{count / total:.1%}", count))
        return out


class Cache:
    def __init__(self, capacity=CACHE_CAPACITY):
        self.capacity = capacity
        self.items = OrderedDict()
        self.prefetched = set()
        self.hits = self.misses = self.prefetches = 0
        self.useful = self.wasted = 0
        self.load_ms = 0.0

    def access(self, path, load_ms):
        if path in self.items:
            self.hits += 1
            self.items.move_to_end(path)
            if path in self.prefetched:
                self.prefetched.remove(path)
                self.useful += 1
            return True
        self.misses += 1
        self.load_ms += load_ms
        self._insert(path)
        return False

    def _insert(self, path):
        if path in self.items:
            self.items.move_to_end(path)
            return
        if len(self.items) >= self.capacity:
            evicted, _ = self.items.popitem(last=False)
            if evicted in self.prefetched:
                self.prefetched.remove(evicted)
                self.wasted += 1
        self.items[path] = True

    def prefetch(self, path):
        if not path or path in self.items:
            return False
        self._insert(path)
        self.prefetched.add(path)
        self.prefetches += 1
        return True

    def finish(self):
        self.wasted += len(self.prefetched)
        self.prefetched.clear()

    def reset_metrics(self):
        self.hits = self.misses = self.prefetches = self.useful = self.wasted = 0
        self.load_ms = 0.0
        self.prefetched.clear()
        self.items.clear()
