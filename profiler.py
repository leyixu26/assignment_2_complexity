import timeit
import cProfile
import pstats
import io
from pympler import asizeof
from memory_profiler import memory_usage
from data_loader import load_market_data_limited
from strategies import NaiveMovingAverageStrategy, WindowedMovingAverageStrategy

WINDOW_SIZE = 10

def run_strategy(strategy, data_points):
    for tick in data_points:
        strategy.generate_signals(tick)

def measure_runtime(strategy_class, data_points, window_size):
    strategy = strategy_class(window_size = window_size)

    start = timeit.default_timer()
    run_strategy(strategy, data_points)
    end = timeit.default_timer()

    return end - start

def measure_memory(strategy_class, data_points, window_size):
    strategy = strategy_class(window_size = window_size)
    run_strategy(strategy, data_points)

    memory_bytes = asizeof.asizeof(strategy)

    return memory_bytes / (1024 * 1024)

def profile_with_cprofile(strategy_class, data_points, window_size):
    strategy = strategy_class(window_size = window_size)

    profiler = cProfile.Profile()
    profiler.enable()
    run_strategy(strategy, data_points)
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats = stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return stream.getvalue()

def benchmark_all(filepath: str, window_size: int):
    results = []
    sizes = [1000, 10000, 100000]

    for size in sizes:
        data = load_market_data_limited(filepath, size)

        naive_time = measure_runtime(NaiveMovingAverageStrategy, data, window_size)
        naive_memory = measure_memory(NaiveMovingAverageStrategy, data, window_size)

        results.append({
            'Strategy': 'NaiveMovingAverageStrategy',
            'ticks': size,
            'runtime': naive_time,
            'memory': naive_memory
        })

        windowed_time = measure_runtime(WindowedMovingAverageStrategy, data, window_size)
        windowed_memory = measure_memory(WindowedMovingAverageStrategy, data, window_size)

        results.append({
            'Strategy': 'WindowedMovingAverageStrategy',
            'ticks': size,
            'runtime': windowed_time,
            'memory': windowed_memory
        })
    
    return results

def print_summary(results):
    print(f"{'Strategy':<12} {'ticks':<10} {'runtime (s)':<14} {'memory (MB)':<12}")
    print("-" * 60)
    
    for r in results:
        print(f"{r['Strategy']:<12} {r['ticks']:<10,} {r['runtime']:<14.4f} {r['memory']:<12.2f}")

