# Smart Caching and Predictive File Prefetching System

## Overview

The **Smart Caching and Predictive File Prefetching System** is a Python-based project that simulates file management, caching, and predictive prefetching techniques.

The system analyzes file access patterns and predicts which file may be accessed next. By using caching and prefetching techniques, it aims to reduce access time and improve system performance.

## Objectives

- Simulate a virtual file system.
- Implement different file allocation techniques.
- Implement LRU-based caching.
- Predict future file accesses using access patterns.
- Perform predictive file prefetching.
- Compare cache performance using hits, misses, and other metrics.
- Analyze the performance of predictive caching against traditional caching.

## Technologies Used

- **Python** – Core programming language
- **Tkinter** – Graphical user interface
- **SQLite** – Database for storing file and access information
- **Data Structures & Algorithms** – Cache management and prediction logic

## Features

- Virtual file and directory management
- File allocation simulation:
  - Contiguous Allocation
  - Linked Allocation
  - Indexed Allocation
- LRU (Least Recently Used) cache replacement
- Predictive file prefetching
- Markov-based file access prediction
- File access history tracking
- Cache hit and miss monitoring
- Prefetch tracking
- Performance comparison and analysis

## System Architecture

The project consists of the following major components:

1. **Virtual File System** – Simulates file and directory operations.
2. **File Allocation Manager** – Simulates contiguous, linked, and indexed file allocation.
3. **Access Logger** – Records file access history.
4. **Prediction Engine** – Uses access patterns and Markov-based prediction to identify the next probable file.
5. **Cache Manager** – Manages cached files using the LRU replacement policy.
6. **Prefetching Engine** – Loads predicted files into cache before their actual access.
7. **Performance Analyzer** – Tracks and evaluates cache performance.

## Working

1. The user accesses a file in the simulated file system.
2. The system records the file access.
3. The cache manager checks whether the file is already present in the cache.
4. If the file is present, a **Cache Hit** occurs.
5. If the file is absent, a **Cache Miss** occurs.
6. The prediction engine analyzes previous access patterns.
7. The system predicts the next file access.
8. The predicted file may be prefetched into the cache.
9. Cache performance metrics are updated.

## Performance Metrics

The system tracks metrics such as:

- Cache Hits
- Cache Misses
- Cache Hit Ratio
- Cache Miss Ratio
- Prefetched Files
- Useful Prefetches
- Wasted Prefetches
- File Access Statistics

## Project Structure

```text
Smart-Caching-and-predictive-file-Prefetching-System/
│
├── complete/
│   ├── Python source files
│   ├── Database files
│   ├── Virtual file system
│   └── Other project resources
│
├── README.md
└── Other project files
```

*Note: The project structure may vary according to the actual files.*

## How to Run

1. Install Python 3 on your system.
2. Clone this repository:

   ```bash
   git clone https://github.com/lakshya0122/Smart-Caching-and-predictive-file-Prefetching-System-.git
   ```

3. Navigate to the project folder.
4. Run the main Python file:

   ```bash
   python main.py
   ```

   Replace `main.py` with the actual entry-point filename of the project if different.

## Project Purpose

This project demonstrates how caching, file management, access pattern analysis, and predictive prefetching can be combined to improve file access efficiency through simulation.

## Contributors

- Lakshya Shukla
- Jigyasa Verma
- Daksh Bahuguna
- Swastika Somvanshi

