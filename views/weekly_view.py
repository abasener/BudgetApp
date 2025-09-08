"""
Weekly View - Bi-weekly budget tracking
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt


class WeeklyView(QWidget):
    def __init__(self, transaction_manager=None, paycheck_processor=None):
        super().__init__()
        self.transaction_manager = transaction_manager
        self.paycheck_processor = paycheck_processor
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Weekly - Bi-weekly Budget Tracker")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Current pay period section
        current_period_frame = QFrame()
        current_period_frame.setFrameStyle(QFrame.Shape.Box)
        current_layout = QVBoxLayout()
        
        current_title = QLabel("Current Pay Period")
        current_title.setStyleSheet("font-weight: bold;")
        current_layout.addWidget(current_title)
        
        # Placeholder for current period data
        placeholder_current = QLabel("Current bi-weekly period info:\n- Start/End dates\n- Original income\n- Bills deducted\n- Automatic savings")
        placeholder_current.setStyleSheet("color: gray; padding: 20px;")
        current_layout.addWidget(placeholder_current)
        
        current_period_frame.setLayout(current_layout)
        layout.addWidget(current_period_frame)
        
        # Week breakdown section
        weeks_frame = QFrame()
        weeks_frame.setFrameStyle(QFrame.Shape.Box)
        weeks_layout = QHBoxLayout()
        
        # Week 1
        week1_layout = QVBoxLayout()
        week1_title = QLabel("Week 1")
        week1_title.setStyleSheet("font-weight: bold;")
        week1_layout.addWidget(week1_title)
        
        week1_placeholder = QLabel("Week 1 tracking:\n- Allocated amount\n- Spent so far\n- Remaining")
        week1_placeholder.setStyleSheet("color: gray; padding: 15px;")
        week1_layout.addWidget(week1_placeholder)
        
        weeks_layout.addLayout(week1_layout)
        
        # Week 2
        week2_layout = QVBoxLayout()
        week2_title = QLabel("Week 2") 
        week2_title.setStyleSheet("font-weight: bold;")
        week2_layout.addWidget(week2_title)
        
        week2_placeholder = QLabel("Week 2 tracking:\n- Allocated amount\n- Rollover from Week 1\n- Spent so far\n- Remaining")
        week2_placeholder.setStyleSheet("color: gray; padding: 15px;")
        week2_layout.addWidget(week2_placeholder)
        
        weeks_layout.addLayout(week2_layout)
        
        weeks_frame.setLayout(weeks_layout)
        layout.addWidget(weeks_frame)
        
        # Rollover section
        rollover_frame = QFrame()
        rollover_frame.setFrameStyle(QFrame.Shape.Box)
        rollover_layout = QVBoxLayout()
        
        rollover_title = QLabel("End of Period Rollover")
        rollover_title.setStyleSheet("font-weight: bold;")
        rollover_layout.addWidget(rollover_title)
        
        rollover_placeholder = QLabel("Surplus/deficit handling:\n- Amount to rollover\n- Target savings account\n- Rollover history")
        rollover_placeholder.setStyleSheet("color: gray; padding: 20px;")
        rollover_layout.addWidget(rollover_placeholder)
        
        rollover_frame.setLayout(rollover_layout)
        layout.addWidget(rollover_frame)
        
        self.setLayout(layout)
        
    def refresh(self):
        """Refresh weekly data"""
        print("Refreshing weekly view...")  # Placeholder