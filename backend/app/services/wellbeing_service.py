"""
Wellbeing Service - Handles CSV loading and saving for wellbeing assessments
Demonstrates file I/O, CSV parsing, and data persistence
"""
import csv
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# File paths
DATA_DIR = Path("/app/data")
TIPS_FILE = DATA_DIR / "wellbeing_tips.csv"
RESULTS_FILE = DATA_DIR / "wellbeing_results.csv"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================
# QUESTION DEFINITIONS
# ============================================

SWEMWBS_QUESTIONS = [
    {"id": "q1_optimistic", "text": "I've been feeling optimistic about the future", "focus": "optimistic"},
    {"id": "q2_useful", "text": "I've been feeling useful", "focus": "useful"},
    {"id": "q3_relaxed", "text": "I've been feeling relaxed", "focus": "relaxed"},
    {"id": "q4_dealing", "text": "I've been dealing with problems well", "focus": "dealing"},
    {"id": "q5_thinking", "text": "I've been thinking clearly", "focus": "thinking"},
    {"id": "q6_close", "text": "I've been feeling close to other people", "focus": "close"},
    {"id": "q7_decisions", "text": "I've been able to make up my own mind about things", "focus": "decisions"},
]

PHQ2_QUESTIONS = [
    {"id": "q8_interest", "text": "Little interest or pleasure in doing things", "focus": "interest"},
    {"id": "q9_depressed", "text": "Feeling down, depressed, or hopeless", "focus": "depressed"},
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


# ============================================
# WELLBEING SERVICE CLASS
# ============================================

class WellbeingService:
    """Service for managing wellbeing assessments with CSV storage"""
    
    @staticmethod
    def load_tips() -> List[Dict]:
        """Load tips from CSV file - demonstrates file reading and CSV parsing"""
        tips = []
        
        if not TIPS_FILE.exists():
            print(f"Warning: Tips file not found at {TIPS_FILE}")
            return WellbeingService._get_default_tips()
        
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
            return WellbeingService._get_default_tips()
        
        return tips
    
    @staticmethod
    def _get_default_tips() -> List[Dict]:
        """Fallback tips if CSV file not found"""
        return [
            {'category': 'general', 'question_focus': 'general', 'score_min': 0, 'score_max': 5, 'tip': 'Take care of yourself today.'},
            {'category': 'optimistic', 'question_focus': 'optimistic', 'score_min': 1, 'score_max': 2, 'tip': 'Try writing down one good thing that happened today.'},
        ]
    
    @staticmethod
    def get_tips_for_assessment(scores: Dict, total_score: float, category: str) -> List[str]:
        """Get personalised tips based on scores - demonstrates data processing"""
        tips = WellbeingService.load_tips()
        selected_tips = []
        
        # Add general category tips
        for tip in tips:
            if tip['category'] == 'general' and tip['question_focus'] == category.lower():
                if tip['score_min'] <= total_score <= tip['score_max']:
                    selected_tips.append(tip['tip'])
                    break
        
        # Add question-specific tips for low scores (1-2)
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
            score = scores.get(q_key, 3)
            if score <= 2:  # Low score, needs tip
                for tip in tips:
                    if tip['question_focus'] == focus and tip['score_min'] <= score <= tip['score_max']:
                        selected_tips.append(tip['tip'])
                        break
        
        # Add PHQ-2 specific alert if needed
        phq2_avg = (scores.get('q8_interest', 3) + scores.get('q9_depressed', 3)) / 2
        if phq2_avg > 3.5:
            selected_tips.append("💙 You've been experiencing low mood. Please consider reaching out to a mental health professional.")
        
        # Return unique tips (no duplicates)
        return list(dict.fromkeys(selected_tips))[:5]  # Max 5 tips
    
    @staticmethod
    def save_assessment(user_id: str, responses: Dict, total_score: float, category: str, tips: List[str]) -> bool:
        """Save assessment results to CSV - demonstrates file writing and data persistence"""
        
        # Prepare row data
        row = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'date': datetime.utcnow().isoformat(),
            'total_score': round(total_score, 2),
            'category': category,
            'q1_optimistic': responses.get('q1_optimistic', 3),
            'q2_useful': responses.get('q2_useful', 3),
            'q3_relaxed': responses.get('q3_relaxed', 3),
            'q4_dealing': responses.get('q4_dealing', 3),
            'q5_thinking': responses.get('q5_thinking', 3),
            'q6_close': responses.get('q6_close', 3),
            'q7_decisions': responses.get('q7_decisions', 3),
            'q8_interest': responses.get('q8_interest', 3),
            'q9_depressed': responses.get('q9_depressed', 3),
            'tips': '|'.join(tips[:3])  # Store first 3 tips
        }
        
        # Check if file exists to write headers
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
        """Get all assessments for a user - demonstrates CSV reading and filtering"""
        history = []
        
        if not RESULTS_FILE.exists():
            return history
        
        try:
            with open(RESULTS_FILE, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('user_id') == user_id:
                        # Convert tips back to list
                        tips_str = row.get('tips', '')
                        row['tips_list'] = tips_str.split('|') if tips_str else []
                        history.append(row)
            
            # Sort by date descending (most recent first)
            history.sort(key=lambda x: x.get('date', ''), reverse=True)
        except Exception as e:
            print(f"Error reading history: {e}")
        
        return history
    
    @staticmethod
    def get_latest_assessment(user_id: str) -> Optional[Dict]:
        """Get the most recent assessment for a user"""
        history = WellbeingService.get_user_history(user_id)
        return history[0] if history else None