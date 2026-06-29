from typing import Dict, Any, List

class ExecutiveSummarySkill:
    """
    Skill to synthesize quantitative and qualitative analysis into executive-ready summaries and recommendations.
    """
    
    @staticmethod
    def generate_summary(kpis: Dict[str, Any], trends: Dict[str, Any], feedback_summary: Dict[str, Any]) -> str:
        """
        Creates a structured summary string explaining performance and customer feedback.
        """
        revenue = kpis.get("successful_revenue", 0.0)
        transactions = kpis.get("total_transactions", 0)
        aov = kpis.get("average_order_value", 0.0)
        trend = trends.get("trend", "Stable")
        satisfaction = feedback_summary.get("satisfaction_score_pct", 0.0)
        negatives = feedback_summary.get("sentiment_summary", {}).get("Negative", 0)
        positives = feedback_summary.get("sentiment_summary", {}).get("Positive", 0)
        
        summary = (
            f"Business Overview:\n"
            f"- Successful Revenue generated: ${revenue:,.2f} over {transactions} transactions.\n"
            f"- Average Order Value: ${aov:,.2f}.\n"
            f"- Sales Trend: The business sales trend is currently '{trend}'.\n"
            f"- Customer Satisfaction: {satisfaction}% based on feedback analysis ({positives} Positive, {negatives} Negative sentiment comments).\n"
        )
        return summary

    @staticmethod
    def identify_risks_and_opportunities(kpis: Dict[str, Any], feedback_summary: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Generates lists of risks and opportunities based on KPI status, customer comments, and anomalies.
        """
        risks = []
        opportunities = []
        
        # Check transaction failures
        failed_count = kpis.get("status_breakdown", {}).get("Failed", 0)
        total_tx = kpis.get("total_transactions", 1)
        failure_rate = (failed_count / max(1, total_tx)) * 100
        
        if failure_rate > 5:
            risks.append(f"High transaction failure rate: {round(failure_rate, 1)}% of sales attempts failed.")
        
        # Check negative sentiment topics
        topic_counts = feedback_summary.get("topic_summary", {})
        payment_issues = topic_counts.get("Payment & Billing", 0)
        perf_issues = topic_counts.get("Performance & Reliability", 0)
        
        if payment_issues > 0:
            risks.append(f"Payment gateway issues: {payment_issues} customers reported payment/checkout issues.")
        if perf_issues > 0:
            risks.append(f"Application performance issues: {perf_issues} customers flagged slowness or crashes.")

        # Find opportunities
        satisfaction = feedback_summary.get("satisfaction_score_pct", 100.0)
        if satisfaction >= 70:
            opportunities.append("High customer goodwill: leverage positive sentiment for testimonials or referral campaigns.")
        else:
            opportunities.append("Immediate UI/UX optimization: improving check-out reliability will quickly recover lost revenue.")
            
        aov = kpis.get("average_order_value", 0.0)
        if aov > 50:
            opportunities.append(f"Healthy average order size (${aov}): upsell and cross-sell options could expand margins further.")
            
        # Specific anomalies
        for anomaly in anomalies:
            if anomaly["type"] == "Failed Transaction" and "payment system" not in [r.lower() for r in risks]:
                risks.append(f"Failed transaction anomaly spotted: Order {anomaly['order_id']} failed.")
                
        # If empty
        if not risks:
            risks.append("No immediate critical risks identified. Operations are stable.")
        if not opportunities:
            opportunities.append("Expand product range or launch targeted marketing campaigns to increase transaction volume.")
            
        return {
            "risks": risks,
            "opportunities": opportunities
        }
