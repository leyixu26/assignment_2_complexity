from data_loader import load_market_data_limited
from strategies import NaiveMovingAverageStrategy, WindowedMovingAverageStrategy
from profiler import benchmark_all, print_summary
from reporting import generate_report, generate_plots

def main():
    filepath = "market_data.csv"
    window_size = 10

    # run benchmark
    results = benchmark_all(filepath, window_size)
    print_summary(results)

    # generate plots
    generate_plots(results, window_size)

    # generate report
    generate_report(results, window_size)

    print("complete")

if __name__ == "__main__":
    main()

    