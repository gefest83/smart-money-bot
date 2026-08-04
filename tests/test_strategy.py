from app.strategies.smart_money import SmartMoneyStrategy


def make_candles(prices):
    # return [timestamp, open, high, low, close, volume]
    candles = []
    for i, p in enumerate(prices):
        candles.append([i * 60_000, p * 0.99, p * 1.01, p * 0.98, p, 1.0])
    return candles


def test_generate_signals_simple():
    strat = SmartMoneyStrategy(structure_period=2, confirmation='Body', volatility_multiplier=1.0, atr_period=2)
    # create small price series with a breakout up
    prices = [100, 101, 102, 110, 111, 112]
    candles = make_candles(prices)
    signals = strat.generate_signals(candles)
    # expect at least one signal
    assert isinstance(signals, dict)

    # ensure no exception and signals is a dict
    # further behavioral tests can be added
