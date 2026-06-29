import re
from typing import List, Dict, Any

class CustomerFeedbackSkill:
    """
    Skill to run sentiment analysis, topic extraction, and priority scoring on customer comments.
    """
    
    POSITIVE_WORDS = {
        "good", "great", "excellent", "love", "awesome", "happy", "best", "perfect",
        "satisfied", "smooth", "easy", "helpful", "nice", "wonderful", "thanks", "thank"
    }
    
    NEGATIVE_WORDS = {
        "bad", "terrible", "worst", "fail", "failed", "failure", "broken", "issue", "error",
        "problem", "slow", "slowly", "bug", "crash", "annoying", "hate", "useless", "disappointed",
        "unable", "charge", "lost", "poor", "difficult", "waste", "expensive", "unreliable", "declined", "decline"
    }

    TOPIC_KEYWORDS = {
        "Payment & Billing": ["pay", "payment", "card", "checkout", "charge", "billing", "gateway", "stripe", "transaction", "price"],
        "Performance & Reliability": ["slow", "lag", "crash", "freeze", "load", "down", "offline", "bug", "speed"],
        "Customer Support": ["support", "help", "contact", "reply", "response", "agent", "ticket", "email"],
        "Product & Features": ["feature", "ui", "button", "design", "navigation", "layout", "search", "filter", "option"]
    }

    @classmethod
    def analyze_comment(cls, comment: str) -> Dict[str, Any]:
        """
        Analyzes a single customer comment.
        Returns: sentiment, score, detected topics, priority.
        """
        # Clean text
        text = str(comment).lower()
        words = re.findall(r"\b[a-z']+\b", text)
        
        # 1. Sentiment analysis
        pos_count = sum(1 for w in words if w in cls.POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in cls.NEGATIVE_WORDS)
        
        sentiment_score = pos_count - neg_count
        if sentiment_score > 0:
            sentiment = "Positive"
        elif sentiment_score < 0:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
            
        # 2. Topic extraction
        topics = []
        for topic, keywords in cls.TOPIC_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                topics.append(topic)
        if not topics:
            topics.append("General Feedback")

        # 3. Priority scoring (1 to 5)
        # Default priority: 2 for positive, 3 for neutral, 4 for negative
        priority = 3
        if sentiment == "Positive":
            priority = 2
        elif sentiment == "Negative":
            priority = 4
            
        # Increase priority if urgent words are detected
        urgent_keywords = ["fail", "error", "charge", "money", "worst", "broken", "lost", "immediate", "urgent"]
        if any(ukw in text for ukw in urgent_keywords):
            priority = max(priority, 5 if sentiment == "Negative" else 4)
            
        return {
            "comment": comment,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "topics": topics,
            "priority": priority
        }

    @classmethod
    def analyze_feedback_batch(cls, feedback_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes a list of feedback objects.
        Expected keys in each dict: 'Feedback' or 'Comment' or 'Text'.
        """
        results = []
        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        topic_counts = {}
        total_priority = 0
        high_priority_issues = []
        
        for row in feedback_list:
            # Find comment text key
            comment_text = row.get("Feedback", row.get("Comment", row.get("Text", "")))
            if not comment_text:
                continue
                
            analysis = cls.analyze_comment(comment_text)
            results.append(analysis)
            
            # Aggregate
            sent = analysis["sentiment"]
            sentiment_counts[sent] += 1
            total_priority += analysis["priority"]
            
            for t in analysis["topics"]:
                topic_counts[t] = topic_counts.get(t, 0) + 1
                
            # If negative and high priority (5), keep track as major issues
            if analysis["priority"] >= 5:
                high_priority_issues.append({
                    "comment": comment_text,
                    "topics": analysis["topics"],
                    "priority": analysis["priority"]
                })
                
        count = max(1, len(results))
        avg_priority = round(total_priority / count, 2)
        
        # Calculate overall satisfaction score (Positive percentage)
        satisfaction_score = round((sentiment_counts["Positive"] / count) * 100, 1)

        return {
            "individual_analyses": results,
            "sentiment_summary": sentiment_counts,
            "topic_summary": topic_counts,
            "average_priority": avg_priority,
            "satisfaction_score_pct": satisfaction_score,
            "high_priority_issues": high_priority_issues,
            "total_analyzed": len(results)
        }
