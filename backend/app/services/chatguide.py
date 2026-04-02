import re
import random

class Chat:
    def __init__(self):
        self.crisis_words = [
            "kill myself", "end my life", "want to die", "suicide", "don't want to live",
            "hurt myself", "self harm", "hurt myself", "cut myself", "i give up", "no reason to live",
            "cant do this anymore", "ending it all", "i'm going to kill myself"
        ]

        self.help_lines = [
            "Samaritans: 116 123 (Available to call 24/7)",
            "Emergency responses 111 (Available for medical health)",
            "Mind: 0300 123 3393 (Support for Mental Health)"
            "SHOUT text: 85258",
            "Papyrus HOPELINE247: 0800 068 4141"
        ]

        self.rules = [
            {
                "words": ["sad", "down", "depressed", "unhappy", "low"],
                "replies": [
                    "I hear that you're feeling sad. Want to talk about it?",
                    "That sounds really hard. What's making you feel this way?",
                    "Feeling down is tough. I'm here to listen.",
                    "Tell me more about it, I'm listening"
                ]
            },
            {
                "words": ["anxious", "nervous", "worried", "stressed", "overwhelmed"],
                "replies": [
                    "Anxiety can be overwhelming. What's on your mind?",
                    "I can hear you're worried. Let's take a deep breath together.",
                    "When you feel anxious, it helps to focus on one thing at a time."
                ]
            },
            {
                "words": ["angry", "frustrated", "annoyed", "mad"],
                "replies": [
                    "It's okay to feel angry. What happened?",
                    "I hear your frustration. Want to talk about it?",
                    "Anger is normal. What's triggering these feelings?"
                ]
            },
            {
                "words": ["alone", "lonely", "nobody", "no one"],
                "replies": [
                    "Feeling alone is really hard. I'm here with you right now.",
                    "Loneliness hurts. Would you like to talk about it?",
                    "You're not alone in this conversation. What's on your mind?"
                ]
            }
        ]

        self.defaults = [
            "Tell me more about how you feel?",
            "How does it make you feel?",
            "I'm listening , tell me more.",
            "How long have you felt this way?"
        ]

        self.greetings = [
            "Hi", "hello", "hey", "hi there", "morning", "afternoon", "evening",
        ]

        self.greetings_replies = [
            "Hello! , How are you doing today?"
            "Hiya , what's on your mind?"
            "Hey , I'm here to listen to what you have to tell me about"
        ]

    def is_crisis(self, message):
            msg = message.lower()
            for word in self.crisis_words:
                if word in msg:
                    return True
            return False
        
    def get_reply(self, message):
            if self.is_crisis(message):
                return(
                    "I'm worried for your health , please reach out to help right away" + "\n".join(self.help_lines),
                    "CRISIS",
                    self.help_lines
                )
            msg_lower = message.lower()
            for greet in self.greetings:
                if msg_lower.startswith(greet):
                    return random.choice(self.greeting_replies), "greeting", None
                
                for rule in self.rules:
                    for word in rule ["words"]:
                        if word in msg_lower:
                            return random.choice(rule["replies"]), rule["words"][0], None
                        
            return random.choice(self.defaults), "default", None
                        

