import math
from typing import List, Dict, Any

class BusinessAnalyticsSkill:
    """
    Skill to compute business KPIs, perform trend analysis, and detect sales anomalies.
    """
    
    @staticmethod
    def calculate_kpis(sales_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates basic KPIs:
        - Total Revenue
        - Total Transactions
        - Average Order Value (AOV)
        - Transaction Status breakdown
        """
        if not sales_data:
            return {
                "total_revenue": 0.0,
                "total_transactions": 0,
                "average_order_value": 0.0,
                "status_breakdown": {}
            }
            
        total_rev = 0.0
        successful_rev = 0.0
        total_tx = len(sales_data)
        status_breakdown = {}
        
        for row in sales_data:
            # Parse amount
            amount_str = str(row.get("Amount", "0")).replace("$", "").replace(",", "").strip()
            try:
                amount = float(amount_str)
            except ValueError:
                amount = 0.0
                
            status = row.get("Status", "Completed").strip()
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
            
            total_rev += amount
            if status.lower() not in ["failed", "refunded", "cancelled"]:
                successful_rev += amount
                
        completed_tx = status_breakdown.get("Completed", 0) + status_breakdown.get("Success", 0)
        aov = successful_rev / max(1, completed_tx)
        
        return {
            "total_revenue": round(total_rev, 2),
            "successful_revenue": round(successful_rev, 2),
            "total_transactions": total_tx,
            "average_order_value": round(aov, 2),
            "status_breakdown": status_breakdown
        }

    @staticmethod
    def analyze_trends(sales_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identifies sales trends over time, e.g., daily or transaction sequence trends.
        """
        if not sales_data:
            return {"trend": "No Data", "percentage_change": 0.0}
            
        # Group by date if available, otherwise use sequence order
        by_date = {}
        for row in sales_data:
            date = row.get("Date", "Unknown").split(" ")[0].split("T")[0]
            amount_str = str(row.get("Amount", "0")).replace("$", "").replace(",", "").strip()
            try:
                amount = float(amount_str)
            except ValueError:
                amount = 0.0
            
            status = row.get("Status", "Completed").lower()
            if status not in ["failed", "refunded", "cancelled"]:
                by_date[date] = by_date.get(date, 0.0) + amount

        # Sort dates
        sorted_dates = sorted(list(by_date.keys()))
        if len(sorted_dates) < 2:
            return {"trend": "Stable (insufficient dates)", "daily_average": round(sum(by_date.values()), 2)}
            
        # Compare first half of dates with second half to find trend direction
        mid = len(sorted_dates) // 2
        first_half = sum(by_date[d] for d in sorted_dates[:mid])
        second_half = sum(by_date[d] for d in sorted_dates[mid:])
        
        diff = second_half - first_half
        denom = max(1.0, first_half)
        pct_change = (diff / denom) * 100
        
        if pct_change > 5:
            trend = "Increasing"
        elif pct_change < -5:
            trend = "Decreasing"
        else:
            trend = "Stable"
            
        return {
            "trend": trend,
            "pct_change_half_over_half": round(pct_change, 2),
            "daily_sales": {d: round(by_date[d], 2) for d in sorted_dates}
        }

    @staticmethod
    def detect_anomalies(sales_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detects anomalies such as failed transactions, unusually high orders, or sudden sales drops.
        """
        anomalies = []
        if not sales_data:
            return anomalies
            
        # 1. Flag failed transactions explicitly
        for i, row in enumerate(sales_data):
            status = str(row.get("Status", "")).strip().lower()
            if status == "failed":
                anomalies.append({
                    "type": "Failed Transaction",
                    "row_index": i,
                    "order_id": row.get("OrderID", "N/A"),
                    "amount": row.get("Amount", "0"),
                    "description": f"Transaction of {row.get('Amount')} failed."
                })
                
        # 2. Check for statistical amount anomalies in successful ones
        successful_amounts = []
        for row in sales_data:
            status = str(row.get("Status", "")).strip().lower()
            if status not in ["failed", "refunded", "cancelled"]:
                try:
                    amt = float(str(row.get("Amount", "0")).replace("$", "").replace(",", "").strip())
                    successful_amounts.append(amt)
                except ValueError:
                    pass
                    
        if len(successful_amounts) > 3:
            mean = sum(successful_amounts) / len(successful_amounts)
            variance = sum((x - mean) ** 2 for x in successful_amounts) / len(successful_amounts)
            std_dev = math.sqrt(variance)
            
            if std_dev > 0:
                for i, row in enumerate(sales_data):
                    status = str(row.get("Status", "")).strip().lower()
                    if status not in ["failed", "refunded", "cancelled"]:
                        try:
                            amt = float(str(row.get("Amount", "0")).replace("$", "").replace(",", "").strip())
                            # Outliers > 2 standard deviations
                            if abs(amt - mean) > 2.5 * std_dev:
                                direction = "High" if amt > mean else "Low"
                                anomalies.append({
                                    "type": f"Statistical Outlier ({direction} Value)",
                                    "row_index": i,
                                    "order_id": row.get("OrderID", "N/A"),
                                    "amount": row.get("Amount", "0"),
                                    "description": f"Transaction amount {row.get('Amount')} is outside normal range (Mean: {round(mean, 2)}, StdDev: {round(std_dev, 2)})"
                                })
                        except ValueError:
                            pass
                            
        return anomalies
