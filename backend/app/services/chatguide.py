import re
import random
from typing import Tuple, List, Dict, Optional
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
            "📞 **Samaritans**: 116 123 (free, 24/7) - [Visit Website](https://www.samaritans.org)",
            "📞 **NHS 111**: 111 (medical help) - [NHS Mental Health](https://www.nhs.uk/mental-health)",
            "📞 **Mind**: 0300 123 3393 - [Visit Mind Website](https://www.mind.org.uk)",
            "📞 **SHOUT**: Text 85258 - [Visit SHOUT](https://www.giveusashout.org)"
        ]
        
        # ============================================
        # MEMORY
        # ============================================
        self.user_name = None
        self.last_topic = None
        self.last_user_response = None
        self.conversation_topics = []  # Track topics discussed
        
        # ============================================
        # GREETING RESPONSES (8 variations)
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
        # "HOW ARE YOU?" RESPONSES (6 variations)
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
        # GOOD/OKAY RESPONSES (dig deeper, 8 variations)
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
        # JOB RESPONSES (10 variations)
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
        # COURSEWORK RESPONSES (8 variations)
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
        # MONEY RESPONSES (8 variations)
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
        # SADNESS RESPONSES (12 variations)
        # ============================================
        self.sad_responses = [
            "I'm sorry to hear that. Want to tell me what happened?",
            "That sounds really hard. I'm here to listen if you want to share.",
            "I hear you. Sometimes just talking about it helps a bit. What's going on?",
            "That's tough. Do you want to talk about what's making you feel this way?",
            "I'm really sorry you're going through that. What's been the hardest part?",
            "Feeling down is really heavy. When did you first notice feeling this way?",
            "I hear so much pain in your words. What would help you feel even a little better?",
            "That sounds really painful. I'm glad you reached out. What's on your mind?",
            "Sadness can feel so isolating. You're not alone in this. What's been happening?",
            "I'm here with you. What do you think triggered these feelings?",
            "Sometimes when we're sad, everything feels harder. What's one small thing that might help?",
            "Thank you for trusting me with these feelings. What does this sadness need right now?"
        ]
        
        # ============================================
        # ANXIETY RESPONSES (12 variations)
        # ============================================
        self.anxious_responses = [
    "😰 Anxiety can feel overwhelming. Try this <a href='https://www.calm.com/breathe' target='_blank' style='color: #9CAF88; text-decoration: underline;'>5-minute breathing exercise</a> or <a href='https://www.mind.org.uk/information-support/tips-for-everyday-living/wellbeing/wellbeing/' target='_blank' style='color: #9CAF88; text-decoration: underline;'>read wellbeing tips from Mind</a>.",
    "I hear you're feeling worried. Here's a helpful <a href='https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/stress-busting-techniques/' target='_blank' style='color: #9CAF88; text-decoration: underline;'>NHS guide to stress</a>.",
    "Anxiety is tough. Would you like to try a <a href='https://www.therapistaid.com/therapy-worksheet/anxiety-journal' target='_blank' style='color: #9CAF88; text-decoration: underline;'>guided journal exercise</a>?"
]
        
        # ============================================
        # STORY RESPONSES (when user shares something specific, 8 variations)
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

        self.activity_responses = [
    "🎯 Here's an activity that might help: <a href='https://www.nytimes.com/2016/05/08/well/move/the-scientific-7-minute-workout.html' target='_blank' style='color: #9CAF88; text-decoration: underline;'>7-minute workout</a>",
    "🌿 Try this: <a href='https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/stress-busting-techniques/' target='_blank' style='color: #9CAF88; text-decoration: underline;'>NHS stress-busting techniques</a>",
    "💚 Here's a helpful resource: <a href='https://www.mind.org.uk/information-support/tips-for-everyday-living/wellbeing/' target='_blank' style='color: #9CAF88; text-decoration: underline;'>Mind wellbeing tips</a>"
]
        
        # ============================================
        # NAME RECOGNITION RESPONSES (6 variations)
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
        # FOLLOW-UP RESPONSES (references previous topic, 8 variations)
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
        # DEFAULT RESPONSES (10 variations)
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
        # REFERENCE PHRASES (user referring to previous conversation)
        # ============================================
        self.reference_phrases = [
            "just that", "like i said", "as i mentioned", "already told you",
            "i said", "remember", "that thing", "what i said", "you know",
            "like i was saying", "as i was saying"
        ]
    
    # ============================================
    # Extract topics from user message
    # ============================================
    def extract_topics(self, message: str) -> List[str]:
        topics = []
        msg_lower = message.lower()
        
        topic_keywords = {
            "jobs": ["job", "work", "career", "interview", "application", "hiring", "employment"],
            "money": ["money", "bills", "rent", "expensive", "cost", "paid", "financial"],
            "coursework": ["coursework", "assignment", "deadline", "exam", "study", "class", "uni"],
            "sad": ["sad", "down", "depressed", "unhappy", "low", "miserable", "lonely", "heartbroken"],
            "anxious": ["anxious", "nervous", "worried", "stressed", "overwhelmed", "panic", "scared", "fear"]
        }
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in msg_lower:
                    topics.append(topic)
                    break
        
        return topics
    
    # ============================================
    # Check if user is telling a story
    # ============================================
    def is_story(self, message: str) -> bool:
        if len(message.split()) > 15:
            return True
        story_indicators = ["happened", "today", "yesterday", "then", "and then", "so then", "because"]
        msg_lower = message.lower()
        for indicator in story_indicators:
            if indicator in msg_lower:
                return True
        return False
    
    # ============================================
    # Check if user is referring to previous conversation
    # ============================================
    def is_referring_to_previous(self, message: str) -> bool:
        msg_lower = message.lower()
        return any(phrase in msg_lower for phrase in self.reference_phrases)
    
    # ============================================
    # Extract name
    # ============================================
    def extract_name(self, message: str) -> Optional[str]:
        patterns = [
            r"my name is (\w+)",
            r"i'm called (\w+)",
            r"i am (\w+)",
            r"name is (\w+)",
            r"call me (\w+)"
        ]
        msg_lower = message.lower()
        for pattern in patterns:
            match = re.search(pattern, msg_lower)
            if match:
                return match.group(1).capitalize()
        return None
    
    # ============================================
    # Check for crisis
    # ============================================
    def is_crisis(self, message: str) -> bool:
        msg_lower = message.lower()
        for word in self.crisis_words:
            if word in msg_lower:
                return True
        return False

    def get_reply(self, message: str, last_messages: List[Dict] = None) -> Tuple[str, str, Optional[List[str]]]:
        if self.is_crisis(message):
            return (
                "I'm really concerned about what you're sharing. Your safety is the most important thing. "
                "Please reach out to someone who can help right away:\n\n" + 
                "\n".join(self.help_lines) +
                "\n\nYou don't have to go through this alone. Please reach out.",
                "CRISIS",
                self.help_lines
            )
        
        msg_lower = message.lower()
        
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
        # USER REFERRING TO PREVIOUS CONVERSATION
        # ============================================
        if self.is_referring_to_previous(message) and self.last_topic:
            return random.choice(self.followup_responses).format(topic=self.last_topic), "followup", None
        
        # ============================================
        # USER TELLING A STORY
        # ============================================
        if self.is_story(message):
            # Store topics from the story
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
    
        # Extract topics from journals
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
    
        if topics:
            unique_topics = list(set(topics))
            return f"I noticed from your journal that you've been dealing with {', '.join(unique_topics)}. Would you like to talk about that?"
    
        return ""