import timeit
from typing import List, Dict, Any
import os
from tqdm import tqdm
from concurrent.futures import (ProcessPoolExecutor, ThreadPoolExecutor,
                                as_completed)

import pandas as pd
import matplotlib.pyplot as plt

from nyfitsa.nyfitsa import fetch_single_site_infos, Results

urls: List[str] = []

with open("../urls.txt", "r") as file:
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
workers: List[int] = [int(cpu/2), cpu, cpu*2] if cpu is not None else [8]
benchmark_results: Dict[str, List[Any]] = {
    "Worker Count": [],
    "ThreadPoolExecutorTime": [],
    "ProcessPoolExecutorTime": [],
}


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

    benchmark_results["Worker Count"].append(worker)
    benchmark_results["ThreadPoolExecutorTime"].append(thread_time)
    benchmark_results["ProcessPoolExecutorTime"].append(process_time)

df = pd.DataFrame(benchmark_results)

# Plot the results as a bar graph
df.set_index("Worker Count").plot(kind="bar", width=0.8)  # type: ignore

# Add labels and title
plt.xlabel("Worker Count")  # type: ignore
plt.ylabel("Execution Time (seconds)")  # type: ignore
plt.title("Benchmark: ThreadPoolExecutor vs ProcessPoolExecutor")  # type: ignore
plt.legend(["ThreadPoolExecutor", "ProcessPoolExecutor"])  # type: ignore

plt.savefig("bar_graph.png")  # type: ignore
print("Graph saved as 'bar_graph.png'")
