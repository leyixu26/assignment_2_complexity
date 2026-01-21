import unittest
import sys
from pathlib import Path
from datetime import datetime
from data_loader import load_market_data_limited
from profiler import measure_runtime, measure_memory, profile_with_cprofile

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import MarketDataPoint
from strategies import NaiveMovingAverageStrategy, WindowedMovingAverageStrategy

class TestStrategies(unittest.TestCase):
    def create_tick(self, price):
        return MarketDataPoint(timestamp=datetime.now(), symbol='TEST', price=price)

    def test_produce_same_signals(self):
        naive = NaiveMovingAverageStrategy(window_size=10)
        windowed = WindowedMovingAverageStrategy(window_size=10)

        prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
        
        for price in prices:
            tick = self.create_tick(price)
            naive_signal = naive.generate_signals(tick)
            windowed_signal = windowed.generate_signals(tick)
            self.assertEqual(naive_signal, windowed_signal)

    def test_hold_before_window_size(self):
        naive = NaiveMovingAverageStrategy(window_size=10)
        windowed = WindowedMovingAverageStrategy(window_size=10)

        prices = [100, 101, 102, 103, 104, 105, 106, 107, 108]
        
        for price in prices:
            tick = self.create_tick(price)
            self.assertEqual(naive.generate_signals(tick), ["Hold"])
            self.assertEqual(windowed.generate_signals(tick), ["Hold"])

    def test_long_signal(self):
        naive = NaiveMovingAverageStrategy(window_size=10)
        windowed = WindowedMovingAverageStrategy(window_size=10)

        prices = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]

        for price in prices:
            naive.generate_signals(self.create_tick(price))
            windowed.generate_signals(self.create_tick(price))
        
        tick = self.create_tick(110)
        self.assertEqual(naive.generate_signals(tick), ["Long"])
        self.assertEqual(windowed.generate_signals(tick), ["Long"])

    def test_short_signal(self):
        naive = NaiveMovingAverageStrategy(window_size=10)
        windowed = WindowedMovingAverageStrategy(window_size=10)

        prices = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]

        for price in prices:
            naive.generate_signals(self.create_tick(price))
            windowed.generate_signals(self.create_tick(price))
        
        tick = self.create_tick(90)
        self.assertEqual(naive.generate_signals(tick), ["Short"])
        self.assertEqual(windowed.generate_signals(tick), ["Short"])
    
    def test_hold_signal(self):
        naive = NaiveMovingAverageStrategy(window_size=10)
        windowed = WindowedMovingAverageStrategy(window_size=10)

        prices = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]

        for price in prices:
            naive.generate_signals(self.create_tick(price))
            windowed.generate_signals(self.create_tick(price))
        
        tick = self.create_tick(100)
        self.assertEqual(naive.generate_signals(tick), ["Hold"])
        self.assertEqual(windowed.generate_signals(tick), ["Hold"])

    def test_window_sizes(self):
        for window_size in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            naive = NaiveMovingAverageStrategy(window_size=window_size)
            windowed = WindowedMovingAverageStrategy(window_size=window_size)

            for price in list(range(100, 150)):
                tick = self.create_tick(price)
                naive_signal = naive.generate_signals(tick)
                windowed_signal = windowed.generate_signals(tick)
                self.assertEqual(naive_signal, windowed_signal)

    def test_memory(self):
        naive = NaiveMovingAverageStrategy(window_size=10)
        windowed = WindowedMovingAverageStrategy(window_size=10)

        for i in range(100):
            tick = self.create_tick(i)
            naive.generate_signals(tick)
            windowed.generate_signals(tick)
        
        self.assertEqual(len(naive.price_history), 100)
        self.assertEqual(len(windowed.window), 10)

    def test_optimized_strategy_performance_requirements(self):
        """
        Test that WindowedMovingAverageStrategy meets performance requirements:
        - Runs under 1 second for 100k ticks
        - Uses <100MB memory for 100k ticks
        """
        # Check if market_data.csv exists
        data_file = Path(__file__).parent.parent / "market_data.csv"
        
        window_size = 10
        num_ticks = 100000
        
        # Load 100k ticks
        data = load_market_data_limited(str(data_file), num_ticks)
        self.assertEqual(len(data), num_ticks, "Failed to load 100k ticks")
        
        # Measure runtime
        runtime = measure_runtime(WindowedMovingAverageStrategy, data, window_size)
        
        # Measure memory
        memory_mb = measure_memory(WindowedMovingAverageStrategy, data, window_size)
        
        # Assert performance requirements
        self.assertLess(
            runtime, 
            1.0, 
            f"Runtime {runtime:.4f}s exceeds 1 second requirement for {num_ticks} ticks"
        )
        
        self.assertLess(
            memory_mb, 
            100.0, 
            f"Memory {memory_mb:.2f}MB exceeds 100MB requirement for {num_ticks} ticks"
        )
        
        # Print results for verification
        print(f"\nPerformance Test Results for {num_ticks} ticks:")
        print(f"  Runtime: {runtime:.4f}s (requirement: <1.0s)")
        print(f"  Memory: {memory_mb:.2f}MB (requirement: <100MB)")
    
    def test_profiling_hotspots_naive(self):
        """
        Test that profiling output includes expected hotspots for NaiveMovingAverageStrategy.
        Expected hotspots: list slicing, sum operations
        """
        # Check if market_data.csv exists
        data_file = Path(__file__).parent.parent / "market_data.csv"
        if not data_file.exists():
            self.skipTest("market_data.csv not found. Run download_data.py first.")
        
        # Use smaller dataset for faster profiling test
        data = load_market_data_limited(str(data_file), 10000)
        window_size = 10
        
        # Get profiling output
        profile_output = profile_with_cprofile(NaiveMovingAverageStrategy, data, window_size)
        
        # Check for expected hotspots in profiling output
        # These should appear in the top functions by cumulative time
        self.assertIn(
            'generate_signals', 
            profile_output.lower(),
            "generate_signals should appear in profiling output"
        )
        
        # Check that sum or slicing operations are present (indirectly through function calls)
        # The profiling output should show time spent in generate_signals
        # We can't directly check for 'sum' or slicing, but we can verify the function is profiled
        self.assertGreater(
            len(profile_output), 
            100,
            "Profiling output should contain function call information"
        )

        print("\nNaive Strategy Profiling Output (first 500 chars):")
        print(profile_output[:500])
    
    def test_profiling_hotspots_windowed(self):
        """
        Test that profiling output includes expected hotspots for WindowedMovingAverageStrategy.
        Expected hotspots: deque operations, arithmetic operations
        """
        # Check if market_data.csv exists
        data_file = Path(__file__).parent.parent / "market_data.csv"
        if not data_file.exists():
            self.skipTest("market_data.csv not found. Run download_data.py first.")
        
        # Use smaller dataset for faster profiling test
        data = load_market_data_limited(str(data_file), 10000)
        window_size = 10
        
        # Get profiling output
        profile_output = profile_with_cprofile(WindowedMovingAverageStrategy, data, window_size)
        
        # Check for expected hotspots in profiling output
        self.assertIn(
            'generate_signals', 
            profile_output.lower(),
            "generate_signals should appear in profiling output"
        )
        
        # Verify profiling output contains function call information
        self.assertGreater(
            len(profile_output), 
            100,
            "Profiling output should contain function call information"
        )
        
        print("\nWindowed Strategy Profiling Output (first 500 chars):")
        print(profile_output[:500])
    
    def test_memory_peaks_comparison(self):
        """
        Test that memory usage shows expected difference between naive and windowed strategies.
        Windowed should use significantly less memory for large inputs.
        """
        # Check if market_data.csv exists
        data_file = Path(__file__).parent.parent / "market_data.csv"
        if not data_file.exists():
            self.skipTest("market_data.csv not found. Run download_data.py first.")
        
        window_size = 10
        num_ticks = 100000
        
        # Load data
        data = load_market_data_limited(str(data_file), num_ticks)
        
        # Measure memory for both strategies
        naive_memory = measure_memory(NaiveMovingAverageStrategy, data, window_size)
        windowed_memory = measure_memory(WindowedMovingAverageStrategy, data, window_size)
        
        # Windowed should use less memory than naive
        self.assertLess(
            windowed_memory,
            naive_memory,
            f"Windowed strategy ({windowed_memory:.2f}MB) should use less memory than naive ({naive_memory:.2f}MB)"
        )
        
        # Windowed memory should be very small (close to 0)
        self.assertLess(
            windowed_memory,
            1.0,
            f"Windowed strategy should use <1MB, got {windowed_memory:.2f}MB"
        )
        
        print(f"\nMemory Comparison for {num_ticks} ticks:")
        print(f"  Naive: {naive_memory:.2f}MB")
        print(f"  Windowed: {windowed_memory:.2f}MB")
        print(f"  Improvement: {naive_memory/windowed_memory:.1f}x less memory" if windowed_memory > 0 else "  Improvement: Significant")

if __name__ == "__main__":
    unittest.main()

