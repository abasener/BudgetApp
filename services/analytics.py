"""
Analytics Engine - Generate charts and spending insights with normal vs all spending toggle
"""

from typing import Dict, List, Tuple, Optional
from datetime import date, datetime, timedelta
from collections import defaultdict
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from models import TransactionType
from services.transaction_manager import TransactionManager


class AnalyticsEngine:
    def __init__(self):
        self.transaction_manager = TransactionManager()
    
    def close(self):
        """Close database connections"""
        self.transaction_manager.close()
    
    # Core data retrieval methods
    def get_spending_data(self, include_analytics_only: bool = True, days_back: int = 90) -> List[Dict]:
        """Get spending transactions as dictionaries for analysis"""
        spending_transactions = self.transaction_manager.get_spending_transactions(include_analytics_only)
        
        # Filter by date range if specified
        if days_back > 0:
            cutoff_date = date.today() - timedelta(days=days_back)
            spending_transactions = [
                t for t in spending_transactions 
                if t.date >= cutoff_date
            ]
        
        # Convert to dictionaries for easier analysis
        data = []
        for tx in spending_transactions:
            data.append({
                'date': tx.date,
                'amount': tx.amount,
                'category': tx.category or 'Uncategorized',
                'description': tx.description or '',
                'week_number': tx.week_number,
                'day_of_week': tx.date.strftime('%A'),
                'include_in_analytics': tx.include_in_analytics
            })
        
        return data
    
    # Day of week analysis (your favorite feature!)
    def analyze_spending_by_day_of_week(self, include_analytics_only: bool = True) -> Dict[str, float]:
        """Analyze which days of the week you spend the most money"""
        spending_data = self.get_spending_data(include_analytics_only)
        
        day_totals = defaultdict(float)
        for transaction in spending_data:
            day_totals[transaction['day_of_week']] += transaction['amount']
        
        # Ensure all days are present and in order
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        result = {day: day_totals.get(day, 0.0) for day in days_order}
        
        return result
    
    def create_day_of_week_chart(self, include_analytics_only: bool = True) -> go.Figure:
        """Create bar chart showing spending by day of week"""
        day_spending = self.analyze_spending_by_day_of_week(include_analytics_only)
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(day_spending.keys()),
                y=list(day_spending.values()),
                marker_color='lightblue',
                text=[f'${v:.0f}' for v in day_spending.values()],
                textposition='auto'
            )
        ])
        
        title_suffix = " (Normal Spending Only)" if include_analytics_only else " (All Spending)"
        fig.update_layout(
            title=f"Spending by Day of Week{title_suffix}",
            xaxis_title="Day of Week",
            yaxis_title="Amount Spent ($)",
            showlegend=False
        )
        
        return fig
    
    # Category analysis
    def analyze_spending_by_category(self, include_analytics_only: bool = True) -> Dict[str, float]:
        """Analyze spending by category"""
        return self.transaction_manager.get_spending_by_category(include_analytics_only)
    
    def create_category_pie_chart(self, include_analytics_only: bool = True) -> go.Figure:
        """Create pie chart showing spending by category"""
        category_spending = self.analyze_spending_by_category(include_analytics_only)
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(category_spending.keys()),
                values=list(category_spending.values()),
                textinfo='label+percent',
                textposition='auto'
            )
        ])
        
        title_suffix = " (Normal Spending Only)" if include_analytics_only else " (All Spending)"
        fig.update_layout(title=f"Spending by Category{title_suffix}")
        
        return fig
    
    def create_category_bar_chart(self, include_analytics_only: bool = True) -> go.Figure:
        """Create horizontal bar chart for category spending"""
        category_spending = self.analyze_spending_by_category(include_analytics_only)
        
        # Sort by amount (descending)
        sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
        categories, amounts = zip(*sorted_categories) if sorted_categories else ([], [])
        
        fig = go.Figure(data=[
            go.Bar(
                x=amounts,
                y=categories,
                orientation='h',
                marker_color='lightgreen',
                text=[f'${v:.0f}' for v in amounts],
                textposition='auto'
            )
        ])
        
        title_suffix = " (Normal Spending Only)" if include_analytics_only else " (All Spending)"
        fig.update_layout(
            title=f"Spending by Category{title_suffix}",
            xaxis_title="Amount Spent ($)",
            yaxis_title="Category",
            showlegend=False
        )
        
        return fig
    
    # Weekly trends
    def analyze_spending_by_week(self, include_analytics_only: bool = True, weeks_back: int = 12) -> Dict[int, float]:
        """Analyze spending trends by week"""
        week_spending = self.transaction_manager.get_spending_by_week(include_analytics_only)
        
        # Filter to recent weeks if specified
        if weeks_back > 0:
            current_week = self.transaction_manager.get_current_week()
            if current_week:
                min_week = max(1, current_week.week_number - weeks_back + 1)
                week_spending = {
                    week: amount for week, amount in week_spending.items() 
                    if week >= min_week
                }
        
        return week_spending
    
    def create_weekly_trend_chart(self, include_analytics_only: bool = True, weeks_back: int = 12) -> go.Figure:
        """Create line chart showing weekly spending trends"""
        week_spending = self.analyze_spending_by_week(include_analytics_only, weeks_back)
        
        # Sort by week number
        sorted_weeks = sorted(week_spending.items())
        weeks, amounts = zip(*sorted_weeks) if sorted_weeks else ([], [])
        
        fig = go.Figure(data=[
            go.Scatter(
                x=weeks,
                y=amounts,
                mode='lines+markers',
                line=dict(color='blue', width=2),
                marker=dict(size=6),
                text=[f'Week {w}: ${a:.0f}' for w, a in zip(weeks, amounts)],
                hovertemplate='Week %{x}<br>Spent: $%{y:.2f}<extra></extra>'
            )
        ])
        
        title_suffix = " (Normal Spending Only)" if include_analytics_only else " (All Spending)"
        fig.update_layout(
            title=f"Weekly Spending Trend{title_suffix}",
            xaxis_title="Week Number",
            yaxis_title="Amount Spent ($)",
            showlegend=False
        )
        
        return fig
    
    # Monthly analysis
    def analyze_spending_by_month(self, include_analytics_only: bool = True) -> Dict[str, float]:
        """Analyze spending by month"""
        spending_data = self.get_spending_data(include_analytics_only, days_back=365)
        
        month_totals = defaultdict(float)
        for transaction in spending_data:
            month_key = transaction['date'].strftime('%Y-%m')
            month_totals[month_key] += transaction['amount']
        
        return dict(month_totals)
    
    def create_monthly_trend_chart(self, include_analytics_only: bool = True) -> go.Figure:
        """Create monthly spending trend chart"""
        month_spending = self.analyze_spending_by_month(include_analytics_only)
        
        # Sort by month
        sorted_months = sorted(month_spending.items())
        months, amounts = zip(*sorted_months) if sorted_months else ([], [])
        
        # Convert to readable month names
        month_labels = [datetime.strptime(month, '%Y-%m').strftime('%b %Y') for month in months]
        
        fig = go.Figure(data=[
            go.Scatter(
                x=month_labels,
                y=amounts,
                mode='lines+markers',
                line=dict(color='purple', width=2),
                marker=dict(size=8),
                fill='tonexty' if len(amounts) > 1 else None,
                hovertemplate='%{x}<br>Spent: $%{y:.2f}<extra></extra>'
            )
        ])
        
        title_suffix = " (Normal Spending Only)" if include_analytics_only else " (All Spending)"
        fig.update_layout(
            title=f"Monthly Spending Trend{title_suffix}",
            xaxis_title="Month",
            yaxis_title="Amount Spent ($)",
            showlegend=False
        )
        
        return fig
    
    # Advanced analytics
    def get_spending_statistics(self, include_analytics_only: bool = True) -> Dict[str, float]:
        """Get statistical summary of spending"""
        spending_data = self.get_spending_data(include_analytics_only)
        amounts = [tx['amount'] for tx in spending_data]
        
        if not amounts:
            return {
                'total': 0, 'average': 0, 'median': 0, 
                'min': 0, 'max': 0, 'count': 0
            }
        
        amounts.sort()
        n = len(amounts)
        median = amounts[n//2] if n % 2 == 1 else (amounts[n//2-1] + amounts[n//2]) / 2
        
        return {
            'total': sum(amounts),
            'average': sum(amounts) / len(amounts),
            'median': median,
            'min': min(amounts),
            'max': max(amounts),
            'count': len(amounts)
        }
    
    def find_spending_patterns(self, include_analytics_only: bool = True) -> Dict[str, any]:
        """Find interesting spending patterns and insights"""
        spending_data = self.get_spending_data(include_analytics_only)
        
        if not spending_data:
            return {"error": "No spending data available"}
        
        # Day of week analysis
        day_spending = self.analyze_spending_by_day_of_week(include_analytics_only)
        highest_spending_day = max(day_spending, key=day_spending.get)
        lowest_spending_day = min(day_spending, key=day_spending.get)
        
        # Category analysis
        category_spending = self.analyze_spending_by_category(include_analytics_only)
        top_category = max(category_spending, key=category_spending.get) if category_spending else "None"
        
        # Transaction frequency
        stats = self.get_spending_statistics(include_analytics_only)
        
        patterns = {
            'highest_spending_day': highest_spending_day,
            'highest_day_amount': day_spending[highest_spending_day],
            'lowest_spending_day': lowest_spending_day,
            'lowest_day_amount': day_spending[lowest_spending_day],
            'top_spending_category': top_category,
            'top_category_amount': category_spending.get(top_category, 0),
            'average_transaction': stats['average'],
            'largest_transaction': stats['max'],
            'total_transactions': stats['count'],
            'total_spending': stats['total']
        }
        
        return patterns
    
    def create_comparison_chart(self) -> go.Figure:
        """Create chart comparing normal vs all spending"""
        normal_stats = self.get_spending_statistics(include_analytics_only=True)
        all_stats = self.get_spending_statistics(include_analytics_only=False)
        
        categories = ['Total Spending', 'Transaction Count', 'Average Transaction']
        normal_values = [normal_stats['total'], normal_stats['count'], normal_stats['average']]
        all_values = [all_stats['total'], all_stats['count'], all_stats['average']]
        
        fig = go.Figure(data=[
            go.Bar(name='Normal Spending Only', x=categories, y=normal_values, marker_color='lightblue'),
            go.Bar(name='All Spending', x=categories, y=all_values, marker_color='lightcoral')
        ])
        
        fig.update_layout(
            title="Normal vs All Spending Comparison",
            xaxis_title="Metrics",
            yaxis_title="Value",
            barmode='group'
        )
        
        return fig
    
    # Dashboard summary
    def generate_dashboard_summary(self, include_analytics_only: bool = True) -> Dict[str, any]:
        """Generate comprehensive dashboard summary"""
        
        try:
            stats = self.get_spending_statistics(include_analytics_only)
            patterns = self.find_spending_patterns(include_analytics_only)
            category_spending = self.analyze_spending_by_category(include_analytics_only)
            
            # Income vs spending summary
            income_vs_spending = self.transaction_manager.get_income_vs_spending_summary()
            
            summary = {
                'spending_stats': stats,
                'spending_patterns': patterns,
                'category_breakdown': category_spending,
                'income_vs_spending': income_vs_spending,
                'analytics_mode': 'Normal Spending Only' if include_analytics_only else 'All Spending',
                'generated_at': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            return {'error': f'Failed to generate dashboard summary: {str(e)}'}