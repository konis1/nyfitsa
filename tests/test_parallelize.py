import timeit
from typing import List, Dict, Any
import os
from tqdm import tqdm
from concurrent.futures import (ProcessPoolExecutor, ThreadPoolExecutor,
                                as_completed)

from nyfitsa.nyfitsa import fetch_single_site_infos, Results

urls: List[str] = []

with open("urls.txt", "r") as file:
    for line in file:
        urls.append(line.strip())


def fetching_urls_concurrent(
        urls: List[str],
        number_of_workers: int,
        use_threads: bool = True,
        ) -> Results:
    websites: List[Dict[str, Any]] = []

    class_executor = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

    with class_executor(max_workers=number_of_workers) as executor:
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


cpu: int | None = os.cpu_count()
workers: List[int] = [2, cpu, cpu*2] if cpu is not None else [2]


def benchmark_fetching_urls_concurrent(
        use_threads: bool,
        worker: int
        ) -> float:
    return timeit.timeit(
        lambda: fetching_urls_concurrent(urls, worker, use_threads),
        number=5
    )


for worker in workers:

    thread_time = benchmark_fetching_urls_concurrent(True, worker)
    process_time = benchmark_fetching_urls_concurrent(False, worker)

    # Display results
    print(f"Worker count: {worker}")
    print(f"ThreadPoolExecutor time: {thread_time:.2f} seconds")
    print(f"ProcessPoolExecutor time: {process_time:.2f} seconds")

    # Compare results
    if thread_time < process_time:
        print("ThreadPoolExecutor is faster")
    else:
        print("ProcessPoolExecutor is faster")
