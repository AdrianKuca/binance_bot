from strategy import StrategyBase
from utils.enums import Decision
from utils.indicators import rsi


class Strategy(StrategyBase):
    def __init__(self, start_fiat, start_crypto):
        self.rsi_window_size = 5
        self.rsi_min = 30
        self.rsi_max = 80
        super().__init__(start_fiat, start_crypto)

    def calculate_decision(self, data):
        decision = Decision.WAIT
        amount = 0
        if len(data) < self.rsi_window_size:
            rsi_value = 50
        else:
            rsi_value = rsi(data[:, 4], self.rsi_window_size)
        self.indicator_values.append(rsi_value)

        if rsi_value > self.rsi_max:
            if self.balance_crypto > 0:
                decision = Decision.SELL
                diff_percent = (rsi_value - self.rsi_max) / (100 - self.rsi_max)
                factor = 0.6 + diff_percent * 0.4
                amount = self.balance_crypto * factor
                if amount < 10 / data[-1, 4]:
                    decision = Decision.WAIT

        elif rsi_value < self.rsi_min:
            if self.balance_fiat > 0:
                decision = Decision.BUY
                diff_percent = (self.rsi_min - rsi_value) / self.rsi_min
                factor = 0.6 + diff_percent * 0.4
                amount = self.balance_fiat * factor
                if amount < 10:
                    decision = Decision.WAIT

        return decision, amount

    def _plot_indicator_over_time(self, ax):
        super()._plot_indicator_over_time(ax)
        ax.plot(self.times, self.indicator_values, color="red")
        ax.set_title(f"RSI with window size: {self.rsi_window_size}")
        ax.fill_between(self.times, 0, self.rsi_min, color="C0", alpha=0.3)
        ax.fill_between(self.times, self.rsi_max, 100, color="C0", alpha=0.3)
