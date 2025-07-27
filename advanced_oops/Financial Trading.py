# Financial_Trading_System_with_Multiple_Inheritance.py

class TradingAccount:
    def __init__(self, account_id):
        self.account_id = account_id
        self.balance = 0
        self.portfolio = {}
    
    def deposit(self, amount):
        self.balance += amount
        print(f"[TradingAccount] Deposited {amount}. New balance: {self.balance}")
    
    def withdraw(self, amount):
        if amount > self.balance:
            print("[TradingAccount] Insufficient funds.")
            return False
        self.balance -= amount
        print(f"[TradingAccount] Withdrew {amount}. New balance: {self.balance}")
        return True
    
    def show_portfolio(self):
        print(f"[TradingAccount] Portfolio: {self.portfolio}")
        return self.portfolio

class RiskManagement:
    def assess_risk(self, symbol, amount):
        # Dummy risk logic: don't allow trades > 50% of balance
        if hasattr(self, 'balance'):
            if amount > self.balance * 0.5:
                print(f"[RiskManagement] Trade for {symbol} is too risky!")
                return False
            print(f"[RiskManagement] Trade for {symbol} is within risk limits.")
            return True
        print("[RiskManagement] No balance info available.")
        return False

class AnalyticsEngine:
    def analyze_market(self, symbol):
        # Dummy analysis
        print(f"[AnalyticsEngine] Analyzing market for {symbol}...")
        return {"trend": "up", "confidence": 0.8}

    def performance_metrics(self):
        # Dummy performance
        print("[AnalyticsEngine] Calculating performance metrics...")
        return {"return": 0.12, "sharpe_ratio": 1.5}

class NotificationSystem:
    def send_alert(self, message):
        print(f"[NotificationSystem] ALERT: {message}")

    def report(self, data):
        print(f"[NotificationSystem] REPORT: {data}")

# Derived Classes

class StockTrader(TradingAccount, RiskManagement, AnalyticsEngine):
    def __init__(self, account_id):
        TradingAccount.__init__(self, account_id)
    
    def trade_stock(self, symbol, amount):
        print(f"[StockTrader] Attempting to trade {symbol} for {amount}")
        if not self.assess_risk(symbol, amount):
            print("[StockTrader] Trade blocked by risk management.")
            return
        if not self.withdraw(amount):
            print("[StockTrader] Trade failed due to insufficient funds.")
            return
        self.portfolio[symbol] = self.portfolio.get(symbol, 0) + amount
        print(f"[StockTrader] Bought {symbol} for {amount}.")
    
    def performance_metrics(self):
        # Override to add stock-specific metrics
        base_metrics = super().performance_metrics()
        base_metrics["type"] = "stock"
        print(f"[StockTrader] Performance: {base_metrics}")
        return base_metrics

class CryptoTrader(TradingAccount, RiskManagement, NotificationSystem):
    def __init__(self, account_id):
        TradingAccount.__init__(self, account_id)
    
    def trade_crypto(self, symbol, amount):
        print(f"[CryptoTrader] Attempting to trade {symbol} for {amount}")
        if not self.assess_risk(symbol, amount):
            self.send_alert(f"Trade for {symbol} blocked by risk management.")
            return
        if not self.withdraw(amount):
            self.send_alert("Trade failed due to insufficient funds.")
            return
        self.portfolio[symbol] = self.portfolio.get(symbol, 0) + amount
        self.send_alert(f"Bought {symbol} for {amount}.")
    
    def performance_metrics(self):
        # Override to add crypto-specific metrics
        print("[CryptoTrader] Calculating crypto performance metrics...")
        return {"return": 0.2, "sharpe_ratio": 2.0, "type": "crypto"}

# ProfessionalTrader inherits from both StockTrader and CryptoTrader
class ProfessionalTrader(StockTrader, CryptoTrader):
    def __init__(self, account_id):
        StockTrader.__init__(self, account_id)
        # CryptoTrader.__init__ is not called to avoid double-initialization of TradingAccount
    
    def trade(self, asset_type, symbol, amount):
        if asset_type == "stock":
            self.trade_stock(symbol, amount)
        elif asset_type == "crypto":
            self.trade_crypto(symbol, amount)
        else:
            print("[ProfessionalTrader] Unknown asset type.")
    
    def performance_metrics(self):
        # Combine both stock and crypto metrics
        stock_metrics = StockTrader.performance_metrics(self)
        crypto_metrics = CryptoTrader.performance_metrics(self)
        combined = {
            "stock": stock_metrics,
            "crypto": crypto_metrics
        }
        print(f"[ProfessionalTrader] Combined Performance: {combined}")
        return combined

    # Handle method conflicts: prefer NotificationSystem's send_alert
    def send_alert(self, message):
        NotificationSystem.send_alert(self, message)

# --- Example Usage / Test Cases ---

if __name__ == "__main__":
    print("=== StockTrader Demo ===")
    st = StockTrader("ST123")
    st.deposit(1000)
    st.trade_stock("AAPL", 400)
    st.trade_stock("AAPL", 600)  # Should be blocked by risk
    st.show_portfolio()
    st.performance_metrics()
    print()

    print("=== CryptoTrader Demo ===")
    ct = CryptoTrader("CT456")
    ct.deposit(2000)
    ct.trade_crypto("BTC", 1200)
    ct.trade_crypto("ETH", 900)  # Should be blocked by risk
    ct.show_portfolio()
    ct.performance_metrics()
    print()

    print("=== ProfessionalTrader Demo ===")
    pt = ProfessionalTrader("PT789")
    pt.deposit(5000)
    pt.trade("stock", "GOOG", 2000)
    pt.trade("crypto", "BTC", 1000)
    pt.trade("crypto", "ETH", 3000)  # Should be blocked by risk
    pt.show_portfolio()
    pt.performance_metrics()
    pt.send_alert("End of trading day.")
