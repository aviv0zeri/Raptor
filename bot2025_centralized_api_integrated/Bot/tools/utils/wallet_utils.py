"""
💼 Wallet Utilities - The Digital Vault Management
Where balances are tracked and fortunes are calculated
"""

from colorama import Fore, Style
try:
    from ..api.api_utils import wallet_data, wallet_lock, get_non_zero_balances, get_asset_usd_value
except ImportError:
    # Fallback for IDE compatibility
    wallet_data = {}
    wallet_lock = None
    def get_non_zero_balances(client):
        return {}
    def get_asset_usd_value(asset, amount, client):
        return 0

def print_wallet():
    """
    💰 Display the cosmic wallet in all its colorful glory
    Shows non-zero balances with their USD values and total portfolio worth
    """
    with wallet_lock:
        non_zero_balances = wallet_data
    
    total_usd_value = 0.0

    print("\n 💼 Wallet:")
    for asset, info in non_zero_balances.items():
        formatted_amount = f"{info['balance']:.8f}"
        formatted_usd_value = f"{info['usd_value']:.6f}"
        print(f"\t{Fore.LIGHTYELLOW_EX}{asset: <10}{Fore.RESET}  {Fore.LIGHTYELLOW_EX}{formatted_amount}{Fore.LIGHTGREEN_EX}  ${formatted_usd_value} {Fore.RESET}")
        total_usd_value += info['usd_value']
    
    # Display the grand total
    print(f"\n 🌟 Total Portfolio Value: {Fore.GREEN}${total_usd_value:.6f}{Fore.RESET}")

def get_wallet_summary():
    """
    📊 Get a summary of the wallet without printing
    Returns total USD value and asset count for programmatic use
    """
    with wallet_lock:
        non_zero_balances = wallet_data
    
    total_usd_value = sum(info['usd_value'] for info in non_zero_balances.values())
    asset_count = len(non_zero_balances)
    
    return {
        'total_usd_value': total_usd_value,
        'asset_count': asset_count,
        'assets': non_zero_balances
    }

def get_asset_balance(asset_symbol):
    """
    🔍 Get the balance of a specific asset from the wallet
    Returns the balance and USD value for the requested asset
    """
    with wallet_lock:
        non_zero_balances = wallet_data
    
    asset_info = non_zero_balances.get(asset_symbol.upper())
    if asset_info:
        return {
            'balance': asset_info['balance'],
            'usd_value': asset_info['usd_value']
        }
    return None

def get_top_assets_by_value(limit=5):
    """
    🏆 Get the top assets by USD value in the wallet
    Useful for portfolio analysis and risk management
    """
    with wallet_lock:
        non_zero_balances = wallet_data
    
    # Sort assets by USD value in descending order
    sorted_assets = sorted(
        non_zero_balances.items(), 
        key=lambda x: x[1]['usd_value'], 
        reverse=True
    )
    
    return sorted_assets[:limit]

def calculate_portfolio_allocation():
    """
    📈 Calculate the percentage allocation of each asset in the portfolio
    Returns a dictionary with asset symbols and their allocation percentages
    """
    with wallet_lock:
        non_zero_balances = wallet_data
    
    total_usd_value = sum(info['usd_value'] for info in non_zero_balances.values())
    
    if total_usd_value == 0:
        return {}
    
    allocation = {}
    for asset, info in non_zero_balances.items():
        percentage = (info['usd_value'] / total_usd_value) * 100
        allocation[asset] = {
            'percentage': percentage,
            'usd_value': info['usd_value'],
            'balance': info['balance']
        }
    
    return allocation

def print_portfolio_allocation():
    """
    🎨 Display the portfolio allocation in a beautiful format
    Shows each asset's percentage of the total portfolio
    """
    allocation = calculate_portfolio_allocation()
    
    if not allocation:
        print("\n 💼 Portfolio is empty")
        return
    
    print("\n 📊 Portfolio Allocation:")
    print("=" * 50)
    
    # Sort by percentage in descending order
    sorted_allocation = sorted(
        allocation.items(), 
        key=lambda x: x[1]['percentage'], 
        reverse=True
    )
    
    for asset, info in sorted_allocation:
        percentage = info['percentage']
        usd_value = info['usd_value']
        
        # Create a visual bar
        bar_length = int(percentage / 2)  # Scale the bar
        bar = "█" * bar_length
        
        print(f"{Fore.LIGHTYELLOW_EX}{asset: <10}{Fore.RESET} {bar} {Fore.LIGHTGREEN_EX}{percentage:5.1f}%${Fore.RESET} {usd_value:.2f}")

def check_sufficient_balance(asset_symbol, required_amount):
    """
    ✅ Check if there's sufficient balance for a trade
    Returns True if balance is sufficient, False otherwise
    """
    asset_info = get_asset_balance(asset_symbol)
    
    if asset_info is None:
        return False
    
    return asset_info['balance'] >= required_amount

def get_available_trading_balance(asset_symbol):
    """
    💸 Get the available balance for trading (excluding locked amounts)
    Returns the free balance that can be used for new orders
    """
    asset_info = get_asset_balance(asset_symbol)
    
    if asset_info is None:
        return 0.0
    
    return asset_info['balance']
