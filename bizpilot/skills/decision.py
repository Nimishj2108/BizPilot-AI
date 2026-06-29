from typing import List, Dict, Any

class DecisionSupportSkill:
    """
    Skill to prioritize issues, map them to recommended actions, and evaluate options.
    """
    
    @staticmethod
    def evaluate_and_recommend(risks: List[str], opportunities: List[str]) -> List[Dict[str, Any]]:
        """
        Translates risks and opportunities into concrete prioritized recommendations.
        """
        recommendations = []
        
        # Parse risks first (usually higher urgency/priority)
        for risk in risks:
            risk_lower = risk.lower()
            if "payment" in risk_lower or "failure rate" in risk_lower:
                recommendations.append({
                    "action": "Improve payment system",
                    "priority": "High",
                    "reason": "Address transaction failures and checkout dropouts causing revenue loss.",
                    "impact": "High",
                    "effort": "Medium",
                    "category": "Engineering"
                })
            elif "performance" in risk_lower or "slow" in risk_lower:
                recommendations.append({
                    "action": "Optimize database and server response times",
                    "priority": "Medium",
                    "reason": "Address customer complaints regarding application slowness or lag.",
                    "impact": "High",
                    "effort": "High",
                    "category": "Engineering"
                })
            elif "support" in risk_lower or "contact" in risk_lower:
                recommendations.append({
                    "action": "Set up customer support ticketing queue",
                    "priority": "Medium",
                    "reason": "Improve response times and client communication channels.",
                    "impact": "Medium",
                    "effort": "Low",
                    "category": "Operations"
                })
            else:
                # General risk recommendation
                recommendations.append({
                    "action": f"Mitigate operational risk: {risk.split(':')[0]}",
                    "priority": "Medium",
                    "reason": risk,
                    "impact": "Medium",
                    "effort": "Medium",
                    "category": "Operations"
                })
                
        # Parse opportunities
        for opportunity in opportunities:
            opp_lower = opportunity.lower()
            if "goodwill" in opp_lower or "positive" in opp_lower:
                recommendations.append({
                    "action": "Launch customer referral program",
                    "priority": "Low",
                    "reason": "Leverage existing high customer satisfaction for brand growth.",
                    "impact": "Medium",
                    "effort": "Low",
                    "category": "Marketing"
                })
            elif "aov" in opp_lower or "average order size" in opp_lower:
                recommendations.append({
                    "action": "Implement product cross-selling / bundle discounts",
                    "priority": "Medium",
                    "reason": "Capitalize on healthy average order sizes to boost revenue.",
                    "impact": "Medium",
                    "effort": "Medium",
                    "category": "Product"
                })
            elif "ui/ux" in opp_lower or "reliability" in opp_lower:
                recommendations.append({
                    "action": "Contact affected customer cohort",
                    "priority": "High",
                    "reason": "Proactively reach out to customers who suffered checkout failures to offer discount codes and re-engage them.",
                    "impact": "High",
                    "effort": "Low",
                    "category": "Support"
                })
                
        # Ensure we have at least one High priority recommendation
        if not recommendations:
            recommendations.append({
                "action": "Conduct deep dive operational audit",
                "priority": "Medium",
                "reason": "Set up baseline KPIs and monitor feedback trends.",
                "impact": "Medium",
                "effort": "Low",
                "category": "Management"
            })
            
        # Ensure distinct recommendations (deduplicate by action)
        seen_actions = set()
        unique_recs = []
        for rec in recommendations:
            if rec["action"] not in seen_actions:
                seen_actions.add(rec["action"])
                unique_recs.append(rec)
                
        # Sort so High priority is first
        priority_map = {"High": 0, "Medium": 1, "Low": 2}
        unique_recs.sort(key=lambda x: priority_map.get(x["priority"], 3))
        
        return unique_recs
