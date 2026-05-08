import re
import random
from typing import Tuple, List, Dict, Optional
from collections import Counter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

class Chat:
    def __init__(self):
       
        #SAFETY: Crisis keywords
        
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
        
       
        #MEMORY
       
        self.user_name = None
        self.last_topic = None
        self.last_user_response = None
        self.conversation_topics = []
        
       
        #ACTIVITIES FOR BOREDOM / FREE TIME
        
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
        
 
        self.how_are_you_responses = [
            "I'm doing alright, thanks for asking. But more importantly, how are YOU feeling?",
            "I'm here to listen to you. What's been going on in your world?",
            "Thanks for checking in. I'm more interested in how you're doing though.",
            "I'm good. But tell me about you - what's been happening?",
            "I appreciate you asking. What's on your mind today?",
            "I'm doing well. What would be most helpful for us to talk about?"
        ]
        
       
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
        
   
        self.boredom_responses = [
            "Feeling bored? Here are some things you could try:",
            "I can suggest some activities if you're looking for something to do:",
            "Want some ideas to fill your time? Here are a few suggestions:",
            "Looking for something to do? Try one of these:"
        ]
        

        self.job_responses = [
            "Looking for jobs can be really stressful. Here are some helpful resources:\n• <a href='https://www.indeed.co.uk' target='_blank'>Indeed - Job Search</a>\n• <a href='https://www.gov.uk/jobsearch' target='_blank'>Gov.uk Job Search</a>\n• <a href='https://www.totaljobs.com' target='_blank'>TotalJobs</a>\n\nWhat kind of work are you looking for?",
            "Job hunting is tough. Try these sites:\n• <a href='https://www.linkedin.com/jobs/' target='_blank'>LinkedIn Jobs</a>\n• <a href='https://www.reed.co.uk' target='_blank'>Reed</a>\n• <a href='https://www.glassdoor.co.uk' target='_blank'>Glassdoor</a>\n\nWhat areas are you interested in?",
            "I hear you about job searching. Here's how to write a good CV: <a href='https://www.careers.govt.nz/resources/cv-and-cover-letter-templates/' target='_blank'>CV Writing Guide</a>\n\nHave you had any luck with applications?",
            "Finding work takes time. Try <a href='https://www.cv-library.co.uk' target='_blank'>CV-Library</a> or <a href='https://www.monster.co.uk' target='_blank'>Monster</a>\n\nWhat would your ideal job look like?",
            "Job hunting can feel endless. The <a href='https://www.nationalcareers.service.gov.uk/job-profiles' target='_blank'>National Careers Service</a> has great advice.\n\nWhat's been the hardest part?",
            "Are you looking for full-time or part-time work?\n\nHere's a guide to <a href='https://www.acas.org.uk/your-rights-and-responsibilities' target='_blank'>employment rights</a> you should know.",
            "What kind of roles have you been applying for?\n\nNeed help with interviews? <a href='https://www.themuse.com/advice/interview-tips' target='_blank'>Interview Tips & Tricks</a>",
            "The job market is tough right now. <a href='https://www.mind.org.uk/information-support/tips-for-everyday-living/work/' target='_blank'>Mind's Work & Mental Health Guide</a> might help.\n\nHow are you coping with it?",
        ]
        
   
        self.money_responses = [
            "Money stress is really hard. Here are some resources that might help:\n• <a href='https://www.citizensadvice.org.uk/debt-and-money/' target='_blank'>Citizens Advice - Money Help</a>\n• <a href='https://www.moneyhelper.org.uk/en' target='_blank'>Money Helper (Government)</a>\n• <a href='https://www.stepchange.org' target='_blank'>StepChange Debt Charity</a>\n\nHave you looked into any financial support options?",
            "I hear you about needing money. <a href='https://www.entitledto.co.uk' target='_blank'>EntitledTo - Benefits Calculator</a> can show what you might be eligible for.\n\nWhat kind of work would you ideally want?",
            "Financial pressure can feel overwhelming. <a href='https://www.mind.org.uk/information-support/tips-for-everyday-living/money-and-mental-health/' target='_blank'>Mind's Money & Mental Health Guide</a>\n\nWhat's been the toughest part?",
            "Money worries affect everything. <a href='https://www.turn2us.org.uk' target='_blank'>Turn2Us - Grants and Benefits Help</a>\n\nAre there any local resources you could tap into?",
            "I understand money is tight. <a href='https://www.gov.uk/student-finance' target='_blank'>Student Finance England</a> or <a href='https://www.gov.uk/universal-credit' target='_blank'>Universal Credit</a> might be relevant.\n\nHave you thought about what kind of income would help most?",
            "Financial stress is exhausting. <a href='https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/money-and-mental-health/' target='_blank'>NHS Guide to Money & Mental Health</a>\n\nWhat would make the biggest difference right now?",
            "Have you looked into student support or hardship funds? Many universities offer <a href='https://www.gov.uk/student-finance' target='_blank'>hardship grants</a>.\n\nWould you like me to help you explore options?",
        ]
        
  
        self.coursework_responses = [
            "Coursework can be overwhelming. Here are some study resources:\n• <a href='https://www.bbc.co.uk/bitesize' target='_blank'>BBC Bitesize</a>\n• <a href='https://www.khanacademy.org' target='_blank'>Khan Academy</a>\n• <a href='https://www.quizlet.com' target='_blank'>Quizlet - Study Tools</a>\n\nHow are you managing it all?",
            "Balancing coursework is tough. Try the <a href='https://todoist.com' target='_blank'>Todoist</a> app for organising deadlines.\n\nWhat's your heaviest subject right now?",
            "I remember you mentioned coursework. <a href='https://www.grammarly.com' target='_blank'>Grammarly</a> can help with writing assignments.\n\nHow's that coming along?",
            "Deadlines can be stressful. Try the <a href='https://pomofocus.io' target='_blank'>Pomodoro Timer</a> for focused study sessions.\n\nWhen are your next assignments due?",
            "What subject are you finding most challenging?\n\n<a href='https://www.youtube.com/crashcourse' target='_blank'>Crash Course on YouTube</a> has great free tutorials.",
            "Are you getting the support you need with your coursework?\n\nMost universities offer <a href='https://www.mind.org.uk/information-support/tips-for-everyday-living/student-life/' target='_blank'>student wellbeing services</a>.",
            "How do you usually manage when coursework gets overwhelming?\n\nTry <a href='https://www.notion.so' target='_blank'>Notion</a> for organising notes and deadlines.",
            "Is there a particular assignment that's worrying you?\n\n<a href='https://www.thestudyspace.com' target='_blank'>The Study Space</a> offers free study tips and motivation.",
        ]
      
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
        
    
        self.anxious_responses = [
            "Anxiety can feel overwhelming. Would you like to try a breathing exercise? <a href='https://www.calm.com/breathe' target='_blank'>Calm Breathing Exercise</a>",
            "I hear you're feeling worried. The <a href='https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/stress-busting-techniques/' target='_blank'>NHS stress guide</a> has some helpful techniques.",
            "Anxiety is tough. Here's a <a href='https://www.therapistaid.com/therapy-worksheet/anxiety-journal' target='_blank'>guided journal exercise</a> that might help.",
            "Let's take a moment. Try breathing in for 4 seconds, holding for 4, and out for 4.",
            "When anxiety hits, grounding yourself can help. Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.",
            "Remember that anxious feelings usually pass. You've gotten through tough moments before.",
            "Would it help to talk about what's specifically worrying you right now?"
        ]
        
   
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
        
   
        self.name_responses = [
            "Nice to meet you, {name}. What's been on your mind?",
            "Hi {name}, good to properly meet you. I'm here for you.",
            "Thanks for sharing your name, {name}. How are you feeling today?",
            "Lovely to meet you, {name}. What would you like to talk about?",
            "Good to know your name, {name}. What's been happening in your world?",
            "Hi {name}. I'm glad you're here. What's on your mind today?"
        ]
        
 
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
        
    
        self.reference_phrases = [
            "just that", "like i said", "as i mentioned", "already told you",
            "i said", "remember", "that thing", "what i said", "you know",
            "like i was saying", "as i was saying"
        ]

        self.job_support_sites = [
            "Here are some job support websites:\n\n• <a href='https://www.indeed.co.uk' target='_blank'>Indeed</a> - Largest job board\n• <a href='https://www.linkedin.com/jobs/' target='_blank'>LinkedIn Jobs</a> - Network and apply\n• <a href='https://www.totaljobs.com' target='_blank'>TotalJobs</a>\n• <a href='https://www.reed.co.uk' target='_blank'>Reed</a>\n• <a href='https://www.gov.uk/jobsearch' target='_blank'>Gov.uk Job Search</a>\n\nWould you like help with CV writing or interview tips?",
        ]

        self.money_support_sites = [
            "Here are some money support websites:\n\n• <a href='https://www.citizensadvice.org.uk/debt-and-money/' target='_blank'>Citizens Advice - Free Money Advice</a>\n• <a href='https://www.moneyhelper.org.uk/en' target='_blank'>Money Helper (Government)</a>\n• <a href='https://www.stepchange.org' target='_blank'>StepChange - Free Debt Advice</a>\n• <a href='https://www.entitledto.co.uk' target='_blank'>EntitledTo - Benefits Calculator</a>\n• <a href='https://www.turn2us.org.uk' target='_blank'>Turn2Us - Grants Search</a>\n\nWould you like me to help you explore any of these options?",
        ]

        self.stress_management_tips = [
            "Here are some stress management techniques:\n\n• <a href='https://www.calm.com/breathe' target='_blank'>5-Minute Breathing Exercise</a>\n• <a href='https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/stress-busting-techniques/' target='_blank'>NHS Stress-Busting Guide</a>\n• <a href='https://www.mind.org.uk/information-support/tips-for-everyday-living/stress/' target='_blank'>Mind's Stress Guide</a>\n• Try the 5-4-3-2-1 grounding technique: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste",
        ]

      
        self.boredom_keywords = ["bored", "nothing to do", "free time", "what to do", "any ideas", "suggest something"]
        self.kindness_keywords = ["kind", "kindness", "nice thing", "good deed", "help someone"]
        self.happiness_keywords = ["happier", "feel better", "cheer up", "boost mood", "feel good", "happy"]
        
        self.journal_summary_keywords = [
            "what did i write", "show me my journal", "journal summary", 
            "what have i been writing", "read my journal", "my entries",
            "summarise my journal", "summarize my journal", "journal recap"
        ]

        self.mood_analysis_keywords = [
            "how is my mood", "mood trend", "am i getting better", 
            "track my mood", "mood analysis", "how have i been feeling"
        ]


        self.job_support_keywords = ["job support", "job sites", "job websites", "find a job", "job search"]
        self.money_support_keywords = ["money support", "financial help", "money help", "benefits", "financial support"]
        self.stress_keywords = ["stress tips", "manage stress", "stress management", "calm down"]

 
    
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


    
    async def get_journal_summary(self, user_id: str, db) -> str:
        from app.models.journal import JournalEntry
        
        result = await db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(desc(JournalEntry.created_at))
            .limit(7)
        )
        entries = result.scalars().all()
    
        if not entries:
            return "You haven't written any journal entries yet. Would you like to write one now?"
    
        sentiments = [e.sentiment_label for e in entries if e.sentiment_label]
        sentiment_counts = Counter(sentiments) if sentiments else {}
        mood_scores = [e.mood_score for e in entries if e.mood_score]
        avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 3
    
        response = f"📊 Journal Summary\n\n"
        response += f"You've written {len(entries)} entries recently.\n"
        response += f"Average mood: {avg_mood:.1f}/5\n\n"
    
        if sentiment_counts:
            response += f"Sentiment breakdown:\n"
            for label, count in sentiment_counts.items():
                emoji = "😊" if label == "positive" else "😔" if label == "negative" else "😐"
                response += f"  {emoji} {label}: {count}\n"
            response += "\n"
    
        latest = entries[0]
        preview = latest.encrypted_content[:100] + "..." if len(latest.encrypted_content) > 100 else latest.encrypted_content
        response += f"Latest entry:\n{preview}\n"
    
        return response

    async def analyze_my_mood(self, user_id: str, db) -> str:
        from app.models.journal import JournalEntry
        
        result = await db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(desc(JournalEntry.created_at))
            .limit(14)
        )
        entries = result.scalars().all()
    
        if len(entries) < 3:
            return "You don't have enough journal entries yet for me to analyse your mood trends. Try writing a few more entries!"
    
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
    
        response = f"📈 Mood Trend Analysis\n\n"
        response += f"Based on your last {len(entries)} journal entries:\n"
        response += f"Overall trend: {trend}\n\n"
        response += advice
    
        return response

    

    
    
    
    async def get_wellbeing_summary(self, user_id: str, db) -> str:
        from app.services.wellbeing_service import WellbeingService
        
        latest = WellbeingService.get_latest_assessment(user_id)
        
        if not latest:
            return "You haven't completed a wellbeing assessment yet. Would you like to take one? You can find it in the Mood & Wellbeing section."
        
        category = latest.get('category', 'Unknown')
        total_score = latest.get('total_score', 0)
        date = latest.get('date', '')[:10]
        
        category_advice = {
            "Excellent": "You're thriving! Here are some resources to maintain your wellbeing:\n• <a href='https://www.nhs.uk/every-mind-matters/' target='_blank'>Every Mind Matters</a>\n• <a href='https://www.mind.org.uk/information-support/tips-for-everyday-living/wellbeing/' target='_blank'>Mind Wellbeing Tips</a>",
            "Good": "You're doing well! Here are some resources to keep you on track:\n• <a href='https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/' target='_blank'>NHS Self-Help Guides</a>\n• <a href='https://www.mentalhealth.org.uk/explore-mental-health/publications' target='_blank'>Mental Health Foundation</a>",
            "Moderate": "You're managing. Here are some resources that might help:\n• <a href='https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/tips-for-low-mood/' target='_blank'>NHS Tips for Low Mood</a>\n• <a href='https://www.mind.org.uk/information-support/tips-for-everyday-living/wellbeing/wellbeing/' target='_blank'>Mind Wellbeing Guide</a>",
            "Concerning": "Your wellbeing matters. Here are some resources that can help:\n• <a href='https://www.mind.org.uk/information-support/guides-to-support-and-services/crisis-services/' target='_blank'>Mind Crisis Services</a>\n• <a href='https://www.nhs.uk/mental-health/nhs-voluntary-charity-services/' target='_blank'>NHS Mental Health Services</a>\n• <a href='https://www.samaritans.org/' target='_blank'>Samaritans - 116 123</a>",
            "Critical": "Please reach out for support. You deserve help:\n• <a href='https://www.samaritans.org/' target='_blank'>Samaritans - 116 123 (24/7)</a>\n• <a href='https://www.nhs.uk/mental-health/nhs-voluntary-charity-services/' target='_blank'>NHS Mental Health Services</a>"
        }
        
        advice = category_advice.get(category, "Here are some general wellbeing resources:\n• <a href='https://www.nhs.uk/every-mind-matters/' target='_blank'>Every Mind Matters</a>\n• <a href='https://www.mind.org.uk/' target='_blank'>Mind</a>")
        
        response = f"📊 Your Latest Wellbeing Assessment\n\n"
        response += f"Date: {date}\n"
        response += f"Score: {total_score}/5\n"
        response += f"Category: {category}\n\n"
        response += f"Personalised Advice:\n{advice}\n\n"
        response += f"Would you like to take another assessment or talk about how you've been feeling?"
        
        return response

    async def analyze_wellbeing_trend(self, user_id: str, db) -> str:
        from app.services.wellbeing_service import WellbeingService
        
        history = WellbeingService.get_user_history(user_id)
        
        if not history:
            return "You haven't completed any wellbeing assessments yet. Take one in the Mood & Wellbeing section to start tracking your progress!"
        
        if len(history) < 2:
            return f"You've completed {len(history)} assessment. Take another one to see your progress over time!"
        
        scores = []
        dates = []
        for item in history[:5]:
            scores.append(float(item.get('total_score', 0)))
            dates.append(item.get('date', '')[:10])
        
        if len(scores) >= 2:
            first = scores[-1]
            last = scores[0]
            difference = last - first
            
            if difference > 0.5:
                trend = "improving significantly 📈"
                advice = "That's fantastic progress! What do you think has helped you feel better?"
            elif difference > 0.2:
                trend = "improving 📈"
                advice = "Good progress! Keep up the positive habits you've been building."
            elif difference < -0.5:
                trend = "declining significantly 📉"
                advice = "I notice your scores have been lower. Would you like to talk about what might be affecting your wellbeing?"
            elif difference < -0.2:
                trend = "declining 📉"
                advice = "Your scores have trended downward. Here's a <a href='https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/tips-for-low-mood/' target='_blank'>NHS guide for low mood</a> that might help."
            else:
                trend = "stable 📊"
                advice = "Your wellbeing has been consistent. Small daily habits can make a big difference over time."
        else:
            trend = "insufficient data"
            advice = "Complete more assessments to see your wellbeing trend!"
        
        response = f"📈 Wellbeing Trend Analysis\n\n"
        response += f"Based on your last {len(history)} assessments:\n"
        
        for i, (score, date) in enumerate(zip(scores[:3], dates[:3])):
            response += f"  {date}: {score}/5\n"
        
        response += f"\n📊 Overall trend: {trend}\n\n"
        response += f"{advice}\n\n"
        response += f"Would you like to take a new assessment or talk about specific concerns?"
        
        return response

    async def get_wellbeing_tips(self, user_id: str, db, topic: str = None) -> str:
        from app.services.wellbeing_service import WellbeingService
        
        latest = WellbeingService.get_latest_assessment(user_id)
        
        if not latest:
            return "Take a wellbeing assessment first to get personalised tips! You can find it in the Mood & Wellbeing section."
        
        category = latest.get('category', 'Moderate')
        
        tips_by_category = {
            "Excellent": [
                "🌟 Keep up your great habits! Consider sharing what works with others.",
                "📝 Try a gratitude journal - write 3 good things each day.",
                "🧘 Maintain your wellbeing with <a href='https://www.nhs.uk/every-mind-matters/' target='_blank'>Every Mind Matters</a>",
                "💪 Challenge yourself to learn something new or help someone this week."
            ],
            "Good": [
                "🌱 Small improvements can make a big difference. Try adding one new positive habit.",
                "📖 Read <a href='https://www.shortstoryguide.com/uplifting-short-stories/' target='_blank'>uplifting short stories</a> to boost your mood.",
                "🧘 Try <a href='https://www.calm.com/breathe' target='_blank'>5-minute breathing exercises</a> daily.",
                "💚 Connect with others - <a href='https://www.meetup.com' target='_blank'>find local groups on Meetup</a>"
            ],
            "Moderate": [
                "🌿 Focus on small steps. Here's a <a href='https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/tips-for-low-mood/' target='_blank'>NHS guide for low mood</a>",
                "🚶 Take a 10-minute walk each day - it's proven to boost mood.",
                "📝 Try journaling your thoughts using the journal feature.",
                "💬 Talk to someone you trust. <a href='https://www.samaritans.org/' target='_blank'>Samaritans</a> are available 24/7 if you need support."
            ],
            "Concerning": [
                "🫂 Your wellbeing matters. <a href='https://www.mind.org.uk/information-support/guides-to-support-and-services/crisis-services/' target='_blank'>Mind Crisis Services</a> can help.",
                "📞 Reach out to <a href='https://www.samaritans.org/' target='_blank'>Samaritans</a> at 116 123 for confidential support.",
                "🧘 Try this <a href='https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/stress-busting-techniques/' target='_blank'>NHS stress-busting guide</a>",
                "💙 Remember: you're not alone. Many people care about your wellbeing."
            ],
            "Critical": [
                "🆘 Please reach out immediately: <a href='https://www.samaritans.org/' target='_blank'>Samaritans 116 123</a>",
                "🏥 Contact your GP or <a href='https://www.nhs.uk/mental-health/nhs-voluntary-charity-services/' target='_blank'>NHS Mental Health Services</a>",
                "💙 You deserve support. <a href='https://www.mind.org.uk/information-support/guides-to-support-and-services/crisis-services/' target='_blank'>Mind Crisis Support</a>"
            ]
        }
        
        tips = tips_by_category.get(category, tips_by_category["Moderate"])
        selected_tips = random.sample(tips, min(2, len(tips)))
        
        response = f"💡 Personalised Wellbeing Tips (Based on your {category} category)\n\n"
        for tip in selected_tips:
            response += f"• {tip}\n"
        response += f"\nWould you like to take a new assessment to update your results?"
        
        return response

   

    
    
    async def get_reply(self, message: str, last_messages: List[Dict] = None) -> Tuple[str, str, Optional[List[str]]]:
    

    
        if self.is_crisis(message):
            return (
                "I'm really concerned about what you're sharing. Your safety is the most important thing.\n\n"
                "Please reach out to someone who can help right away:\n\n" + 
                "\n".join(self.help_lines) +
                "\n\nYou don't have to go through this alone. Please reach out.",
                "CRISIS",
                self.help_lines
            )
    
        msg_lower = message.lower()
    
    

    
        if any(phrase in msg_lower for phrase in self.journal_summary_keywords):
            return "📊 I can see your journal entries. Please ask this question from the main chat interface.", "journal_summary", None
    
        if any(phrase in msg_lower for phrase in self.mood_analysis_keywords):
            return "📈 I can analyse your mood trend. Please ask this question from the main chat interface.", "mood_analysis", None
    
    
    #EXTRACT AND STORE NAME
    
        name = self.extract_name(message)
        if name and not self.user_name:
            self.user_name = name
            return random.choice(self.name_responses).format(name=name), "name", None
    
   
    #GREETINGS
   
        greetings = ["hi", "hello", "hey", "hi there", "hello there", "good morning", "good afternoon", "good evening"]
        if any(msg_lower.startswith(greet) for greet in greetings):
            if self.user_name:
                return f"Hey {self.user_name}. How are you doing today?", "greeting", None
            return random.choice(self.greeting_responses), "greeting", None
    
    
  
    
        if "how are you" in msg_lower or "how are you doing" in msg_lower:
            return random.choice(self.how_are_you_responses), "how_are_you", None
    
   

    
        good_phrases = ["i'm good", "im good", "i am good", "doing good", "doing well", "i'm okay", "im okay"]
        if any(phrase in msg_lower for phrase in good_phrases):
            return random.choice(self.good_responses), "good", None
    
   

   
        if any(phrase in msg_lower for phrase in self.job_support_keywords):
            self.last_topic = "job support"
            return random.choice(self.job_support_sites), "job_support", None
    
        if any(phrase in msg_lower for phrase in self.money_support_keywords):
            self.last_topic = "money support"
            return random.choice(self.money_support_sites), "money_support", None
    
        if any(phrase in msg_lower for phrase in self.stress_keywords):
            self.last_topic = "stress management"
            return random.choice(self.stress_management_tips), "stress_tips", None
    
    

    
        if any(word in msg_lower for word in self.boredom_keywords):
            self.last_topic = "activities to do"
            return self.get_activity_suggestions("boredom"), "boredom", None
    
        if any(word in msg_lower for word in self.kindness_keywords):
            self.last_topic = "acts of kindness"
            return self.get_activity_suggestions("kindness"), "kindness", None
    
        if any(word in msg_lower for word in self.happiness_keywords):
            self.last_topic = "mood boosting activities"
            return self.get_activity_suggestions("happiness"), "happiness", None
    
  
    #If user asks a question
        if "?" in message or any(word in msg_lower for word in ["what", "how", "why", "when", "where", "who"]):
            self.last_topic = None
    
    
        if self.is_referring_to_previous(message) and self.last_topic:
            return random.choice(self.followup_responses).format(topic=self.last_topic), "followup", None
    
   #users are allowed to tell stories
        if self.is_story(message):
            topics = self.extract_topics(message)
            if topics:
                self.last_topic = topics[0]
            return random.choice(self.story_responses), "story", None
    
  #topics and responses
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
    
    
        self.last_user_response = message
    
        if self.last_topic and len(message.split()) < 8:
            return random.choice(self.followup_responses).format(topic=self.last_topic), "followup", None
    
        return random.choice(self.default_responses), "default", None