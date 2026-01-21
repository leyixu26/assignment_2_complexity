from collections import deque
from models import MarketDataPoint, Strategy

class NaiveMovingAverageStrategy(Strategy):
    """
    Naive Moving Average Strategy

    Space Complexity : O(n) where n is the total ticks because it stores the entire price_history list.
    Space grows linearly with the size of the input.

    Time Complexity: O(k) per tick, k is the window size because it slices and sums the window for each tick.
    O(n*k) for n ticks. If k is a constant, the time complexity simplifies to O(n).
    """
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.price_history = [] # O(n) space

    def generate_signals(self, tick: MarketDataPoint) -> list:
        self.price_history.append(tick.price) # O(1) time

        if len(self.price_history) < self.window_size: # O(1) time
            return ["Hold"]

        window = self.price_history[-self.window_size:] # O(k) time, slicing creates a new list by copying the last k elements one by one
        average = sum(window) / self.window_size # O(k) time to sum the k window

        if tick.price > average: # O(1) time
            return ["Long"]
        elif tick.price < average: # O(1) time
            return ["Short"]
        else: # O(1) time
            return ["Hold"]


class WindowedMovingAverageStrategy(Strategy):
    """
    Windowed Moving Average Strategy

    Space Complexity: O(k) where k is the window size because it only stores the window deque and its running sum.
    Space is constant regardless of the number of ticks.

    Time Complexity: O(1) per tick because it only appends and pops from the deque and updates the running sum.
    O(n) for n ticks.
    """
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.window = deque(maxlen = window_size)  # O(k) space
        self.running_sum = 0.0   # O(1) space
    
    def generate_signals(self, tick:MarketDataPoint) -> list:
        if len(self.window) == self.window_size: # O(1) time
            self.running_sum -= self.window[0] # O(1) time to pop the first element from deque

        self.window.append(tick.price) # O(1) time to append the new element to the deque
        self.running_sum += tick.price # O(1) time to update the running sum

        if len(self.window) < self.window_size: # O(1) time
            return ["Hold"]
        
        average = self.running_sum / self.window_size # O(1) time to calculate the average (no summing operations)

        if tick.price > average: # O(1) time
            return ["Long"]
        elif tick.price < average: # O(1) time
            return ["Short"]
        else: # O(1) time
            return ["Hold"]




