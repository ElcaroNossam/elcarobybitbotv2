#!/usr/bin/env python3
"""
Wrap hardcoded strings in iOS Swift views with .localized calls.
Handles Text(), Label(), TextField(), confirmationDialog(), navigationTitle() etc.
"""
import re
import os

BASE = "ios/EnlikoTrading/EnlikoTrading"

# ============================================================================
# Replacement maps per file: (exact_old_string, exact_new_string)
# ============================================================================

POSITION_DETAIL_REPLACEMENTS = [
    # Toolbar menu items
    ('Label("Modify TP/SL", systemImage:', 'Label("pos_modify_tpsl".localized, systemImage:'),
    ('Label("Add to Position", systemImage: "plus.circle")', 'Label("pos_add_to_position".localized, systemImage: "plus.circle")'),
    ('Label("Close Position", systemImage: "xmark.circle")', 'Label("pos_close_position".localized, systemImage: "xmark.circle")'),
    # Confirmation dialog
    ('.confirmationDialog("Close Position", isPresented:', '.confirmationDialog("pos_close_position".localized, isPresented:'),
    ('Button("Close 100%", role: .destructive)', 'Button("pos_close_100".localized, role: .destructive)'),
    ('Text("Are you sure you want to close this position?")', 'Text("pos_close_confirm_msg".localized)'),
    # PnL card
    ('Text("Unrealized PnL")', 'Text("pos_unrealized_pnl".localized)'),
    ('Text("ROE")', 'Text("pos_roe".localized)'),
    ('Text("Size")', 'Text("pos_size".localized)'),
    ('Text("Value")', 'Text("pos_value".localized)'),
    # Position Details section
    ('Text("Position Details")', 'Text("pos_details".localized)'),
    ('detailRow("Entry Price",', 'detailRow("pos_entry_price".localized,'),
    ('detailRow("Mark Price",', 'detailRow("pos_mark_price".localized,'),
    ('detailRow("Liq. Price",', 'detailRow("pos_liq_price".localized,'),
    ('detailRow("Margin",', 'detailRow("pos_margin".localized,'),
    ('detailRow("Maintenance Margin",', 'detailRow("pos_maintenance_margin".localized,'),
    ('detailRow("Opened",', 'detailRow("pos_opened".localized,'),
    # TP/SL section
    ('Text("TP/SL")', 'Text("pos_tpsl".localized)'),
    ('Text("Modify")', 'Text("btn_modify".localized)'),
    ('Text("Take Profit")', 'Text("pos_take_profit".localized)'),
    ('Text("Not Set")', 'Text("pos_not_set".localized)'),
    ('Text("Stop Loss")', 'Text("pos_stop_loss".localized)'),
    # Quick actions
    ('Text("Quick Actions")', 'Text("pos_quick_actions".localized)'),
    ('Text("Partial Close")', 'Text("pos_partial_close".localized)'),
    ('Text("Add Position")', 'Text("pos_add_position".localized)'),
    ('Text("Flip")', 'Text("pos_flip".localized)'),
    ('Text("Close Position (100%)")', 'Text("pos_close_full".localized)'),
    # Partial close sheet
    ('Text("Close Partial Position")', 'Text("pos_close_partial_title".localized)'),
    ('Text("Closing Size")', 'Text("pos_closing_size".localized)'),
    ('Text("Estimated PnL")', 'Text("pos_estimated_pnl".localized)'),
    ('Text("Remaining Size")', 'Text("pos_remaining_size".localized)'),
    # Modify TP/SL sheet
    ('Text("Modify TP/SL")', 'Text("pos_modify_tpsl".localized)'),
    ('Text("Current Price")', 'Text("pos_current_price".localized)'),
    ('Label("Take Profit", systemImage:', 'Label("pos_take_profit".localized, systemImage:'),
    ('TextField("TP Price",', 'TextField("pos_tp_price".localized,'),
    ('Label("Stop Loss", systemImage:', 'Label("pos_stop_loss".localized, systemImage:'),
    ('TextField("SL Price",', 'TextField("pos_sl_price".localized,'),
    ('Text("Save Changes")', 'Text("btn_save_changes".localized)'),
    # Add to position sheet
    ('Text("Add to Position")', 'Text("pos_add_to_position".localized)'),
    ('Text("Current Position")', 'Text("pos_current_position".localized)'),
    ('Text("Amount to Add (USDT)")', 'Text("pos_amount_to_add".localized)'),
    ('TextField("Enter amount",', 'TextField("pos_enter_amount".localized,'),
    # Cancel buttons
    ('Text("Cancel")', 'Text("btn_cancel".localized)'),
    ('Button("Cancel", role: .cancel)', 'Button("btn_cancel".localized, role: .cancel)'),
]

HYPERLIQUID_REPLACEMENTS = [
    # Navigation title
    ('.navigationTitle("HyperLiquid")', '.navigationTitle("hl_title".localized)'),
    # Balance header
    ('Text("Total Balance")', 'Text("hl_total_balance".localized)'),
    ('Text("Perp")', 'Text("hl_perp".localized)'),
    ('Text("Spot")', 'Text("hl_spot".localized)'),
    # Quick Actions
    ('Text("Deposit")', 'Text("hl_deposit".localized)'),
    ('Text("Withdraw")', 'Text("hl_withdraw".localized)'),
    ('Text("Transfer")', 'Text("hl_transfer".localized)'),
    # Stats
    ('Text("24h Volume")', 'Text("hl_24h_volume".localized)'),
    ('Text("Open Interest")', 'Text("hl_open_interest".localized)'),
    ('Text("Funding Rate")', 'Text("hl_funding_rate".localized)'),
    ('Text("Positions")', 'Text("hl_positions".localized)'),
    # Margin details
    ('Text("Margin Details")', 'Text("hl_margin_details".localized)'),
    ('Text("Account Margin")', 'Text("hl_account_margin".localized)'),
    ('Text("Margin Ratio")', 'Text("hl_margin_ratio".localized)'),
    # Activity
    ('Text("Recent Activity")', 'Text("hl_recent_activity".localized)'),
    ('Text("See All")', 'Text("hl_see_all".localized)'),
    ('Text("No transfers yet")', 'Text("hl_no_transfers".localized)'),
    # Points section
    ('Text("HyperLiquid Points")', 'Text("hl_points_title".localized)'),
    ('Text("How to Earn")', 'Text("hl_how_to_earn".localized)'),
    ('Text("Trading Volume")', 'Text("hl_earn_trading".localized)'),
    ('Text("Earn 1 point per $1,000 traded")', 'Text("hl_earn_trading_desc".localized)'),
    ('Text("Referrals")', 'Text("hl_earn_referrals".localized)'),
    ('Text("Invite friends to join")', 'Text("hl_earn_referrals_desc".localized)'),
    ('Text("Daily Login")', 'Text("hl_earn_daily".localized)'),
    ('Text("Check in every day")', 'Text("hl_earn_daily_desc".localized)'),
    ('Text("Vault Deposits")', 'Text("hl_earn_vault".localized)'),
    ('Text("Deposit to earn extra")', 'Text("hl_earn_vault_desc".localized)'),
    # Deposit/Withdraw sheets
    ('Text("Deposit USDC")', 'Text("hl_deposit_usdc".localized)'),
    ('Text("Withdraw USDC")', 'Text("hl_withdraw_usdc".localized)'),
    ('Text("Destination Address")', 'Text("hl_dest_address".localized)'),
    ('Text("Internal Transfer")', 'Text("hl_internal_transfer".localized)'),
    ('Text("From")', 'Text("hl_from".localized)'),
    ('Text("To")', 'Text("hl_to".localized)'),
    # Vaults
    ('Text("Deposit to Vault")', 'Text("hl_deposit_to_vault".localized)'),
    ('Text("Vault Details")', 'Text("hl_vault_details".localized)'),
    ('Text("TVL")', 'Text("hl_tvl".localized)'),
    ('Text("Your Deposit")', 'Text("hl_your_deposit".localized)'),
    ('Text("Your PnL")', 'Text("hl_your_pnl".localized)'),
    ('Text("30d Return")', 'Text("hl_30d_return".localized)'),
    ('Text("PnL:")', 'Text("hl_pnl_label".localized)'),
    # Cancel
    ('Text("Cancel")', 'Text("btn_cancel".localized)'),
    ('Button("Cancel", role: .cancel)', 'Button("btn_cancel".localized, role: .cancel)'),
]

SPOT_TRADING_REPLACEMENTS = [
    # Navigation  (already uses .localized for some, skip those)
    # DCA strategy selection
    ('Text("Fixed")', 'Text("spot_dca_fixed".localized)'),
    ('Text("Same amount")', 'Text("spot_dca_fixed_desc".localized)'),
    ('Text("Value Avg")', 'Text("spot_dca_value_avg".localized)'),
    ('Text("Buy dips more")', 'Text("spot_dca_value_avg_desc".localized)'),
    ('Text("Fear/Greed")', 'Text("spot_dca_fear_greed".localized)'),
    ('Text("Fear = Buy more")', 'Text("spot_dca_fear_greed_desc".localized)'),
    ('Text("Crash Boost")', 'Text("spot_dca_crash_boost".localized)'),
    ('Text("3x on -15%")', 'Text("spot_dca_crash_boost_desc".localized)'),
    ('Text("Momentum")', 'Text("spot_dca_momentum".localized)'),
    ('Text("Follow trend")', 'Text("spot_dca_momentum_desc".localized)'),
    ('Text("RSI Smart")', 'Text("spot_dca_rsi".localized)'),
    ('Text("RSI < 30 buy")', 'Text("spot_dca_rsi_desc".localized)'),
    # Actions
    ('Text("Execute DCA")', 'Text("spot_execute_dca".localized)'),
    ('Text("Rebalance Now")', 'Text("spot_rebalance_now".localized)'),
    ('Text("Enable Auto DCA")', 'Text("spot_enable_auto_dca".localized)'),
    ('Text("Enable TP Levels")', 'Text("spot_enable_tp_levels".localized)'),
    ('Text("Trailing TP")', 'Text("spot_trailing_tp".localized)'),
    # Portfolio types
    ('Text("💎 Blue Chips")', 'Text("spot_port_blue_chip".localized)'),
    ('Text("🏦 DeFi")', 'Text("spot_port_defi".localized)'),
    ('Text("⚡ Layer 2")', 'Text("spot_port_layer2".localized)'),
    ('Text("🤖 AI & Data")', 'Text("spot_port_ai".localized)'),
    ('Text("🎮 Gaming")', 'Text("spot_port_gaming".localized)'),
    ('Text("🐕 Memecoins")', 'Text("spot_port_meme".localized)'),
    ('Text("⚔️ L1 Killers")', 'Text("spot_port_l1_killers".localized)'),
    ('Text("🏛️ RWA")', 'Text("spot_port_rwa".localized)'),
    ('Text("🔧 Infrastructure")', 'Text("spot_port_infra".localized)'),
    ('Text("₿ BTC Only")', 'Text("spot_port_btc_only".localized)'),
    ('Text("💰 ETH+BTC")', 'Text("spot_port_eth_btc".localized)'),
    ('Text("⚙️ Custom")', 'Text("spot_port_custom".localized)'),
    # Strategy labels
    ('Text("📊 Fixed")', 'Text("spot_strat_fixed".localized)'),
    ('Text("📈 Value Averaging")', 'Text("spot_strat_value_avg".localized)'),
    ('Text("😱 Fear & Greed")', 'Text("spot_strat_fear_greed".localized)'),
    ('Text("🚨 Crash Boost")', 'Text("spot_strat_crash_boost".localized)'),
    # Frequency
    ('Text("⏰ Hourly")', 'Text("spot_freq_hourly".localized)'),
    ('Text("📅 Daily")', 'Text("spot_freq_daily".localized)'),
    ('Text("📆 Weekly")', 'Text("spot_freq_weekly".localized)'),
    # TP presets
    ('Text("🐢 Conservative")', 'Text("spot_tp_conservative".localized)'),
    ('Text("⚖️ Balanced")', 'Text("spot_tp_balanced".localized)'),
    ('Text("🦁 Aggressive")', 'Text("spot_tp_aggressive".localized)'),
    ('Text("🌙 Moonbag")', 'Text("spot_tp_moonbag".localized)'),
    # Features
    ('Text("🔒 Profit Lock")', 'Text("spot_profit_lock".localized)'),
    ('Text("Sell 50% when +30% profit")', 'Text("spot_profit_lock_desc".localized)'),
    ('Text("⚖️ Auto Rebalance")', 'Text("spot_auto_rebalance".localized)'),
    ('Text("Rebalance when >10% drift")', 'Text("spot_rebalance_desc".localized)'),
    # Portfolio stats
    ('Text("Invested")', 'Text("spot_invested".localized)'),
    ('Text("Current Value")', 'Text("spot_current_value".localized)'),
    ('Text("Unrealized PnL")', 'Text("spot_unrealized_pnl".localized)'),
    ('Text("Fear & Greed Index")', 'Text("spot_fear_greed_index".localized)'),
    # Empty state
    ('Text("No Spot Holdings")', 'Text("spot_no_holdings".localized)'),
    ('Text("Start building your portfolio with DCA")', 'Text("spot_no_holdings_desc".localized)'),
    ('Text("Buy Crypto")', 'Text("spot_buy_crypto".localized)'),
    # Sheets
    ('Text("Select Coin")', 'Text("spot_select_coin".localized)'),
    ('Text("Amount (USDT)")', 'Text("spot_amount_usdt".localized)'),
    ('TextField("Enter amount",', 'TextField("spot_enter_amount".localized,'),
    ('Text("Select Portfolio")', 'Text("spot_select_portfolio".localized)'),
    ('Text("Additional Investment (optional)")', 'Text("spot_additional_investment".localized)'),
    ('Text("Rebalance Portfolio")', 'Text("spot_rebalance_portfolio".localized)'),
    # Cancel
    ('Text("Cancel")', 'Text("btn_cancel".localized)'),
    ('Button("Cancel", role: .cancel)', 'Button("btn_cancel".localized, role: .cancel)'),
]

ALERTS_REPLACEMENTS = [
    # Navigation
    ('.navigationTitle("Price Alerts")', '.navigationTitle("alert_title".localized)'),
    ('.confirmationDialog("Delete Alert?",', '.confirmationDialog("alert_delete_confirm".localized,'),
    ('Button("Delete", role: .destructive)', 'Button("btn_delete".localized, role: .destructive)'),
    ('Button("Cancel", role: .cancel)', 'Button("btn_cancel".localized, role: .cancel)'),
    # Empty state
    ('Text("No Price Alerts")', 'Text("alert_empty_title".localized)'),
    ('Text("Create alerts to get notified when\\nprices reach your targets")', 'Text("alert_empty_desc".localized)'),
    ('Text("Create Alert")', 'Text("alert_create".localized)'),
    # Alert card labels
    ('Text("Target")', 'Text("alert_target".localized)'),
    ('Text("Current")', 'Text("alert_current".localized)'),
    ('Text("Distance")', 'Text("alert_distance".localized)'),
    ('Text("Edit")', 'Text("btn_edit".localized)'),
    ('Text("Delete")', 'Text("btn_delete".localized)'),
    # Create/Edit alert sheet
    ('Text("Symbol")', 'Text("alert_symbol".localized)'),
    ('Text("Condition")', 'Text("alert_condition".localized)'),
    ('Text("Target Price")', 'Text("alert_target_price".localized)'),
    ('Text("Note (optional)")', 'Text("alert_note".localized)'),
    ('TextField("Add a note...",', 'TextField("alert_add_note".localized,'),
    ('Text("Push Notification")', 'Text("alert_push_notif".localized)'),
    ('Text("Sound")', 'Text("alert_sound".localized)'),
    ('Text("Repeat Alert")', 'Text("alert_repeat".localized)'),
    ('Text("Edit Alert")', 'Text("alert_edit_title".localized)'),
    ('Text("New Alert")', 'Text("alert_new_title".localized)'),
    ('Text("Save")', 'Text("btn_save".localized)'),
    ('Text("Cancel")', 'Text("btn_cancel".localized)'),
    # Search
    ('TextField("Search symbol",', 'TextField("alert_search_symbol".localized,'),
    ('Text("Select Symbol")', 'Text("alert_select_symbol".localized)'),
]

SUB_SETTINGS_REPLACEMENTS = [
    # Exchange settings
    ('Text("Demo & Real accounts")', 'Text("exchange_bybit_desc".localized)'),
    ('Text("Testnet & Mainnet")', 'Text("exchange_hl_desc".localized)'),
    # The ternary inline is tricky, handle with regex later
    ('Text("Select Exchange")', 'Text("exchange_select".localized)'),
    ('.navigationTitle("Exchange")', '.navigationTitle("exchange_title".localized)'),
    # Leverage
    ('Text("Default Leverage")', 'Text("leverage_default".localized)'),
    ('Text("Higher leverage increases risk of liquidation")', 'Text("leverage_warning".localized)'),
    ('.navigationTitle("Leverage")', '.navigationTitle("leverage_title".localized)'),
    # Risk Management
    ('Text("Entry %")', 'Text("risk_entry_pct".localized)'),
    ('Text("Take Profit %")', 'Text("risk_tp_pct".localized)'),
    ('Text("Stop Loss %")', 'Text("risk_sl_pct".localized)'),
    ('Text("Position Sizing")', 'Text("risk_position_sizing".localized)'),
    ('Text("Use ATR for SL/TP")', 'Text("risk_use_atr".localized)'),
    ('Text("Enable DCA")', 'Text("risk_enable_dca".localized)'),
    ('Text("Advanced")', 'Text("risk_advanced".localized)'),
    ('Text("ATR adjusts SL/TP based on market volatility. DCA adds to positions at drawdown levels.")', 'Text("risk_advanced_footer".localized)'),
    ('Text("Save Settings")', 'Text("btn_save_settings".localized)'),
    ('.navigationTitle("Risk Management")', '.navigationTitle("risk_title".localized)'),
    # About
    ('Text("Professional Trading Platform")', 'Text("about_subtitle".localized)'),
    ('Text("Version")', 'Text("about_version".localized)'),
    ('Text("Website")', 'Text("about_website".localized)'),
    ('Text("Support")', 'Text("about_support".localized)'),
    ('Text("Telegram")', 'Text("about_telegram".localized)'),
    ('Text("© 2026 Enliko. All rights reserved.")', 'Text("about_copyright".localized)'),
    ('.navigationTitle("About")', '.navigationTitle("about_title".localized)'),
    # API Keys
    ('Text("Demo Account")', 'Text("apikey_demo_account".localized)'),
    ('Text("Practice trading with testnet")', 'Text("apikey_demo_subtitle".localized)'),
    ('Text("Real Account")', 'Text("apikey_real_account".localized)'),
    ('Text("Live trading with real funds")', 'Text("apikey_real_subtitle".localized)'),
    ('Text("Testnet")', 'Text("apikey_testnet".localized)'),
    ('Text("Practice with test funds")', 'Text("apikey_testnet_subtitle".localized)'),
    ('Text("Mainnet")', 'Text("apikey_mainnet".localized)'),
    ('Text("Real funds trading")', 'Text("apikey_mainnet_subtitle".localized)'),
    ('TextField("API Key",', 'TextField("apikey_key_placeholder".localized,'),
    ('TextField("API Secret",', 'TextField("apikey_secret_placeholder".localized,'),
    ('TextField("Private Key (0x...)",', 'TextField("apikey_private_key_placeholder".localized,'),
    ('Text("API Wallet:")', 'Text("apikey_api_wallet".localized)'),
    ('Text("Main Wallet:")', 'Text("apikey_main_wallet".localized)'),
    ('Text("Balance:")', 'Text("apikey_balance".localized)'),
    # Common
    ('Text("Cancel")', 'Text("btn_cancel".localized)'),
    ('Button("Cancel", role: .cancel)', 'Button("btn_cancel".localized, role: .cancel)'),
]


FILES = {
    f"{BASE}/Views/Trading/PositionDetailView.swift": POSITION_DETAIL_REPLACEMENTS,
    f"{BASE}/Views/Exchange/HyperLiquidView.swift": HYPERLIQUID_REPLACEMENTS,
    f"{BASE}/Views/Trading/SpotTradingView.swift": SPOT_TRADING_REPLACEMENTS,
    f"{BASE}/Views/Alerts/AlertsView.swift": ALERTS_REPLACEMENTS,
    f"{BASE}/Views/Settings/SubSettingsViews.swift": SUB_SETTINGS_REPLACEMENTS,
}


def apply_replacements(filepath, replacements):
    if not os.path.exists(filepath):
        print(f"SKIP: {filepath} not found")
        return 0
    
    with open(filepath, "r") as f:
        content = f.read()
    
    original = content
    count = 0
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1
    
    if content != original:
        with open(filepath, "w") as f:
            f.write(content)
        print(f"OK: {os.path.basename(filepath)} — {count} replacements applied")
    else:
        print(f"NO CHANGES: {os.path.basename(filepath)}")
    
    return count


def handle_enum_raw_values():
    """
    Handle enum rawValues that need computed displayName properties.
    HLTab, AlertTab, AlertCondition use rawValue as display text.
    We add a displayName computed property.
    """
    # AlertsView.swift - AlertCondition enum
    alerts_file = f"{BASE}/Views/Alerts/AlertsView.swift"
    if os.path.exists(alerts_file):
        with open(alerts_file, "r") as f:
            content = f.read()
        
        # Add displayName to AlertCondition enum
        old_condition = '''    enum AlertCondition: String, CaseIterable {
        case above = "Price Above"
        case below = "Price Below"
        case crossUp = "Cross Up"
        case crossDown = "Cross Down"
        case percentUp = "% Change Up"
        case percentDown = "% Change Down"'''
        
        new_condition = '''    enum AlertCondition: String, CaseIterable {
        case above = "Price Above"
        case below = "Price Below"
        case crossUp = "Cross Up"
        case crossDown = "Cross Down"
        case percentUp = "% Change Up"
        case percentDown = "% Change Down"
        
        var displayName: String {
            switch self {
            case .above: return "alert_cond_above".localized
            case .below: return "alert_cond_below".localized
            case .crossUp: return "alert_cond_cross_up".localized
            case .crossDown: return "alert_cond_cross_down".localized
            case .percentUp: return "alert_cond_pct_up".localized
            case .percentDown: return "alert_cond_pct_down".localized
            }
        }'''
        
        if old_condition in content:
            content = content.replace(old_condition, new_condition)
            # Replace .rawValue usage for conditions
            content = content.replace('.condition.rawValue', '.condition.displayName')
            print("OK: AlertCondition.displayName added")
        
        # Add displayName to AlertTab enum
        old_tab = '''    enum AlertTab: String, CaseIterable {
        case active = "Active"
        case triggered = "Triggered"
        case all = "All"
    }'''
        
        new_tab = '''    enum AlertTab: String, CaseIterable {
        case active = "Active"
        case triggered = "Triggered"
        case all = "All"
        
        var displayName: String {
            switch self {
            case .active: return "alert_tab_active".localized
            case .triggered: return "alert_tab_triggered".localized
            case .all: return "alert_tab_all".localized
            }
        }
    }'''
        
        if old_tab in content:
            content = content.replace(old_tab, new_tab)
            # Replace .rawValue usage for tabs
            content = content.replace('tab.rawValue', 'tab.displayName')
            print("OK: AlertTab.displayName added")
        
        with open(alerts_file, "w") as f:
            f.write(content)
    
    # HyperLiquidView.swift - HLTab enum  
    hl_file = f"{BASE}/Views/Exchange/HyperLiquidView.swift"
    if os.path.exists(hl_file):
        with open(hl_file, "r") as f:
            content = f.read()
        
        old_hl_tab = '''    enum HLTab: String, CaseIterable {
        case overview = "Overview"
        case vaults = "Vaults"
        case transfers = "Transfers"
        case points = "Points"
    }'''
        
        new_hl_tab = '''    enum HLTab: String, CaseIterable {
        case overview = "Overview"
        case vaults = "Vaults"
        case transfers = "Transfers"
        case points = "Points"
        
        var displayName: String {
            switch self {
            case .overview: return "hl_tab_overview".localized
            case .vaults: return "hl_tab_vaults".localized
            case .transfers: return "hl_tab_transfers".localized
            case .points: return "hl_tab_points".localized
            }
        }
    }'''
        
        if old_hl_tab in content:
            content = content.replace(old_hl_tab, new_hl_tab)
            # Replace .rawValue for HLTab
            content = content.replace('tab.rawValue', 'tab.displayName')
            print("OK: HLTab.displayName added")
        
        with open(hl_file, "w") as f:
            f.write(content)
    
    # HyperLiquidView.swift - TransferType enum
    if os.path.exists(hl_file):
        with open(hl_file, "r") as f:
            content = f.read()
        
        old_tt = '''    enum TransferType: String {
        case deposit = "Deposit"
        case withdraw = "Withdraw"
        case spotToPerp = "Spot → Perp"
        case perpToSpot = "Perp → Spot"
    }'''
        
        new_tt = '''    enum TransferType: String {
        case deposit = "Deposit"
        case withdraw = "Withdraw"
        case spotToPerp = "Spot → Perp"
        case perpToSpot = "Perp → Spot"
        
        var displayName: String {
            switch self {
            case .deposit: return "hl_deposit".localized
            case .withdraw: return "hl_withdraw".localized
            case .spotToPerp: return "Spot → Perp"
            case .perpToSpot: return "Perp → Spot"
            }
        }
    }'''
        
        if old_tt in content:
            content = content.replace(old_tt, new_tt)
            content = content.replace('.type.rawValue', '.type.displayName')
            print("OK: TransferType.displayName added")
        
        with open(hl_file, "w") as f:
            f.write(content)


def handle_exchange_ternary():
    """Handle the ternary expression for exchange description in SubSettingsViews."""
    file = f"{BASE}/Views/Settings/SubSettingsViews.swift"
    if not os.path.exists(file):
        return
    
    with open(file, "r") as f:
        content = f.read()
    
    old = 'Text(exchange == .bybit ? "Demo & Real accounts" : "Testnet & Mainnet")'
    new = 'Text(exchange == .bybit ? "exchange_bybit_desc".localized : "exchange_hl_desc".localized)'
    
    if old in content:
        content = content.replace(old, new)
        with open(file, "w") as f:
            f.write(content)
        print("OK: Exchange ternary localized")


def main():
    total = 0
    
    # 1. Apply simple replacements
    for filepath, replacements in FILES.items():
        total += apply_replacements(filepath, replacements)
    
    # 2. Handle enum rawValues
    handle_enum_raw_values()
    
    # 3. Handle special cases
    handle_exchange_ternary()
    
    print(f"\nTotal: {total} replacements across {len(FILES)} files")


if __name__ == "__main__":
    main()
