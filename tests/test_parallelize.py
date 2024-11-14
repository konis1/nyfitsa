import timeit
from typing import List, Dict, Any
import os
import multiprocessing
from tqdm import tqdm
from concurrent.futures import (ProcessPoolExecutor, ThreadPoolExecutor,
                                as_completed)

from nyfitsa.nyfitsa import fetch_single_site_infos, Results

urls: List[str] = []

with open("urls.txt", "r") as file:
    for line in file:
        urls.append(line.strip())


def fetching_urls_conccurent(
        urls: List[str],
        use_threads: bool = True
        ) -> Results:
    websites: List[Dict[str, Any]] = []
    workers: int | None = min(os.cpu_count() or 1, 8)
    class_executor = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

    with class_executor(max_workers=workers) as executor:
        future_to_url = {
            executor.submit(fetch_single_site_infos, url):
            url for url in urls
            }
        for future in tqdm(
            as_completed(future_to_url),
            total=len(urls),
            desc="Getting sites infos",
            colour="green"
        ):
            websites.append(future.result())
    results = Results.model_validate({"site_infos": websites})
    return results


def parralelize_fetching(urls: List[str]) -> Results:
    websites: List[Dict[str, Any]] = []
    workers: int | None = min(os.cpu_count() or 1, 8)

    # with ProcessPoolExecutor(max_workers=workers) as executor:
    with multiprocessing.Pool(workers) as pool:
        for site_info in tqdm(
            pool.imap_unordered(
                fetch_single_site_infos,
                urls
                ),
            total=len(urls),
            desc="Getting sites infos",
            colour="green"
        ):
            websites.append(site_info)
    results = Results.model_validate({"site_infos": websites})
    return results


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
