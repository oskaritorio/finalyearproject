"""
Simple Sentiment Analysis using keyword matching
NO external dependencies - works immediately
"""

import random
from collections import Counter
from typing import Dict, List

class SentimentAnalyzer:
    
    # Positive words
    positive_words = [
        "happy", "good", "great", "awesome", "wonderful", "excellent", 
        "amazing", "fantastic", "love", "enjoy", "blessed", "grateful",
        "positive", "hopeful", "excited", "proud", "relaxed", "calm",
        "nice", "lovely", "beautiful", "perfect", "brilliant", "glad",
        "joy", "delighted", "wonderful", "terrific", "pleased"
    ]
    
    # Negative words
    negative_words = [
        "sad", "bad", "terrible", "awful", "horrible", "depressed", 
        "anxious", "stressed", "angry", "frustrated", "hurt", "pain",
        "tired", "exhausted", "worried", "scared", "hopeless", "lonely",
        "upset", "miserable", "dreadful", "disappointed", "annoyed",
        "hate", "panic", "stressed", "cry", "miserable"
    ]
    
    @staticmethod
    def analyze(text: str) -> Dict:
        """Analyse sentiment based on keyword matching"""
        text_lower = text.lower()
        
        # Count positive and negative words
        positive_count = 0
        negative_count = 0
        
        for word in SentimentAnalyzer.positive_words:
            if word in text_lower:
                positive_count += 1
        
        for word in SentimentAnalyzer.negative_words:
            if word in text_lower:
                negative_count += 1
        
        # Calculate polarity
        total = positive_count + negative_count
        if total == 0:
            polarity = 0
        else:
            polarity = (positive_count - negative_count) / total
        
        # Cap at -1 to 1 range
        polarity = max(-1, min(1, polarity))
        
        # Determine label
        if polarity > 0.2:
            label = "positive"
            emoji = "😊"
        elif polarity < -0.2:
            label = "negative"
            emoji = "😔"
        else:
            label = "neutral"
            emoji = "😐"
        
        # Extract key phrases
        key_phrases = []
        for word in SentimentAnalyzer.positive_words:
            if word in text_lower and word not in key_phrases:
                key_phrases.append(word)
                if len(key_phrases) >= 3:
                    break
        if len(key_phrases) < 3:
            for word in SentimentAnalyzer.negative_words:
                if word in text_lower and word not in key_phrases:
                    key_phrases.append(word)
                    if len(key_phrases) >= 3:
                        break
        
        return {
            "polarity": round(polarity, 2),
            "label": label,
            "emoji": emoji,
            "key_phrases": key_phrases[:3],
            "positive_count": positive_count,
            "negative_count": negative_count
        }
    
    @staticmethod
    def analyze_batch(texts: List[str]) -> Dict:
        results = [SentimentAnalyzer.analyze(t) for t in texts if t]
        
        if not results:
            return {"avg_polarity": 0, "common_label": "neutral", "total_analysed": 0}
        
        avg_polarity = sum(r["polarity"] for r in results) / len(results)
        
        labels = [r["label"] for r in results]
        common_label = Counter(labels).most_common(1)[0][0] if labels else "neutral"
        
        return {
            "avg_polarity": round(avg_polarity, 2),
            "common_label": common_label,
            "total_analysed": len(results)
        }
    
    @staticmethod
    def get_wellbeing_tip(sentiment: Dict) -> str:
        """Generate a personalised tip based on sentiment"""
        if sentiment["label"] == "positive":
            tips = [
                "You're in a positive space! Keep doing what's working for you.",
                "Great energy! Consider sharing something positive with a friend today.",
                "Your positive mindset is shining through. Keep nurturing it!"
            ]
            return random.choice(tips)
        elif sentiment["label"] == "negative":
            tips = [
                "I notice you might be going through a tough time. Want to talk about it?",
                "Remember that difficult feelings pass. Take a deep breath.",
                "It's okay not to be okay. Consider reaching out to someone you trust."
            ]
            return random.choice(tips)
        else:
            tips = [
                "You seem balanced today. Small steps lead to big changes.",
                "Thanks for sharing. How are you feeling about what you wrote?",
                "Keep going - every entry is a step toward understanding yourself better."
            ]
            return random.choice(tips)