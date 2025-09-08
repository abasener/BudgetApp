"""
Dashboard View - Account overview and spending analytics
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QCheckBox, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt


class DashboardView(QWidget):
    def __init__(self, transaction_manager=None, analytics_engine=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        self.analytics_engine = analytics_engine
        
        # Analytics toggle
        self.include_analytics_only = True
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Dashboard - Account Overview & Analytics")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title)
        
        # Analytics toggle
        toggle_layout = QHBoxLayout()
        self.analytics_toggle = QCheckBox("Show Normal Spending Only (Filter Abnormal Transactions)")
        self.analytics_toggle.setChecked(True)
        self.analytics_toggle.toggled.connect(self.toggle_analytics_mode)
        toggle_layout.addWidget(self.analytics_toggle)
        toggle_layout.addStretch()
        main_layout.addLayout(toggle_layout)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        
        # Account balances section
        self.accounts_frame = QFrame()
        self.accounts_frame.setFrameStyle(QFrame.Shape.Box)
        self.accounts_layout = QVBoxLayout()
        
        accounts_title = QLabel("Account Balances")
        accounts_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.accounts_layout.addWidget(accounts_title)
        
        self.accounts_content = QLabel("Loading account data...")
        self.accounts_content.setStyleSheet("padding: 10px;")
        self.accounts_layout.addWidget(self.accounts_content)
        
        self.accounts_frame.setLayout(self.accounts_layout)
        layout.addWidget(self.accounts_frame)
        
        # Financial Summary section
        self.summary_frame = QFrame()
        self.summary_frame.setFrameStyle(QFrame.Shape.Box)
        self.summary_layout = QVBoxLayout()
        
        summary_title = QLabel("Financial Summary")
        summary_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.summary_layout.addWidget(summary_title)
        
        self.summary_content = QLabel("Loading summary data...")
        self.summary_content.setStyleSheet("padding: 10px;")
        self.summary_layout.addWidget(self.summary_content)
        
        self.summary_frame.setLayout(self.summary_layout)
        layout.addWidget(self.summary_frame)
        
        # Analytics section
        self.analytics_frame = QFrame()
        self.analytics_frame.setFrameStyle(QFrame.Shape.Box)
        self.analytics_layout = QVBoxLayout()
        
        analytics_title = QLabel("Spending Analytics")
        analytics_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.analytics_layout.addWidget(analytics_title)
        
        self.analytics_content = QLabel("Loading analytics data...")
        self.analytics_content.setStyleSheet("padding: 10px;")
        self.analytics_layout.addWidget(self.analytics_content)
        
        self.analytics_frame.setLayout(self.analytics_layout)
        layout.addWidget(self.analytics_frame)
        
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
        
    def toggle_analytics_mode(self, checked):
        """Toggle between normal and all spending analytics"""
        self.include_analytics_only = checked
        self.refresh()
    
    def refresh(self):
        """Refresh dashboard data"""
        if not self.transaction_manager or not self.analytics_engine:
            self.accounts_content.setText("Services not available")
            self.summary_content.setText("Services not available") 
            self.analytics_content.setText("Services not available")
            return
        
        try:
            # Update accounts
            self.update_accounts_display()
            
            # Update financial summary
            self.update_summary_display()
            
            # Update analytics
            self.update_analytics_display()
            
        except Exception as e:
            error_msg = f"Error refreshing dashboard: {str(e)}"
            print(error_msg)
            self.accounts_content.setText(error_msg)
            self.summary_content.setText(error_msg)
            self.analytics_content.setText(error_msg)
    
    def update_accounts_display(self):
        """Update account balances display with goal progress"""
        accounts = self.transaction_manager.get_all_accounts()
        
        if not accounts:
            self.accounts_content.setText("No accounts found")
            return
        
        account_text = ""
        total_balance = 0
        
        for account in accounts:
            default_marker = " (Default Savings)" if account.is_default_save else ""
            account_text += f"{account.name}: ${account.running_total:.2f}{default_marker}\n"
            
            # Show goal progress if account has a goal
            if account.goal_amount > 0:
                progress_percent = account.goal_progress_percent
                remaining = account.goal_remaining
                
                progress_bar = "=" * int(progress_percent / 5)  # 20 chars max
                progress_bar = progress_bar.ljust(20, "-")
                
                account_text += f"  Goal: ${account.goal_amount:.2f} [{progress_bar}] {progress_percent:.1f}%\n"
                if remaining > 0:
                    account_text += f"  Remaining: ${remaining:.2f}\n"
                else:
                    account_text += f"  ✓ Goal achieved! (${-remaining:.2f} over)\n"
            
            account_text += "\n"
            total_balance += account.running_total
        
        account_text += f"Total Balance: ${total_balance:.2f}"
        self.accounts_content.setText(account_text)
    
    def update_summary_display(self):
        """Update financial summary display"""
        summary = self.transaction_manager.get_income_vs_spending_summary()
        
        mode_text = "Normal Spending Only" if self.include_analytics_only else "All Spending"
        
        summary_text = f"Analytics Mode: {mode_text}\n\n"
        summary_text += f"Total Income: ${summary.get('total_income', 0):.2f}\n"
        summary_text += f"Total Spending: ${summary.get('total_spending', 0):.2f}\n"
        summary_text += f"Total Bills: ${summary.get('total_bills', 0):.2f}\n"
        summary_text += f"Total Savings: ${summary.get('total_savings', 0):.2f}\n"
        summary_text += f"Net Difference: ${summary.get('net_difference', 0):.2f}"
        
        if summary.get('net_difference', 0) > 0:
            summary_text += " (Surplus)"
        elif summary.get('net_difference', 0) < 0:
            summary_text += " (Deficit)"
        
        self.summary_content.setText(summary_text)
    
    def update_analytics_display(self):
        """Update analytics display"""
        # Get spending statistics
        stats = self.analytics_engine.get_spending_statistics(self.include_analytics_only)
        
        # Get day of week analysis
        day_spending = self.analytics_engine.analyze_spending_by_day_of_week(self.include_analytics_only)
        highest_day = max(day_spending, key=day_spending.get) if day_spending else "N/A"
        
        # Get category analysis  
        category_spending = self.analytics_engine.analyze_spending_by_category(self.include_analytics_only)
        top_category = max(category_spending, key=category_spending.get) if category_spending else "N/A"
        
        mode_text = "Normal Spending Only" if self.include_analytics_only else "All Spending"
        
        analytics_text = f"Mode: {mode_text}\n\n"
        analytics_text += f"Transaction Count: {stats.get('count', 0)}\n"
        analytics_text += f"Total Spending: ${stats.get('total', 0):.2f}\n"
        analytics_text += f"Average Transaction: ${stats.get('average', 0):.2f}\n"
        analytics_text += f"Largest Transaction: ${stats.get('max', 0):.2f}\n\n"
        
        analytics_text += f"Highest Spending Day: {highest_day}\n"
        if highest_day in day_spending:
            analytics_text += f"  Amount: ${day_spending[highest_day]:.2f}\n"
        
        analytics_text += f"Top Spending Category: {top_category}\n"
        if top_category in category_spending:
            analytics_text += f"  Amount: ${category_spending[top_category]:.2f}"
        
        self.analytics_content.setText(analytics_text)