# Real-Time Trading Strategy Performance Analysis

A performance analysis project comparing two implementations of a moving average trading strategy: a naive approach that stores all historical data versus an optimized windowed approach using a deque with a running sum.

## Project Overview

This project benchmarks and analyzes the time and space complexity of two moving average trading strategies:
- **NaiveMovingAverageStrategy**: Stores all price history, O(n) space complexity
- **WindowedMovingAverageStrategy**: Uses a fixed-size deque with running sum, O(k) space complexity

The analysis demonstrates how algorithmic optimization can achieve significant performance improvements while maintaining correctness.

## Features

- Performance benchmarking (runtime and memory usage)
- Complexity analysis and reporting
- Visual performance plots
- Comprehensive test suite
- Market data download and generation

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd assignment_2
   ```

2. **Install required dependencies:**
   ```bash
   pip install yfinance pandas numpy matplotlib pympler memory-profiler
   ```

   Or create a `requirements.txt` file with:
   ```
   yfinance>=0.2.0
   pandas>=1.5.0
   numpy>=1.23.0
   matplotlib>=3.6.0
   pympler>=0.9
   memory-profiler>=0.60.0
   ```

   Then install:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download market data:**
   ```bash
   python download_data.py
   ```
   
   This script:
   - Downloads real ANET stock data from Yahoo Finance
   - Generates synthetic data to reach ~105,000 rows
   - Saves data to `market_data.csv`
   - Creates visualization charts (`price_series.png`, `price_series_zoomed.png`)

## Usage

### Running the Main Analysis

Execute the main script to run benchmarks and generate reports:

```bash
python main.py
```

This will:
1. Benchmark both strategies with different input sizes (1k, 10k, 100k ticks)
2. Print a summary table of results
3. Generate performance plots (`performance_plots.png`)
4. Generate a detailed complexity report (`complexity_report.md`)

### Running Tests

Run the test suite to verify correctness and performance:

```bash
python -m unittest tests.test_strategies
```

Or run with verbose output:

```bash
python -m unittest tests.test_strategies -v
```

## Module Descriptions

### `main.py`
Entry point for the application. Orchestrates benchmarking, plotting, and report generation.

**Key Functions:**
- `main()`: Runs the complete analysis pipeline

### `models.py`
Defines core data structures and abstract interfaces.

**Classes:**
- `MarketDataPoint`: Immutable dataclass representing a single market tick (timestamp, symbol, price)
- `Strategy`: Abstract base class defining the interface for trading strategies

### `strategies.py`
Implements two moving average trading strategies.

**Classes:**
- `NaiveMovingAverageStrategy`: 
  - Stores all price history in a list
  - Time: O(k) per tick, O(n*k) total
  - Space: O(n)
  
- `WindowedMovingAverageStrategy`:
  - Uses `deque` with `maxlen` and maintains a running sum
  - Time: O(1) per tick, O(n) total
  - Space: O(k) where k is window size

**Signal Generation:**
- Returns `["Long"]` when price > moving average
- Returns `["Short"]` when price < moving average
- Returns `["Hold"]` when price == moving average or before window is filled

### `data_loader.py`
Handles loading market data from CSV files.

**Functions:**
- `parse_timestamp(timestamp_str)`: Parses timestamp strings to datetime objects
- `load_market_data(filename)`: Loads all data from CSV (not used in main flow)
- `load_market_data_limited(filename, limit)`: Loads a specified number of rows for benchmarking

### `profiler.py`
Performance measurement and benchmarking utilities.

**Functions:**
- `run_strategy(strategy, data_points)`: Executes a strategy on a dataset
- `measure_runtime(strategy_class, data_points, window_size)`: Measures execution time
- `measure_memory(strategy_class, data_points, window_size)`: Measures memory usage
- `profile_with_cprofile(strategy_class, data_points, window_size)`: Generates detailed profiling output
- `benchmark_all(filepath, window_size)`: Runs benchmarks for both strategies at multiple input sizes
- `print_summary(results)`: Prints formatted benchmark results

### `reporting.py`
Generates analysis reports and visualizations.

**Functions:**
- `generate_plots(results, window_size)`: Creates performance plots (runtime and memory vs input size)
- `generate_report(results, window_size)`: Generates comprehensive markdown report with:
  - Runtime and memory metrics table
  - Complexity annotations
  - Plot analysis
  - Narrative performance analysis

### `download_data.py`
Downloads real market data and generates synthetic data for testing.

**Features:**
- Downloads ANET stock data from Yahoo Finance (7 days, 1-minute intervals)
- Generates synthetic data using random walk model
- Combines real and synthetic data to reach target size
- Creates visualization charts of the price series

## Output Files

- `market_data.csv`: Market data file (timestamp, symbol, price)
- `performance_plots.png`: Runtime and memory usage plots
- `complexity_report.md`: Detailed complexity analysis report
- `price_series.png`: Full price series visualization
- `price_series_zoomed.png`: Zoomed views of price data

## Performance Requirements

The optimized `WindowedMovingAverageStrategy` meets the following requirements:
- **Runtime**: < 1 second for 100k ticks
- **Memory**: < 100 MB for 100k ticks

## Key Findings

- **Runtime**: Windowed strategy is ~1.6x faster for large datasets
- **Memory**: Windowed strategy uses constant memory (~0.00 MB) vs linear growth (3.05 MB for 100k ticks)
- **Scalability**: Windowed strategy maintains O(1) per-tick operations vs O(k) for naive approach
- **Correctness**: Both strategies produce identical trading signals

## Project Structure

```
assignment_2/
├── main.py                 # Entry point
├── models.py               # Data models
├── strategies.py           # Strategy implementations
├── data_loader.py          # Data loading utilities
├── profiler.py             # Performance benchmarking
├── reporting.py            # Report generation
├── download_data.py        # Data download script
├── market_data.csv         # Market data (generated)
├── complexity_report.md    # Analysis report (generated)
├── performance_plots.png   # Performance charts (generated)
├── price_series.png        # Price visualization (generated)
├── price_series_zoomed.png # Zoomed price chart (generated)
└── tests/
    └── test_strategies.py  # Unit tests
```

## License

This project is part of a Real-Time Systems assignment.

## Author

Assignment 2 - Real-Time Systems

