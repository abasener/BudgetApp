"""
Enhanced Bills View - Interactive bill tracking with line plots and management table
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt
from datetime import date, timedelta
from themes import theme_manager
from widgets import LineChartWidget, BarChartWidget


class BillsView(QWidget):
    def __init__(self, transaction_manager=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        
        # Charts
        self.bill_trends_chart = None
        self.payment_frequency_chart = None
        
        # Management table
        self.bills_table = None
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("🧾 Bills Tracker")
        title.setFont(theme_manager.get_font("title"))
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(15)
        
        # Top section - Bill overview cards
        overview_layout = QHBoxLayout()
        overview_layout.setSpacing(15)
        
        # Bill summary card
        self.bill_summary_frame = self.create_info_card("📊 Bill Summary", "bill_summary")
        overview_layout.addWidget(self.bill_summary_frame)
        
        # Savings status card
        self.savings_status_frame = self.create_info_card("💰 Savings Status", "savings_status")
        overview_layout.addWidget(self.savings_status_frame)
        
        # Next payments card
        self.next_payments_frame = self.create_info_card("📅 Upcoming", "next_payments")
        overview_layout.addWidget(self.next_payments_frame)
        
        content_layout.addLayout(overview_layout)
        
        # Charts section
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        # Bill payment trends over time
        self.bill_trends_chart = LineChartWidget("Bill Payment History")
        self.bill_trends_chart.setMinimumHeight(300)
        charts_layout.addWidget(self.bill_trends_chart)
        
        # Payment frequency distribution
        self.payment_frequency_chart = BarChartWidget("Bills by Frequency")
        self.payment_frequency_chart.setMinimumHeight(300)
        charts_layout.addWidget(self.payment_frequency_chart)
        
        content_layout.addLayout(charts_layout)
        
        # Bills management table
        table_frame = QFrame()
        table_frame.setFrameStyle(QFrame.Shape.Box)
        table_layout = QVBoxLayout()
        
        table_title = QLabel("📋 Bills Management")
        table_title.setFont(theme_manager.get_font("subtitle"))
        table_layout.addWidget(table_title)
        
        # Create bills table
        self.create_bills_table()
        table_layout.addWidget(self.bills_table)
        
        table_frame.setLayout(table_layout)
        content_layout.addWidget(table_frame)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
    
    def create_info_card(self, title: str, content_type: str) -> QFrame:
        """Create a styled information card"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setMinimumHeight(120)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(theme_manager.get_font("subtitle"))
        layout.addWidget(title_label)
        
        # Content label
        content_label = QLabel("Loading...")
        content_label.setWordWrap(True)
        layout.addWidget(content_label)
        
        frame.setLayout(layout)
        
        # Store reference for updating
        setattr(self, f"{content_type}_label", content_label)
        
        return frame
    
    def create_bills_table(self):
        """Create the bills management table"""
        self.bills_table = QTableWidget()
        
        # Set up columns
        headers = ["Bill Name", "Type", "Frequency", "Typical Amount", "Bi-weekly Savings", 
                  "Current Saved", "Last Payment", "Status"]
        self.bills_table.setColumnCount(len(headers))
        self.bills_table.setHorizontalHeaderLabels(headers)
        
        # Configure table
        self.bills_table.setAlternatingRowColors(True)
        self.bills_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.bills_table.setSortingEnabled(True)
        
        # Auto-resize columns
        header = self.bills_table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.bills_table.setMinimumHeight(300)
    
    def refresh(self):
        """Refresh all bills data and charts"""
        if not self.transaction_manager:
            self.bill_summary_label.setText("Services not available")
            self.savings_status_label.setText("Services not available")
            self.next_payments_label.setText("Services not available")
            return
        
        try:
            print("Refreshing enhanced bills view...")
            
            # Update info cards
            self.update_bill_summary()
            self.update_savings_status()
            self.update_next_payments()
            
            # Update charts
            self.update_bill_trends_chart()
            self.update_payment_frequency_chart()
            
            # Update table
            self.update_bills_table()
            
            print("Enhanced bills view refreshed successfully!")
            
        except Exception as e:
            error_msg = f"Error refreshing bills: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            
            self.bill_summary_label.setText(error_msg)
            self.savings_status_label.setText(error_msg)
            self.next_payments_label.setText(error_msg)
    
    def update_bill_summary(self):
        """Update bill summary info card"""
        try:
            bills = self.transaction_manager.get_all_bills()
            
            if not bills:
                self.bill_summary_label.setText("No bills configured")
                return
            
            total_bills = len(bills)
            variable_bills = len([b for b in bills if b.is_variable])
            total_typical_amount = sum(b.typical_amount for b in bills)
            total_bi_weekly_savings = sum(b.amount_to_save for b in bills)
            
            summary_text = f"📊 Total Bills: {total_bills}\n"
            summary_text += f"🔄 Variable: {variable_bills}\n"
            summary_text += f"💵 Monthly Cost: ${total_typical_amount * 2.17:.2f}\n"
            summary_text += f"💰 Bi-weekly Savings: ${total_bi_weekly_savings:.2f}"
            
            self.bill_summary_label.setText(summary_text)
            
        except Exception as e:
            self.bill_summary_label.setText(f"Error: {e}")
    
    def update_savings_status(self):
        """Update savings status info card"""
        try:
            bills = self.transaction_manager.get_all_bills()
            
            if not bills:
                self.savings_status_label.setText("No bills to track")
                return
            
            total_saved = sum(b.running_total for b in bills)
            total_needed = sum(b.typical_amount for b in bills)
            
            # Calculate bills that are fully funded
            fully_funded = 0
            under_funded = 0
            
            for bill in bills:
                if bill.running_total >= bill.typical_amount:
                    fully_funded += 1
                else:
                    under_funded += 1
            
            funding_ratio = (total_saved / total_needed * 100) if total_needed > 0 else 0
            
            status_text = f"💰 Total Saved: ${total_saved:,.2f}\n"
            status_text += f"🎯 Funding: {funding_ratio:.1f}%\n"
            status_text += f"✅ Fully Funded: {fully_funded}\n"
            status_text += f"⚠️ Under-funded: {under_funded}"
            
            self.savings_status_label.setText(status_text)
            
        except Exception as e:
            self.savings_status_label.setText(f"Error: {e}")
    
    def update_next_payments(self):
        """Update next payments info card"""
        try:
            bills = self.transaction_manager.get_all_bills()
            
            if not bills:
                self.next_payments_label.setText("No upcoming payments")
                return
            
            # For manual system, show bills with low savings
            urgent_bills = []
            for bill in bills:
                if bill.running_total < bill.typical_amount:
                    shortfall = bill.typical_amount - bill.running_total
                    urgent_bills.append((bill.name, shortfall))
            
            # Sort by shortfall amount (most urgent first)
            urgent_bills.sort(key=lambda x: x[1], reverse=True)
            
            if not urgent_bills:
                payments_text = "🎉 All bills fully funded!"
            else:
                payments_text = "⚠️ Bills needing savings:\n"
                for bill_name, shortfall in urgent_bills[:3]:  # Show top 3
                    payments_text += f"• {bill_name}: ${shortfall:.0f}\n"
                
                if len(urgent_bills) > 3:
                    payments_text += f"... and {len(urgent_bills) - 3} more"
            
            self.next_payments_label.setText(payments_text)
            
        except Exception as e:
            self.next_payments_label.setText(f"Error: {e}")
    
    def update_bill_trends_chart(self):
        """Update bill payment trends line chart"""
        try:
            # Get bill payment transactions
            all_transactions = self.transaction_manager.get_all_transactions()
            bill_payments = [t for t in all_transactions if t.transaction_type == "bill_pay"]
            
            if not bill_payments:
                self.bill_trends_chart.update_data({}, "Date", "Amount ($)")
                return
            
            # Group by bill and create trend data
            trends_data = {}
            bill_history = {}
            
            for transaction in bill_payments[-50:]:  # Last 50 payments
                if hasattr(transaction, 'bill_id') and transaction.bill_id:
                    # Get bill name
                    try:
                        bill = self.transaction_manager.get_bill_by_id(transaction.bill_id)
                        bill_name = bill.name if bill else f"Bill {transaction.bill_id}"
                    except:
                        bill_name = f"Bill {transaction.bill_id}"
                    
                    if bill_name not in bill_history:
                        bill_history[bill_name] = []
                    
                    # Add payment to history
                    bill_history[bill_name].append((transaction.date.strftime("%m/%d"), transaction.amount))
            
            # Convert to chart format (limit to top 5 bills for readability)
            top_bills = sorted(bill_history.keys())[:5]
            for bill_name in top_bills:
                payments = bill_history[bill_name][-10:]  # Last 10 payments
                trends_data[bill_name] = [(i, amount) for i, (date, amount) in enumerate(payments)]
            
            if trends_data:
                self.bill_trends_chart.update_data(trends_data, "Payment #", "Amount ($)")
            else:
                self.bill_trends_chart.update_data({}, "Payment #", "Amount ($)")
                
        except Exception as e:
            print(f"Error updating bill trends: {e}")
    
    def update_payment_frequency_chart(self):
        """Update payment frequency distribution bar chart"""
        try:
            bills = self.transaction_manager.get_all_bills()
            
            if not bills:
                self.payment_frequency_chart.update_data({}, "Frequency", "Count")
                return
            
            # Count bills by frequency
            frequency_count = {}
            for bill in bills:
                freq = bill.payment_frequency or "unknown"
                frequency_count[freq] = frequency_count.get(freq, 0) + 1
            
            self.payment_frequency_chart.update_data(frequency_count, "Frequency", "Number of Bills")
            
        except Exception as e:
            print(f"Error updating frequency chart: {e}")
    
    def update_bills_table(self):
        """Update the bills management table"""
        try:
            bills = self.transaction_manager.get_all_bills()
            
            self.bills_table.setRowCount(len(bills))
            
            for row, bill in enumerate(bills):
                # Bill Name
                self.bills_table.setItem(row, 0, QTableWidgetItem(bill.name))
                
                # Type
                self.bills_table.setItem(row, 1, QTableWidgetItem(bill.bill_type or "N/A"))
                
                # Frequency
                self.bills_table.setItem(row, 2, QTableWidgetItem(bill.payment_frequency or "N/A"))
                
                # Typical Amount
                typical_text = f"${bill.typical_amount:.2f}"
                if bill.is_variable:
                    typical_text += " (var)"
                self.bills_table.setItem(row, 3, QTableWidgetItem(typical_text))
                
                # Bi-weekly Savings
                if bill.amount_to_save < 1.0 and bill.amount_to_save > 0:
                    savings_text = f"{bill.amount_to_save * 100:.1f}%"
                else:
                    savings_text = f"${bill.amount_to_save:.2f}"
                self.bills_table.setItem(row, 4, QTableWidgetItem(savings_text))
                
                # Current Saved
                self.bills_table.setItem(row, 5, QTableWidgetItem(f"${bill.running_total:.2f}"))
                
                # Last Payment
                if bill.last_payment_date:
                    last_payment_text = f"{bill.last_payment_date} (${bill.last_payment_amount:.2f})"
                else:
                    last_payment_text = "Never"
                self.bills_table.setItem(row, 6, QTableWidgetItem(last_payment_text))
                
                # Status
                if bill.running_total >= bill.typical_amount:
                    status_text = "✅ Funded"
                    status_color = theme_manager.get_color('success')
                else:
                    shortfall = bill.typical_amount - bill.running_total
                    status_text = f"⚠️ Need ${shortfall:.0f}"
                    status_color = theme_manager.get_color('warning')
                
                status_item = QTableWidgetItem(status_text)
                self.bills_table.setItem(row, 7, status_item)
            
            # Auto-resize columns
            self.bills_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error updating bills table: {e}")
    
    def on_theme_changed(self, theme_id):
        """Handle theme change for bills view"""
        try:
            # Refresh charts to apply new theme
            self.update_bill_trends_chart()
            self.update_payment_frequency_chart()
            
            # Update table styling
            self.update_bills_table()
        except Exception as e:
            print(f"Error applying theme to bills view: {e}")