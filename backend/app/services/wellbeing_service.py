
import csv
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

DATA_DIR = Path("/app/data")
TIPS_FILE = DATA_DIR / "wellbeing_tips.csv"
RESULTS_FILE = DATA_DIR / "wellbeing_results.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)



#QUESTION DEFINITIONS


SWEMWBS_QUESTIONS = [
    {"id": "q1_optimistic", "text": "I've been feeling optimistic about the future", "focus": "optimistic", "negative": False},
    {"id": "q2_useful", "text": "I've been feeling useful", "focus": "useful", "negative": False},
    {"id": "q3_relaxed", "text": "I've been feeling relaxed", "focus": "relaxed", "negative": False},
    {"id": "q4_dealing", "text": "I've been dealing with problems well", "focus": "dealing", "negative": False},
    {"id": "q5_thinking", "text": "I've been thinking clearly", "focus": "thinking", "negative": False},
    {"id": "q6_close", "text": "I've been feeling close to other people", "focus": "close", "negative": False},
    {"id": "q7_decisions", "text": "I've been able to make up my own mind about things", "focus": "decisions", "negative": False},
]

PHQ2_QUESTIONS = [
    {"id": "q8_interest", "text": "Little interest or pleasure in doing things", "focus": "interest", "negative": True},
    {"id": "q9_depressed", "text": "Feeling down, depressed, or hopeless", "focus": "depressed", "negative": True},
]

ALL_QUESTIONS = SWEMWBS_QUESTIONS + PHQ2_QUESTIONS


def calculate_category(score: float) -> Tuple[str, str]:
    """Calculate category based on total score"""
    if score >= 4.5:
        return "Excellent", "🟢"
    elif score >= 3.5:
        return "Good", "🟢"
    elif score >= 2.5:
        return "Moderate", "🟡"
    elif score >= 1.5:
        return "Concerning", "🟠"
    else:
        return "Critical", "🔴"


def flip_negative_score(score: int) -> int:
  
    return 6 - score


def process_responses(responses: Dict) -> Dict:

    processed = {}
    
    for q in ALL_QUESTIONS:
        q_id = q["id"]
        original_score = responses.get(q_id, 3)
        
        if q["negative"]:
            # Flip negative questions
            processed[q_id] = flip_negative_score(original_score)
            print(f"Flipped {q_id}: {original_score} → {processed[q_id]}")
        else:
            processed[q_id] = original_score
    
    return processed


class WellbeingService:
    
    @staticmethod
    def load_tips() -> List[Dict]:
        tips = []
        
        if not TIPS_FILE.exists():
            print(f"Warning: Tips file not found at {TIPS_FILE}")
            return []
        
        try:
            with open(TIPS_FILE, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    tips.append({
                        'category': row['category'],
                        'question_focus': row['question_focus'],
                        'score_min': float(row['score_min']),
                        'score_max': float(row['score_max']),
                        'tip': row['tip']
                    })
            print(f"Loaded {len(tips)} tips from CSV")
        except Exception as e:
            print(f"Error loading tips: {e}")
        
        return tips
    
    @staticmethod
    def get_tips_for_assessment(responses: Dict, total_score: float, category: str) -> List[str]:
        tips = WellbeingService.load_tips()
        selected_tips = []
        
        #Process responses to get flipped scores for low score detection
        processed = process_responses(responses)
        
        #Add general category tips
        category_lower = category.lower()
        for tip in tips:
            if tip['category'] == 'general' and tip['question_focus'] == category_lower:
                if tip['score_min'] <= total_score <= tip['score_max']:
                    selected_tips.append(tip['tip'])
                    break
        
        #Add question-specific tips for low scores (1-2) on flipped scores
        question_mapping = {
            'q1_optimistic': 'optimistic',
            'q2_useful': 'useful', 
            'q3_relaxed': 'relaxed',
            'q4_dealing': 'dealing',
            'q5_thinking': 'thinking',
            'q6_close': 'close',
            'q7_decisions': 'decisions',
            'q8_interest': 'interest',
            'q9_depressed': 'depressed'
        }
        
        for q_key, focus in question_mapping.items():
            # Use the flipped score from processed dict
            score = processed.get(q_key, 3)
            if score <= 2:  # Low score after flipping
                for tip in tips:
                    if tip['category'] == 'specific' and tip['question_focus'] == focus:
                        if tip['score_min'] <= score <= tip['score_max']:
                            selected_tips.append(tip['tip'])
                            break
        
        #Remove duplicates and limit to 5 tips
        return list(dict.fromkeys(selected_tips))[:5]
    
    @staticmethod
    def save_assessment(user_id: str, responses: Dict, total_score: float, category: str, tips: List[str]) -> bool:
        
        #Process responses to flip negative questions for storage
        processed = process_responses(responses)
        
        row = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'date': datetime.utcnow().isoformat(),
            'total_score': round(total_score, 2),
            'category': category,
            'q1_optimistic': processed.get('q1_optimistic', 3),
            'q2_useful': processed.get('q2_useful', 3),
            'q3_relaxed': processed.get('q3_relaxed', 3),
            'q4_dealing': processed.get('q4_dealing', 3),
            'q5_thinking': processed.get('q5_thinking', 3),
            'q6_close': processed.get('q6_close', 3),
            'q7_decisions': processed.get('q7_decisions', 3),
            'q8_interest': processed.get('q8_interest', 3),
            'q9_depressed': processed.get('q9_depressed', 3),
            'tips': '|'.join(tips[:3])
        }
        
        file_exists = RESULTS_FILE.exists()
        
        try:
            with open(RESULTS_FILE, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=row.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
            print(f"Saved assessment for user {user_id}")
            return True
        except Exception as e:
            print(f"Error saving assessment: {e}")
            return False
    
    @staticmethod
    def get_user_history(user_id: str) -> List[Dict]:
        history = []
        
        if not RESULTS_FILE.exists():
            return history
        
        try:
            with open(RESULTS_FILE, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('user_id') == user_id:
                        tips_str = row.get('tips', '')
                        row['tips_list'] = tips_str.split('|') if tips_str else []
                        history.append(row)
            
            history.sort(key=lambda x: x.get('date', ''), reverse=True)
        except Exception as e:
            print(f"Error reading history: {e}")
        
        return history
    
    @staticmethod
    def get_latest_assessment(user_id: str) -> Optional[Dict]:
        history = WellbeingService.get_user_history(user_id)
        return history[0] if history else None