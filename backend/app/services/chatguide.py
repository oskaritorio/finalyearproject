import re
import random
from typing import Tuple, List, Dict, Optional
from app.models.journal import JournalEntry
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

class Chat:
    def __init__(self):
        # ============================================
        # SAFETY: Crisis keywords
        # ============================================
        self.crisis_words = [
            "kill myself", "end my life", "want to die", "suicide",
            "hurt myself", "self harm", "cut myself", "harm myself",
            "no reason to live", "give up", "can't go on", "better off dead",
            "want to end it", "feel like dying"
        ]
        
        self.help_lines = [
            "Samaritans: 116 123 (free, 24/7) - <a href='https://www.samaritans.org' target='_blank' style='color: #9CAF88; text-decoration: underline;'>Visit Samaritans Website</a>",
            "NHS 111: 111 - <a href='https://www.nhs.uk/mental-health' target='_blank' style='color: #9CAF88; text-decoration: underline;'>NHS Mental Health Services</a>",
            "Mind: 0300 123 3393 - <a href='https://www.mind.org.uk' target='_blank' style='color: #9CAF88; text-decoration: underline;'>Visit Mind Website</a>",
            "SHOUT: Text 85258 - <a href='https://www.giveusashout.org' target='_blank' style='color: #9CAF88; text-decoration: underline;'>Visit SHOUT Website</a>"
        ]
        
        # ============================================
        # MEMORY
        # ============================================
        self.user_name = None
        self.last_topic = None
        self.last_user_response = None
        self.conversation_topics = []
        self.conversation_history = []
        
        # ============================================
        # ACTIVITIES FOR BOREDOM / FREE TIME
        # ============================================
        self.boredom_activities = [
            "Try reading a book: <a href='https://www.gutenberg.org/' target='_blank'>Free eBooks from Project Gutenberg</a>",
            "Learn something new: <a href='https://www.khanacademy.org/' target='_blank'>Khan Academy - Free Courses</a>",
            "Take a virtual museum tour: <a href='https://artsandculture.google.com/' target='_blank'>Google Arts & Culture</a>",
            "Do a puzzle: <a href='https://www.jigsawplanet.com/' target='_blank'>Free Online Jigsaw Puzzles</a>",
            "Listen to relaxing music: <a href='https://www.youtube.com/watch?v=jfKfPfyJRdk' target='_blank'>Lo-Fi Study Beats</a>",
            "Try a creative hobby: <a href='https://www.skillshare.com/' target='_blank'>Skillshare (free trial)</a>",
            "Go for a walk - fresh air helps clear the mind",
            "Try cooking something new - here's <a href='https://www.bbcgoodfood.com/' target='_blank'>BBC Good Food</a> for recipes"
        ]
        
        # ============================================
        # KINDNESS ACTIVITIES
        # ============================================
        self.kindness_activities = [
            "Send a thoughtful message to a friend or family member",
            "Do a small favour for someone without being asked",
            "Write a thank-you note to someone who helped you recently",
            "Compliment a stranger today - it might make their day",
            "Donate to a charity you care about",
            "Check in on someone who might be feeling lonely",
            "Hold the door open for someone",
            "Leave a kind note for a colleague or classmate",
            "Offer to help someone with a task",
            "Listen to someone who needs to talk"
        ]
        
        # ============================================
        # HAPPINESS / MOOD-BOOSTING ACTIVITIES
        # ============================================
        self.happiness_activities = [
            "Listen to uplifting music: <a href='https://open.spotify.com/playlist/37i9dQZF1DX3Ogo9pFvBkY' target='_blank'>Spotify Happy Playlist</a>",
            "Watch something funny: <a href='https://www.youtube.com/results?search_query=funny+cats' target='_blank'>Funny Videos</a>",
            "Practice gratitude - write down 3 things you're thankful for",
            "Watch a feel-good movie: <a href='https://www.imdb.com/list/ls000032679/' target='_blank'>Top Feel-Good Movies</a>",
            "Call a friend you haven't spoken to in a while",
            "Look at old photos that make you smile",
            "Treat yourself to something you enjoy - a coffee, a walk, a bath",
            "Read something uplifting: <a href='https://www.shortstoryguide.com/uplifting-short-stories/' target='_blank'>Uplifting Short Stories</a>"
        ]
        
        # ============================================
        # SELF-CARE ACTIVITIES
        # ============================================
        self.self_care_activities = [
            "Take a 10-minute break from screens",
            "Make yourself a warm drink and sit quietly",
            "Do some gentle stretching: <a href='https://www.nhs.uk/live-well/exercise/10-minute-stretch/' target='_blank'>NHS 10-Minute Stretch</a>",
            "Take a relaxing bath or shower",
            "Try mindful breathing: <a href='https://www.calm.com/breathe' target='_blank'>Calm Breathing Exercise</a>",
            "Get 7-8 hours of sleep tonight",
            "Drink a glass of water - staying hydrated helps mood",
            "Write down one thing you achieved today, no matter how small"
        ]
        
        # ============================================
        # GREETING RESPONSES
        # ============================================
        self.greeting_responses = [
            "Hey there. How are you doing today?",
            "Hi. Good to see you. What's on your mind?",
            "Hello. How's your day been so far?",
            "Hey. I'm here if you want to talk about anything.",
            "Hi there. Take your time, I'm listening.",
            "Hello. What's been happening in your world?",
            "Hey. How are you feeling today?",
            "Hi. I'm glad you're here. What would you like to talk about?"
        ]
        
        # ============================================
        # "HOW ARE YOU?" RESPONSES
        # ============================================
        self.how_are_you_responses = [
            "I'm doing alright, thanks for asking. But more importantly, how are YOU feeling?",
            "I'm here to listen to you. What's been going on in your world?",
            "Thanks for checking in. I'm more interested in how you're doing though.",
            "I'm good. But tell me about you - what's been happening?",
            "I appreciate you asking. What's on your mind today?",
            "I'm doing well. What would be most helpful for us to talk about?"
        ]
        
        # ============================================
        # GOOD/OKAY RESPONSES
        # ============================================
        self.good_responses = [
            "That's good to hear. Anything specific making today a good day?",
            "Glad to hear that. What's been going well for you?",
            "Nice. Want to share what's been working out?",
            "That's good. Anything on your mind that you want to talk about anyway?",
            "I'm happy to hear that. What's contributed to you feeling good?",
            "That's great. Is there anything you'd still like to talk about?",
            "Good to know. What's been the highlight of your day?",
            "I'm glad you're doing well. Anything you want to celebrate?"
        ]
        
        # ============================================
        # BOREDOM RESPONSES
        # ============================================
        self.boredom_responses = [
            "Feeling bored? Here are some things you could try:",
            "I can suggest some activities if you're looking for something to do:",
            "Want some ideas to fill your time? Here are a few suggestions:",
            "Looking for something to do? Try one of these:"
        ]
        
        # ============================================
        # JOB RESPONSES
        # ============================================
        self.job_responses = [
            "Looking for jobs can be really stressful. How's that process going for you?",
            "Job hunting is tough. What kind of work are you looking for?",
            "I hear you about job searching. Have you had any luck with applications?",
            "Finding work takes time. What areas are you interested in?",
            "Job hunting can feel endless. What's been the hardest part?",
            "Are you looking for full-time or part-time work?",
            "What kind of roles have you been applying for?",
            "The job market is tough right now. How are you coping with it?",
            "Have you had any interviews yet? How did they go?",
            "What would your ideal job look like right now?"
        ]
        
        # ============================================
        # COURSEWORK RESPONSES
        # ============================================
        self.coursework_responses = [
            "Coursework can be overwhelming. How are you managing it all?",
            "Balancing coursework is tough. What's your heaviest subject right now?",
            "I remember you mentioned coursework. How's that coming along?",
            "Deadlines can be stressful. When are your next assignments due?",
            "What subject are you finding most challenging right now?",
            "Are you getting the support you need with your coursework?",
            "How do you usually manage when coursework gets overwhelming?",
            "Is there a particular assignment that's worrying you?"
        ]
        
        # ============================================
        # MONEY RESPONSES
        # ============================================
        self.money_responses = [
            "Money stress is really hard. Have you looked into any financial support options?",
            "I hear you about needing money. What kind of work would you ideally want?",
            "Financial pressure can feel overwhelming. What's been the toughest part?",
            "Money worries affect everything. Are there any local resources you could tap into?",
            "I understand money is tight. Have you thought about what kind of income would help most?",
            "Financial stress is exhausting. What would make the biggest difference right now?",
            "Have you looked into student support or hardship funds?",
            "I hear you. Money problems can feel like they take over everything."
        ]
        
        # ============================================
        # SADNESS RESPONSES (with links to happiness activities)
        # ============================================
        self.sad_responses = [
            "I'm sorry to hear that. Want to tell me what happened?",
            "That sounds really hard. I'm here to listen if you want to share.",
            "I hear you. Sometimes just talking about it helps a bit. What's going on?",
            "That's tough. Do you want to talk about what's making you feel this way?",
            "I'm really sorry you're going through that.",
            "Feeling down is really heavy. When did you first notice feeling this way?",
            "What would help you feel even a little better right now?",
            "Sometimes doing something kind for yourself can help. Here's an idea: " + random.choice(self.self_care_activities),
            "Would you like me to suggest something that might help lift your mood?"
        ]

        journal_summary_keywords = [
            "what did i write", "show me my journal", "journal summary", 
            "what have i been writing", "read my journal", "my entries",
            "summarise my journal", "summarize my journal", "journal recap"
        ]       

        mood_analysis_keywords = [
            "how is my mood", "mood trend", "am i getting better", 
            "track my mood", "mood analysis", "how have i been feeling"
        ]

        
        # ============================================
        # ANXIETY RESPONSES (with links to calming activities)
        # ============================================
        self.anxious_responses = [
            "Anxiety can feel overwhelming. Would you like to try a breathing exercise? <a href='https://www.calm.com/breathe' target='_blank'>Calm Breathing Exercise</a>",
            "I hear you're feeling worried. The <a href='https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/stress-busting-techniques/' target='_blank'>NHS stress guide</a> has some helpful techniques.",
            "Anxiety is tough. Here's a <a href='https://www.therapistaid.com/therapy-worksheet/anxiety-journal' target='_blank'>guided journal exercise</a> that might help.",
            "Let's take a moment. Try breathing in for 4 seconds, holding for 4, and out for 4.",
            "When anxiety hits, grounding yourself can help. Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.",
            "Remember that anxious feelings usually pass. You've gotten through tough moments before.",
            "Would it help to talk about what's specifically worrying you right now?"
        ]
        
        # ============================================
        # STORY RESPONSES
        # ============================================
        self.story_responses = [
            "Wow, that sounds really difficult. How are you feeling about it now?",
            "I see. That must have been hard to go through. Want to talk more about it?",
            "Thanks for sharing that with me. How did that situation make you feel?",
            "That's a lot to deal with. What's been the toughest part of all this?",
            "I hear you. That sounds really unfair. How are you coping with it?",
            "Thank you for telling me that. What happened next?",
            "That sounds like a lot to carry. How are you holding up?",
            "I really appreciate you sharing that. What would support look like for you right now?"
        ]
        
        # ============================================
        # NAME RECOGNITION RESPONSES
        # ============================================
        self.name_responses = [
            "Nice to meet you, {name}. What's been on your mind?",
            "Hi {name}, good to properly meet you. I'm here for you.",
            "Thanks for sharing your name, {name}. How are you feeling today?",
            "Lovely to meet you, {name}. What would you like to talk about?",
            "Good to know your name, {name}. What's been happening in your world?",
            "Hi {name}. I'm glad you're here. What's on your mind today?"
        ]
        
        # ============================================
        # FOLLOW-UP RESPONSES
        # ============================================
        self.followup_responses = [
            "So you mentioned {topic}. Tell me more about that.",
            "Thanks for sharing about {topic}. How's that going for you?",
            "I remember you said {topic}. What's been happening with that?",
            "Going back to what you said about {topic} - how do you feel about it now?",
            "You mentioned {topic} earlier. Want to continue talking about that?",
            "I was thinking about what you said regarding {topic}. How are you feeling about it?",
            "Let's come back to {topic} - what's the most important part for you?",
            "You brought up {topic} before. Has anything changed since then?"
        ]
        
        # ============================================
        # DEFAULT RESPONSES
        # ============================================
        self.default_responses = [
            "I hear you. Want to tell me more about that?",
            "That sounds important. How does that make you feel?",
            "I'm listening. What else is on your mind?",
            "Thanks for sharing that. What do you think would help right now?",
            "I appreciate you telling me that. How long have you been feeling this way?",
            "That's really interesting. Can you help me understand a bit more?",
            "I want to make sure I understand. Could you tell me more?",
            "Thank you for trusting me with this. What would support look like for you?",
            "I hear you. What feels like the most pressing thing to talk about?",
            "That sounds really important. What do you need most right now?"
        ]
        
        # ============================================
        # REFERENCE PHRASES
        # ============================================
        self.reference_phrases = [
            "just that", "like i said", "as i mentioned", "already told you",
            "i said", "remember", "that thing", "what i said", "you know",
            "like i was saying", "as i was saying"
        ]

        # ============================================
        # KEYWORD DETECTION FOR ACTIVITIES
        # ============================================
        self.boredom_keywords = ["bored", "nothing to do", "free time", "what to do", "any ideas", "suggest something"]
        self.kindness_keywords = ["kind", "kindness", "nice thing", "good deed", "help someone"]
        self.happiness_keywords = ["happier", "feel better", "cheer up", "boost mood", "feel good", "happy"]
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def extract_topics(self, message: str) -> List[str]:
        topics = []
        msg_lower = message.lower()
        
        topic_keywords = {
            "jobs": ["job", "work", "career", "interview", "application", "hiring", "employment"],
            "money": ["money", "bills", "rent", "expensive", "cost", "paid", "financial"],
            "coursework": ["coursework", "assignment", "deadline", "exam", "study", "class", "uni"],
            "sad": ["sad", "down", "depressed", "unhappy", "low", "miserable", "lonely", "heartbroken"],
            "anxious": ["anxious", "nervous", "worried", "stressed", "overwhelmed", "panic", "scared", "fear"],
            "bored": self.boredom_keywords,
            "kindness": self.kindness_keywords,
            "happiness": self.happiness_keywords
        }
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in msg_lower:
                    topics.append(topic)
                    break
        
        return topics
    
    def is_story(self, message: str) -> bool:
        if len(message.split()) > 15:
            return True
        story_indicators = ["happened", "today", "yesterday", "then", "and then", "so then", "because"]
        msg_lower = message.lower()
        for indicator in story_indicators:
            if indicator in msg_lower:
                return True
        return False
    
    def is_referring_to_previous(self, message: str) -> bool:
        msg_lower = message.lower()
        return any(phrase in msg_lower for phrase in self.reference_phrases)
    
    def extract_name(self, message: str) -> Optional[str]:
        patterns = [
            r"my name is (\w+)",
            r"i'm called (\w+)",
            r"name is (\w+)",
            r"call me (\w+)"
        ]
        msg_lower = message.lower()
        for pattern in patterns:
            match = re.search(pattern, msg_lower)
            if match:
                return match.group(1).capitalize()
        return None
    
    def is_crisis(self, message: str) -> bool:
        msg_lower = message.lower()
        for word in self.crisis_words:
            if word in msg_lower:
                return True
        return False
    
    def get_activity_suggestions(self, category: str) -> str:
        if category == "boredom":
            activity = random.choice(self.boredom_activities)
            return f"{random.choice(self.boredom_responses)}\n\n• {activity}"
        elif category == "kindness":
            activity = random.choice(self.kindness_activities)
            return f"Here's an act of kindness you could do today:\n\n• {activity}\n\nSmall acts of kindness can boost your mood and someone else's too."
        elif category == "happiness":
            activity = random.choice(self.happiness_activities)
            return f"Here's something that might help lift your mood:\n\n• {activity}"
        elif category == "self_care":
            activity = random.choice(self.self_care_activities)
            return f"Here's a self-care idea:\n\n• {activity}\n\nTaking care of yourself is important."
        return None

    # ============================================
    # MAIN REPLY FUNCTION
    # ============================================
    
    async def get_reply(self, message: str, last_messages: List[Dict] = None) -> Tuple[str, str, Optional[List[str]]]:
        # ============================================
        # SAFETY FIRST - Crisis detection
        # ============================================
        if self.is_crisis(message):
            return (
                "I'm really concerned about what you're sharing. Your safety is the most important thing.\n "
                "\n\nPlease reach out to someone who can help right away:\n\n" + 
                "\n".join(self.help_lines) +
                "\n\nYou don't have to go through this alone. Please reach out.",
                "CRISIS",
                self.help_lines
            )
        
        msg_lower = message.lower()
        # ============================================
        # JOURNAL COMMANDS - Chatbot reads journals
        # ============================================

        journal_summary_keywords = [
            "what did i write", "show me my journal", "journal summary", 
            "what have i been writing", "read my journal", "my entries",
            "summarise my journal", "summarize my journal", "journal recap"
        ]

        mood_analysis_keywords = [
            "how is my mood", "mood trend", "am i getting better", 
            "track my mood", "mood analysis", "how have i been feeling"
        ]

        if any(phrase in msg_lower for phrase in journal_summary_keywords):
            summary = await self.get_journal_summary(current_user.id, db)
            return summary, "journal_summary", None

        if any(phrase in msg_lower for phrase in mood_analysis_keywords):
            analysis = await self.analyze_my_mood(current_user.id, db)
            return analysis, "mood_analysis", None
        
        # ============================================
        # Extract and store name
        # ============================================
        name = self.extract_name(message)
        if name and not self.user_name:
            self.user_name = name
            return random.choice(self.name_responses).format(name=name), "name", None
        
        # ============================================
        # GREETINGS
        # ============================================
        greetings = ["hi", "hello", "hey", "hi there", "hello there", "good morning", "good afternoon", "good evening"]
        if any(msg_lower.startswith(greet) for greet in greetings):
            if self.user_name:
                return f"Hey {self.user_name}. How are you doing today?", "greeting", None
            return random.choice(self.greeting_responses), "greeting", None
        
        # ============================================
        # "HOW ARE YOU?" - user asking bot
        # ============================================
        if "how are you" in msg_lower or "how are you doing" in msg_lower:
            return random.choice(self.how_are_you_responses), "how_are_you", None
        
        # ============================================
        # "I'M GOOD" responses - dig deeper
        # ============================================
        good_phrases = ["i'm good", "im good", "i am good", "doing good", "doing well", "i'm okay", "im okay"]
        if any(phrase in msg_lower for phrase in good_phrases):
            return random.choice(self.good_responses), "good", None
        
        # ============================================
        # BOREDOM DETECTION
        # ============================================
        if any(word in msg_lower for word in self.boredom_keywords):
            self.last_topic = "activities to do"
            return self.get_activity_suggestions("boredom"), "boredom", None
        
        # ============================================
        # KINDNESS DETECTION
        # ============================================
        if any(word in msg_lower for word in self.kindness_keywords):
            self.last_topic = "acts of kindness"
            return self.get_activity_suggestions("kindness"), "kindness", None
        
        # ============================================
        # HAPPINESS/MOOD BOOST DETECTION
        # ============================================
        if any(word in msg_lower for word in self.happiness_keywords):
            self.last_topic = "mood boosting activities"
            return self.get_activity_suggestions("happiness"), "happiness", None
        
        # ============================================
        # USER REFERRING TO PREVIOUS CONVERSATION
        # ============================================
        if self.is_referring_to_previous(message) and self.last_topic:
            return random.choice(self.followup_responses).format(topic=self.last_topic), "followup", None
        
        # ============================================
        # USER TELLING A STORY
        # ============================================
        if self.is_story(message):
            topics = self.extract_topics(message)
            if topics:
                self.last_topic = topics[0]
            return random.choice(self.story_responses), "story", None
        
        # ============================================
        # EXTRACT TOPICS AND RESPOND
        # ============================================
        topics = self.extract_topics(message)
        
        if "jobs" in topics:
            self.last_topic = "looking for jobs"
            return random.choice(self.job_responses), "jobs", None
        
        if "coursework" in topics:
            self.last_topic = "your coursework"
            return random.choice(self.coursework_responses), "coursework", None
        
        if "money" in topics:
            self.last_topic = "needing money"
            return random.choice(self.money_responses), "money", None
        
        if "sad" in topics:
            self.last_topic = "feeling sad"
            return random.choice(self.sad_responses), "sadness", None
        
        if "anxious" in topics:
            self.last_topic = "feeling anxious"
            return random.choice(self.anxious_responses), "anxiety", None
        
        
        
        # ============================================
        # DEFAULT - try to reference last topic if possible
        # ============================================
        self.last_user_response = message
        
        if self.last_topic and len(message.split()) < 8:
            return random.choice(self.followup_responses).format(topic=self.last_topic), "followup", None
        
        return random.choice(self.default_responses), "default", None
    
    async def get_journal_context(self, user_id: str, db: AsyncSession) -> str:
        """Get recent journal entries to provide context for chatbot"""
        from app.models.journal import JournalEntry
        from sqlalchemy import select, desc
    
        result = await db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(desc(JournalEntry.created_at))
            .limit(3)
        )
        entries = result.scalars().all()
    
        if not entries:
            return ""
    
        topics = []
        for entry in entries:
            content = entry.encrypted_content.lower()
            if "stress" in content or "anxious" in content:
                topics.append("stress and anxiety")
            if "work" in content or "job" in content:
                topics.append("work")
            if "exam" in content or "study" in content:
                topics.append("exams")
            if "friend" in content or "family" in content:
                topics.append("relationships")
            if "bored" in content:
                topics.append("feeling bored")
    
        if topics:
            unique_topics = list(set(topics))
            return f"I noticed from your journal that you've been dealing with {', '.join(unique_topics)}. Would you like to talk about that?"
    
        return ""
    
    async def get_journal_summary(self, user_id: str, db, period: str = "recent") -> str:
    
    # Get recent entries
        result = await db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(desc(JournalEntry.created_at))
            .limit(7)
        )
        entries = result.scalars().all()
    
        if not entries:
            return "You haven't written any journal entries yet. Would you like to write one now?"
    
    # Count sentiments
        sentiments = [e.sentiment_label for e in entries if e.sentiment_label]
        sentiment_counts = Counter(sentiments) if sentiments else {}
    
    # Calculate average mood from entries (not just quick mood)
        mood_scores = [e.mood_score for e in entries if e.mood_score]
        avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 3
    
    # Find common topics from key phrases
        all_phrases = []
        for e in entries:
            if e.key_phrases:
                all_phrases.extend(e.key_phrases.split(','))
        top_phrases = Counter(all_phrases).most_common(3) if all_phrases else []
    
    # Build response
        response = f"📊 **Journal Summary**\n\n"
        response += f"You've written {len(entries)} entries recently.\n"
        response += f"Average mood: {avg_mood:.1f}/5\n\n"
    
        if sentiment_counts:
            response += f"**Sentiment breakdown:**\n"
            for label, count in sentiment_counts.items():
                emoji = "😊" if label == "positive" else "😔" if label == "negative" else "😐"
                response += f"  {emoji} {label}: {count}\n"
            response += "\n"
    
        if top_phrases:
            response += f"**Common themes:** {', '.join([p[0] for p in top_phrases])}\n\n"
    
    # Latest entry preview
        latest = entries[0]
        preview = latest.encrypted_content[:100] + "..." if len(latest.encrypted_content) > 100 else latest.encrypted_content
        response += f"📝 **Latest entry:**\n{preview}\n"
    
        return response

    async def analyze_my_mood(self, user_id: str, db) -> str:
    
        result = await db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(desc(JournalEntry.created_at))
            .limit(14)
        )
        entries = result.scalars().all()
    
        if len(entries) < 3:
            return "You don't have enough journal entries yet for me to analyse your mood trends. Try writing a few more entries!"
    
    # Calculate sentiment trend
        sentiments = [e.sentiment_score for e in entries if e.sentiment_score is not None]
        if len(sentiments) >= 3:
            recent_avg = sum(sentiments[:3]) / 3
            older_avg = sum(sentiments[-3:]) / 3
        
            if recent_avg > older_avg + 0.2:
                trend = "improving 📈"
                advice = "That's great! What do you think has contributed to this positive shift?"
            elif recent_avg < older_avg - 0.2:
                trend = "declining 📉"
                advice = "I notice you've been feeling lower lately. Would you like to talk about what might be affecting your mood?"
            else:
                trend = "stable 📊"
                advice = "Your mood has been consistent. Small daily habits can make a big difference over time."
        else:
            trend = "insufficient data"
            advice = "Keep journaling so I can track your mood patterns!"
    
        response = f"📈 **Mood Trend Analysis**\n\n"
        response += f"Based on your last {len(entries)} journal entries:\n"
        response += f"Overall trend: {trend}\n\n"
        response += advice
    
        return response

    async def compare_mood_to_journal(self, user_id: str, db, quick_mood: int) -> str:
    
        result = await db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(desc(JournalEntry.created_at))
            .limit(1)
        )
        latest_journal = result.scalar_one_or_none()
    
        if not latest_journal:
            return None
    
        journal_mood = latest_journal.mood_score
        journal_sentiment = latest_journal.sentiment_label
    
        if abs(quick_mood - journal_mood) <= 1:
            return f"Your quick mood ({quick_mood}/5) matches your recent journal entry! Consistency is great for tracking."
        else:
            return f"I notice a difference - your quick mood is {quick_mood}/5, but your recent journal entry suggested a {journal_sentiment} feeling ({journal_mood}/5). Would you like to explore why there might be a difference?"