import timeit
from typing import List

from nyfitsa.nyfitsa import fetching_urls_concurrently, parralelize_fetching

urls: List[str] = []

with open("urls.txt", "r") as file:
    for line in file:
        urls.append(line.strip())


def benchmark_fetching_urls_concurrently():
    fetching_urls_concurrently(urls)


def benchmark_parralelize_fetching():
    parralelize_fetching(urls)


# Run benchmarks
concurrent_time: float = timeit.timeit(
    benchmark_fetching_urls_concurrently, number=5
    )
parallel_time: float = timeit.timeit(benchmark_parralelize_fetching, number=5)

# Display results
print(f"ThreadPoolExecutor time: {concurrent_time:.2f} seconds")
print(f"multiprocessing.Pool time: {parallel_time:.2f} seconds")

# Compare results
if concurrent_time < parallel_time:
    print("fetching_urls_concurrently (ThreadPoolExecutor) is faster")
else:
    print("parralelize_fetching (multiprocessing.Pool) is faster")
