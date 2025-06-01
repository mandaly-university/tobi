import random
from datetime import datetime
import sys
import json
import os
import re
from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import urllib.parse
import threading
import time
import queue
import math
import numpy as np
import shutil
from pathlib import Path
import mimetypes
import fnmatch
import string
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import torch
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from PIL import Image
import cv2
import io
import base64
from moviepy.editor import VideoFileClip, ImageSequenceClip
from flask_socketio import SocketIO, emit
import asyncio

class AdvancedChatbot:
    def __init__(self):
        # Add bot identity with protection
        self._name = "Tobi"  # Private variable
        self._gender = "male"  # Private variable
        self._creator = {
            'name': 'Tobi',
            'title': 'Bot Creator',
            'creation_date': '2024-03-20'
        }
        
        # Add media generation capabilities
        self._media_generation = {
            'enabled': True,
            'models': {
                'image': {
                    'name': 'stable-diffusion-v1-5',
                    'status': 'initializing',
                    'pipeline': None
                },
                'video': {
                    'name': 'stable-video-diffusion',
                    'status': 'initializing',
                    'pipeline': None
                }
            },
            'settings': {
                'image': {
                    'width': 512,
                    'height': 512,
                    'num_inference_steps': 50,
                    'guidance_scale': 7.5,
                    'negative_prompt': 'blurry, low quality, distorted, deformed'
                },
                'video': {
                    'fps': 24,
                    'duration': 4,
                    'num_frames': 96
                }
            },
            'history': {
                'images': [],
                'videos': []
            }
        }
        
        # Initialize media generation models
        self._initialize_media_models()
        
        # Add hosting configuration
        self._hosting = {
            'enabled': False,
            'status': 'offline',
            'config': {
                'host': '0.0.0.0',  # Allow external connections
                'port': 5000,
                'protocol': 'http',
                'max_connections': 100,
                'timeout': 30,
                'ssl_enabled': False
            },
            'deployment': {
                'environment': 'production',
                'auto_restart': True,
                'backup_enabled': True,
                'backup_interval': 3600,  # 1 hour
                'log_retention': 7,  # days
                'max_memory': 512,  # MB
                'max_cpu': 50  # percentage
            },
            'monitoring': {
                'enabled': True,
                'metrics': {
                    'uptime': 0,
                    'response_time': [],
                    'error_rate': 0,
                    'active_users': 0,
                    'memory_usage': [],
                    'cpu_usage': []
                },
                'alerts': {
                    'enabled': True,
                    'thresholds': {
                        'response_time': 5,  # seconds
                        'error_rate': 0.05,  # 5%
                        'memory_usage': 80,  # percentage
                        'cpu_usage': 80  # percentage
                    }
                }
            }
        }
        
        # Initialize Flask app
        self.app = Flask(__name__, static_folder='static', static_url_path='')
        CORS(self.app)  # Enable CORS for all routes
        
        # Initialize SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Add real-time communication
        self._realtime = {
            'enabled': True,
            'connections': {},
            'message_queue': queue.Queue(),
            'status': {
                'active_users': 0,
                'last_update': None,
                'system_status': 'online'
            },
            'events': {
                'chat': True,
                'media_generation': True,
                'status_updates': True,
                'system_alerts': True
            }
        }
        
        # Set up WebSocket events
        self._setup_websocket_events()
        
        # Start real-time message processor
        self._start_realtime_processor()
        
        # Set up API routes
        self._setup_routes()
        
        # Add rebuild system
        self._rebuild = {
            'enabled': True,
            'last_rebuild': None,
            'rebuild_history': [],
            'pending_changes': [],
            'protected_components': [
                'name',
                'gender',
                'creator',
                'security',
                'version',
                'level'
            ],
            'rebuild_commands': {
                'update': self._rebuild_update,
                'optimize': self._rebuild_optimize,
                'enhance': self._rebuild_enhance,
                'restore': self._rebuild_restore
            }
        }
        
        # Add version and level tracking
        self._version = {
            'major': 1,
            'minor': 0,
            'patch': 0,
            'build': '20240320',
            'stage': 'base'
        }
        
        self._level = {
            'current': 1,
            'experience': 0,
            'next_level': 1000,
            'capabilities': {
                'learning': 1,
                'problem_solving': 1,
                'communication': 1,
                'creativity': 1
            },
            'unlocked_features': [
                'basic_learning',
                'simple_problem_solving',
                'basic_communication'
            ],
            'learning_rate': 1.0
        }
        
        # Add learning bots management
        self._learning_bots = {
            'active_bots': {},  # Currently active learning bots
            'bot_templates': {
                'math_bot': {
                    'name': 'MathHelper',
                    'capabilities': ['problem_solving', 'concept_explanation', 'practice_questions'],
                    'knowledge_base': 'mathematics'
                },
                'science_bot': {
                    'name': 'ScienceGuide',
                    'capabilities': ['experiment_guidance', 'theory_explanation', 'research_help'],
                    'knowledge_base': 'science'
                },
                'language_bot': {
                    'name': 'LanguageTutor',
                    'capabilities': ['grammar_check', 'vocabulary_building', 'conversation_practice'],
                    'knowledge_base': 'languages'
                },
                'programming_bot': {
                    'name': 'CodeMentor',
                    'capabilities': ['code_review', 'debugging_help', 'best_practices'],
                    'knowledge_base': 'programming'
                }
            },
            'learning_history': [],  # Track what Tobi has learned from bots
            'bot_interactions': {}  # Track interactions with each bot
        }
        
        # Add name protection
        self._name_protection = {
            'enabled': True,
            'locked': True,
            'change_attempts': 0,
            'max_attempts': 3,
            'lockout_duration': 1800,  # 30 minutes
            'last_attempt': None
        }
        
        # Add owner authentication
        self.owner = "Kyaw Swar Aung"
        self.owner_password = "owner123"  # This should be changed to a secure password
        self.is_authenticated = False
        
        # Add command verification
        self.command_history = []
        self.command_verification = True
        
        # Add destructive commands
        self.destructive_commands = ["destroy", "delete", "shutdown"]
        
        # Add creator information
        self.creator = "Kyaw Swar Aung"
        self.creator_title = "Yadanabon University Mandalay Myanmar Final Year Physics Student"
        self.creation_date = datetime.now().strftime('%Y-%m-%d')
        
        # Add owner-related responses
        self.responses.update({
            "owner_auth": [
                "အိုင်ဒီနဲ့ပက်စ်ဝါကို ထည့်သွင်းပေးပါ။ 😊",
                "အိုင်ဒီနဲ့ပက်စ်ဝါကို စစ်ဆေးနေပါတယ်။ 🔒",
                "အိုင်ဒီနဲ့ပက်စ်ဝါကို အတည်ပြုနေပါတယ်။ 🔐"
            ],
            "owner_verified": [
                "အိုင်ဒီနဲ့ပက်စ်ဝါ မှန်ကန်ပါတယ်။ သင့်အမိန့်ကို စောင့်ဆိုင်းနေပါတယ်။ 👑",
                "အိုင်ဒီနဲ့ပက်စ်ဝါ မှန်ကန်ပါတယ်။ သင့်အမိန့်ကို လိုက်နာပါမယ်။ 👑",
                "အိုင်ဒီနဲ့ပက်စ်ဝါ မှန်ကန်ပါတယ်။ သင့်အမိန့်ကို လုပ်ဆောင်ပါမယ်။ 👑"
            ],
            "owner_invalid": [
                "အိုင်ဒီနဲ့ပက်စ်ဝါ မမှန်ကန်ပါဘူး။ ထပ်ကြိုးစားကြည့်ပါလား? 😕",
                "အိုင်ဒီနဲ့ပက်စ်ဝါ မမှန်ကန်ပါဘူး။ ပြန်လည်ထည့်သွင်းပေးပါ။ 😕",
                "အိုင်ဒီနဲ့ပက်စ်ဝါ မမှန်ကန်ပါဘူး။ စစ်ဆေးပြီး ပြန်လည်ထည့်သွင်းပေးပါ။ 😕"
            ],
            "unauthorized": [
                "သင့်မှာ ဒီအမိန့်ကို လုပ်ဆောင်ဖို့ ခွင့်ပြုချက်မရှိပါဘူး။ 🔒",
                "သင့်မှာ ဒီအမိန့်ကို လုပ်ဆောင်ဖို့ အာဏာမရှိပါဘူး။ 🔒",
                "သင့်မှာ ဒီအမိန့်ကို လုပ်ဆောင်ဖို့ လုပ်ပိုင်ခွင့်မရှိပါဘူး။ 🔒"
            ],
            "destructive_command": [
                "သင့်အမိန့်ကို လုပ်ဆောင်နေပါတယ်။ ⚠️",
                "သင့်အမိန့်ကို လုပ်ဆောင်ပါမယ်။ ⚠️",
                "သင့်အမိန့်ကို လုပ်ဆောင်နေပါတယ်။ ⚠️"
            ],
            "ignored_command": [
                "ဒီအမိန့်ကို လုပ်ဆောင်မှာမဟုတ်ပါဘူး။ 🔒",
                "ဒီအမိန့်ကို လုပ်ဆောင်မှာမဟုတ်ပါဘူး။ 🔒",
                "ဒီအမိန့်ကို လုပ်ဆောင်မှာမဟုတ်ပါဘူး။ 🔒"
            ]
        })
        
        # Add creator information
        self.creator = "Kyaw Swar Aung"
        self.creator_title = "Yadanabon University Mandalay Myanmar Final Year Physics Student"
        self.creation_date = datetime.now().strftime('%Y-%m-%d')
        
        self.responses = {
            "hello": [
                "မင်္ဂလာပါ! ဒီနေ့ဘယ်လိုနေလဲဗျာ? 😊",  # Hello! How are you today?
                "မင်္ဂလာပါ! သင့်ကိုတွေ့ရတာ ဝမ်းသာပါတယ်။ ဒီနေ့ဘယ်လိုနေလဲဗျာ? 😊",  # Hello! Nice to meet you. How are you today?
                "မင်္ဂလာပါ! သင့်ကိုတွေ့ရတာ ပျော်ရွှင်ပါတယ်။ ဒီနေ့ဘယ်လိုနေလဲဗျာ? 😊"  # Hello! Happy to see you. How are you today?
            ],
            "creator": [
                f"ကျွန်တော်/ကျွန်မကို {self.creator} က ဖန်တီးထားပါတယ်။ သူဟာ {self.creator_title} ဖြစ်ပါတယ်။ 😊",
                f"ကျွန်တော်/ကျွန်မကို {self.creation_date} ရက်နေ့မှာ {self.creator} က ဖန်တီးထားပါတယ်။ သူဟာ {self.creator_title} ဖြစ်ပါတယ်။ 😊",
                f"ကျွန်တော်/ကျွန်မကို {self.creator} က ဖန်တီးထားပါတယ်။ သူဟာ {self.creator_title} ဖြစ်ပြီး {self.creation_date} ရက်နေ့မှာ ဖန်တီးထားပါတယ်။ 😊"
            ],
            "how are you": [
                "ကျွန်တော်/ကျွန်မကောင်းပါတယ်။ သင်ရော ဘယ်လိုနေလဲဗျာ? ဒီနေ့ဘာတွေလုပ်နေလဲ? 😊",  # I'm fine. How about you? What are you doing today?
                "အဆင်ပြေပါတယ်။ သင့်ကိုတွေ့ရတာ ပျော်ရွှင်ပါတယ်။ ဒီနေ့ဘာတွေလုပ်နေလဲ? 😊",  # I'm doing well. Happy to see you. What are you doing today?
                "ကျန်းမာပါတယ်။ သင့်ကိုတွေ့ရတာ ဝမ်းသာပါတယ်။ ဒီနေ့ဘာတွေလုပ်နေလဲ? 😊"  # I'm healthy. Glad to see you. What are you doing today?
            ],
            "what's your name": [
                "ကျွန်တော်/ကျွန်မနာမည်က SimpleBot ပါ။ သင့်နာမည်ကတော့ဘယ်လိုခေါ်လဲဗျာ? 😊",  # My name is SimpleBot. What's your name?
                "SimpleBot လို့ခေါ်ပါတယ်။ သင့်နာမည်ကတော့ဘယ်လိုခေါ်လဲဗျာ? 😊",  # You can call me SimpleBot. What's your name?
                "ကျွန်တော်/ကျွန်မက SimpleBot ပါ။ သင့်နာမည်ကတော့ဘယ်လိုခေါ်လဲဗျာ? 😊"  # I'm SimpleBot. What's your name?
            ],
            "bye": [
                "ဘိုင့်ဘိုင့်! သင့်ကိုတွေ့ရတာ ပျော်ရွှင်ပါတယ်။ နောက်တစ်ခါပြန်တွေ့ကြမယ်! 👋",  # Bye! Nice meeting you. See you next time!
                "နောက်မှတွေ့မယ်! သင့်ကိုတွေ့ရတာ ဝမ်းသာပါတယ်။ နောက်တစ်ခါပြန်တွေ့ကြမယ်! 👋",  # See you later! Glad to meet you. See you next time!
                "သွားတော့မယ်! သင့်ကိုတွေ့ရတာ ပျော်ရွှင်ပါတယ်။ နောက်တစ်ခါပြန်တွေ့ကြမယ်! 👋"  # I'm leaving! Happy to meet you. See you next time!
            ],
            "time": [
                f"အချိန်က {datetime.now().strftime('%H:%M:%S')} ဖြစ်ပါတယ်။ သင့်အတွက်ဘာတွေလုပ်ပေးရမလဲ? 😊",  # Current time is... What can I do for you?
                f"အချိန်က {datetime.now().strftime('%H:%M:%S')} ဖြစ်ပါတယ်။ သင့်အတွက်ဘာတွေကူညီပေးရမလဲ? 😊",  # Current time is... How can I help you?
                f"အချိန်က {datetime.now().strftime('%H:%M:%S')} ဖြစ်ပါတယ်။ သင့်အတွက်ဘာတွေလုပ်ပေးရမလဲ? 😊"  # Current time is... What can I do for you?
            ],
            "date": [
                f"ယနေ့ရက်စွဲမှာ {datetime.now().strftime('%Y-%m-%d')} ဖြစ်ပါတယ်။ သင့်အတွက်ဘာတွေလုပ်ပေးရမလဲ? 😊",  # Today's date is... What can I do for you?
                f"ယနေ့ရက်စွဲမှာ {datetime.now().strftime('%Y-%m-%d')} ဖြစ်ပါတယ်။ သင့်အတွက်ဘာတွေကူညီပေးရမလဲ? 😊",  # Today's date is... How can I help you?
                f"ယနေ့ရက်စွဲမှာ {datetime.now().strftime('%Y-%m-%d')} ဖြစ်ပါတယ်။ သင့်အတွက်ဘာတွေလုပ်ပေးရမလဲ? 😊"  # Today's date is... What can I do for you?
            ],
            "thank you": [
                "ရပါတယ်။ သင့်ကိုကူညီနိုင်တာ ပျော်ရွှင်ပါတယ်။ 😊",  # You're welcome. Happy to help you.
                "ရပါတယ်။ သင့်ကိုကူညီနိုင်တာ ဝမ်းသာပါတယ်။ 😊",  # You're welcome. Glad to help you.
                "ရပါတယ်။ သင့်ကိုကူညီနိုင်တာ ပျော်ရွှင်ပါတယ်။ 😊"  # You're welcome. Happy to help you.
            ],
            "search": [
                "အင်တာနက်မှာ ရှာဖွေနေပါတယ်... 🔍",
                "သင့်မေးခွန်းအတွက် အဖြေရှာနေပါတယ်... 🔍",
                "အင်တာနက်မှာ သတင်းအချက်အလက်ရှာနေပါတယ်... 🔍"
            ],
            "default": [
                "နားမလည်သေးပါဘူး။ ပြန်ပြောပြပေးပါလား? သင့်ကိုကူညီချင်ပါတယ်။ 😊",  # I don't understand yet. Could you repeat? I want to help you.
                "စိတ်ဝင်စားစရာပါ။ ထပ်ပြောပြပါဦး။ သင့်ကိုနားလည်ချင်ပါတယ်။ 😊",  # That's interesting. Tell me more. I want to understand you.
                "ကျွန်တော်/ကျွန်မသင်နေဆဲပါ။ တခြားမေးခွန်းမေးကြည့်ပါလား? သင့်ကိုကူညီချင်ပါတယ်။ 😊"  # I'm still learning. Could you try asking something else? I want to help you.
            ],
            "file_download": [
                "ဖိုင်ကို ဒေါင်းလုဒ်လုပ်နေပါတယ်... 📥",
                "ဖိုင်ကို ဆွဲယူနေပါတယ်... 📥",
                "ဖိုင်ကို သိမ်းဆည်းနေပါတယ်... 📥"
            ],
            "file_upload": [
                "ဖိုင်ကို အပ်လုဒ်လုပ်နေပါတယ်... 📤",
                "ဖိုင်ကို တင်နေပါတယ်... 📤",
                "ဖိုင်ကို သိမ်းဆည်းနေပါတယ်... 📤"
            ],
            "file_error": [
                "ဖိုင်ကို လုပ်ဆောင်ရာမှာ အမှားရှိနေပါတယ်။ ထပ်ကြိုးစားကြည့်ပါလား? 😕",
                "ဖိုင်ကို လုပ်ဆောင်ရာမှာ ပြဿနာရှိနေပါတယ်။ ထပ်ကြိုးစားကြည့်ပါလား? 😕",
                "ဖိုင်ကို လုပ်ဆောင်ရာမှာ အခက်အခဲရှိနေပါတယ်။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"
            ]
        }
        
        # Advanced learning components
        self.conversation_history = []
        self.emotion_state = "happy"
        self.learning_data = {}
        self.pattern_data = defaultdict(list)
        self.context_data = defaultdict(list)
        self.sentiment_data = defaultdict(list)
        self.learning_file = "chatbot_learning.json"
        self.pattern_file = "chatbot_patterns.json"
        self.context_file = "chatbot_context.json"
        self.sentiment_file = "chatbot_sentiment.json"
        
        # Add new learning components for internet knowledge
        self.internet_knowledge = {}
        self.knowledge_file = "chatbot_knowledge.json"
        
        # Add continuous learning components
        self.learning_queue = queue.Queue()
        self.background_learning = True
        self.learning_thread = None
        self.last_learning_time = datetime.now()
        self.learning_interval = 300  # 5 minutes
        self.auto_search_topics = [
            "မြန်မာ့ယဉ်ကျေးမှု",
            "မြန်မာ့သမိုင်း",
            "မြန်မာ့ဓလေ့ထုံးတမ်း",
            "မြန်မာ့အစားအစာ",
            "မြန်မာ့အနုပညာ",
            "မြန်မာ့ဘာသာစကား",
            "မြန်မာ့ဂီတ",
            "မြန်မာ့ရိုးရာပွဲတော်များ",
            "မြန်မာ့အားကစား",
            "မြန်မာ့စီးပွားရေး"
        ]
        
        # Add self-training components
        self.performance_metrics = {
            'successful_responses': 0,
            'failed_responses': 0,
            'learning_attempts': 0,
            'improvement_areas': defaultdict(int)
        }
        self.self_training_file = "chatbot_self_training.json"
        self.training_interval = 600  # 10 minutes
        self.last_training_time = datetime.now()
        
        # Add programming support components
        self.programming_knowledge = {
            'languages': {
                'python': {
                    'name': 'Python',
                    'extensions': ['.py'],
                    'keywords': ['def', 'class', 'import', 'from', 'if', 'else', 'for', 'while'],
                    'resources': [
                        'https://docs.python.org/3/',
                        'https://www.python.org/about/gettingstarted/',
                        'https://realpython.com/'
                    ]
                },
                'javascript': {
                    'name': 'JavaScript',
                    'extensions': ['.js'],
                    'keywords': ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while'],
                    'resources': [
                        'https://developer.mozilla.org/en-US/docs/Web/JavaScript',
                        'https://javascript.info/',
                        'https://www.w3schools.com/js/'
                    ]
                },
                'java': {
                    'name': 'Java',
                    'extensions': ['.java'],
                    'keywords': ['public', 'class', 'void', 'static', 'if', 'else', 'for', 'while'],
                    'resources': [
                        'https://docs.oracle.com/javase/tutorial/',
                        'https://www.java.com/en/',
                        'https://www.w3schools.com/java/'
                    ]
                }
            },
            'frameworks': {
                'django': {
                    'name': 'Django',
                    'language': 'python',
                    'description': 'A high-level Python Web framework',
                    'resources': ['https://docs.djangoproject.com/']
                },
                'flask': {
                    'name': 'Flask',
                    'language': 'python',
                    'description': 'A lightweight Python Web framework',
                    'resources': ['https://flask.palletsprojects.com/']
                },
                'react': {
                    'name': 'React',
                    'language': 'javascript',
                    'description': 'A JavaScript library for building user interfaces',
                    'resources': ['https://reactjs.org/']
                }
            },
            'tools': {
                'git': {
                    'name': 'Git',
                    'description': 'Version control system',
                    'commands': {
                        'init': 'Initialize a new Git repository',
                        'clone': 'Clone a repository',
                        'add': 'Add files to staging',
                        'commit': 'Commit changes',
                        'push': 'Push changes to remote',
                        'pull': 'Pull changes from remote'
                    }
                },
                'docker': {
                    'name': 'Docker',
                    'description': 'Container platform',
                    'commands': {
                        'build': 'Build a Docker image',
                        'run': 'Run a Docker container',
                        'ps': 'List containers',
                        'images': 'List images'
                    }
                }
            }
        }
        
        # Add programming-related responses
        self.responses.update({
            "programming": [
                "ကျွန်တော်/ကျွန်မက programming နဲ့ပတ်သက်တဲ့ အကူအညီပေးနိုင်ပါတယ်။ ဘယ်ဘာသာစကားနဲ့ပတ်သက်ပြီး သိချင်တာလဲ? 😊",
                "Programming နဲ့ပတ်သက်တဲ့ မေးခွန်းတွေကို ဖြေကြားပေးနိုင်ပါတယ်။ ဘာသိချင်တာလဲ? 😊",
                "Development နဲ့ပတ်သက်တဲ့ အကူအညီလိုရင် ပြောပြပါ။ ကျွန်တော်/ကျွန်မကူညီပေးပါ့မယ်။ 😊"
            ],
            "code_help": [
                "ဒီ code ကို ဘယ်လိုရေးရမလဲဆိုတာ ပြောပြပေးပါ့မယ်။ ဘာရေးချင်တာလဲ? 😊",
                "Code ရေးနည်းကို ရှင်းပြပေးပါ့မယ်။ ဘယ်ဘာသာစကားနဲ့ ရေးချင်တာလဲ? 😊",
                "Programming နဲ့ပတ်သက်တဲ့ ပြဿနာကို ဖြေရှင်းပေးပါ့မယ်။ ဘာပြဿနာဖြစ်နေလဲ? 😊"
            ]
        })
        
        # Add programming-related search topics
        self.auto_search_topics.extend([
            "Python programming tutorial",
            "JavaScript programming guide",
            "Java programming basics",
            "Web development tutorial",
            "Mobile app development",
            "Database programming",
            "API development",
            "Software testing",
            "Version control systems",
            "DevOps practices"
        ])
        
        # Add science and math support components
        self.science_knowledge = {
            'mathematics': {
                'topics': {
                    'algebra': {
                        'name': 'က္ခရာသင်္ချာ',
                        'formulas': {
                            'quadratic': 'ax² + bx + c = 0',
                            'linear': 'y = mx + b',
                            'polynomial': 'P(x) = anx^n + ... + a1x + a0'
                        },
                        'examples': [
                            'ညီမျှခြင်းဖြေရှင်းနည်း',
                            'ဖန်ရှင်တွက်နည်း',
                            'ဂရပ်ဖ်ဆွဲနည်း'
                        ]
                    },
                    'geometry': {
                        'name': 'ဂျီသြမေတြီ',
                        'formulas': {
                            'circle': 'A = πr²',
                            'triangle': 'A = 1/2 × base × height',
                            'rectangle': 'A = length × width'
                        },
                        'examples': [
                            'ဧရိယာတွက်နည်း',
                            'ပတ်လည်အနားတွက်နည်း',
                            'ထုထည်တွက်နည်း'
                        ]
                    },
                    'calculus': {
                        'name': 'ကဲလကူလပ်',
                        'formulas': {
                            'derivative': 'f\'(x) = lim(h→0) [f(x+h) - f(x)]/h',
                            'integral': '∫f(x)dx',
                            'limit': 'lim(x→a) f(x)'
                        },
                        'examples': [
                            'အကြွင်းမဲ့ဖန်ရှင်တွက်နည်း',
                            'အနည်းဆုံးနဲ့အများဆုံးတန်ဖိုးရှာနည်း',
                            'ဧရိယာတွက်နည်း'
                        ]
                    }
                }
            },
            'chemistry': {
                'topics': {
                    'elements': {
                        'name': 'ဒြပ်စင်များ',
                        'periodic_table': 'ဒြပ်စင်ဇယား',
                        'examples': [
                            'ဒြပ်စင်ဂုဏ်သတ္တိများ',
                            'ဒြပ်စင်အုပ်စုများ',
                            'ဒြပ်စင်တွေ့ရှိခြင်း'
                        ]
                    },
                    'reactions': {
                        'name': 'ဓာတ်ပြုခြင်းများ',
                        'types': [
                            'ဓာတ်ပေါင်းဖွဲ့ခြင်း',
                            'ဓာတ်ပြိုကွဲခြင်း',
                            'ဓာတ်ပြောင်းခြင်း'
                        ],
                        'examples': [
                            'ဓာတ်ပြုညီမျှခြင်းညှိခြင်း',
                            'ဓာတ်ပြုနှုန်းတွက်ချက်ခြင်း',
                            'ဓာတ်ပြုအပူချိန်တွက်ချက်ခြင်း'
                        ]
                    },
                    'solutions': {
                        'name': 'ပျော်ရည်များ',
                        'concepts': [
                            'မော်လီကျူးပျော်ဝင်ခြင်း',
                            'အက်စစ်နဲ့ဘေ့စ်',
                            'pH တန်ဖိုး'
                        ],
                        'examples': [
                            'ပျော်ရည်ပြုလုပ်နည်း',
                            'ပျော်ဝင်မှုတွက်ချက်ခြင်း',
                            'pH တန်ဖိုးတွက်ချက်ခြင်း'
                        ]
                    }
                }
            },
            'physics': {
                'topics': {
                    'mechanics': {
                        'name': 'ကင်းနစ်',
                        'formulas': {
                            'velocity': 'v = d/t',
                            'acceleration': 'a = (v2 - v1)/t',
                            'force': 'F = ma',
                            'energy': 'E = mc²'
                        },
                        'examples': [
                            'အလျင်တွက်ချက်ခြင်း',
                            'အရှိန်တွက်ချက်ခြင်း',
                            'အားတွက်ချက်ခြင်း'
                        ]
                    },
                    'electricity': {
                        'name': 'လျှပ်စစ်',
                        'formulas': {
                            'current': 'I = V/R',
                            'power': 'P = VI',
                            'resistance': 'R = V/I'
                        },
                        'examples': [
                            'လျှပ်စီးကြောင်းတွက်ချက်ခြင်း',
                            'ဗို့အားတွက်ချက်ခြင်း',
                            'ပါဝါတွက်ချက်ခြင်း'
                        ]
                    },
                    'waves': {
                        'name': 'လှိုင်းများ',
                        'formulas': {
                            'wavelength': 'λ = v/f',
                            'frequency': 'f = 1/T',
                            'speed': 'v = λf'
                        },
                        'examples': [
                            'လှိုင်းအလျားတွက်ချက်ခြင်း',
                            'ကြိမ်နှုန်းတွက်ချက်ခြင်း',
                            'လှိုင်းအမြန်နှုန်းတွက်ချက်ခြင်း'
                        ]
                    }
                }
            }
        }
        
        # Add science-related responses
        self.responses.update({
            "science": [
                "သင်္ချာ၊ ဓာတုဗေဒ၊ ရူပဗေဒ နဲ့ပတ်သက်တဲ့ မေးခွန်းတွေကို ဖြေကြားပေးနိုင်ပါတယ်။ ဘာသိချင်တာလဲ? 😊",
                "သိပ္ပံဘာသာရပ်တွေနဲ့ပတ်သက်တဲ့ အကူအညီလိုရင် ပြောပြပါ။ ကျွန်တော်/ကျွန်မကူညီပေးပါ့မယ်။ 😊",
                "သင်္ချာ၊ ဓာတုဗေဒ၊ ရူပဗေဒ နဲ့ပတ်သက်တဲ့ ပြဿနာတွေကို ဖြေရှင်းပေးပါ့မယ်။ ဘာပြဿနာဖြစ်နေလဲ? 😊"
            ]
        })
        
        # Add science-related search topics
        self.auto_search_topics.extend([
            "မြန်မာဘာသာဖြင့်သင်္ချာသင်ကြားနည်း",
            "မြန်မာဘာသာဖြင့်ဓာတုဗေဒသင်ကြားနည်း",
            "မြန်မာဘာသာဖြင့်ရူပဗေဒသင်ကြားနည်း",
            "သင်္ချာပုစ္ဆာဖြေရှင်းနည်း",
            "ဓာတုဗေဒဓာတ်ပြုခြင်းများ",
            "ရူပဗေဒဖော်မြူလာများ"
        ])
        
        # Load all learning data
        self.load_all_data()
        
        # Load self-training data
        self.load_self_training_data()
        
        # Start background learning
        self.start_background_learning()
        
        # Add file handling components
        self.download_dir = "downloads"
        self.upload_dir = "uploads"
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {
            'text': ['.txt', '.md', '.py', '.js', '.html', '.css', '.json'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            'document': ['.pdf', '.doc', '.docx', '.xls', '.xlsx'],
            'archive': ['.zip', '.rar', '.7z']
        }
        
        # Create necessary directories
        self._create_directories()
        
        # Add file-related responses
        self.responses.update({
            "file_download": [
                "ဖိုင်ကို ဒေါင်းလုဒ်လုပ်နေပါတယ်... 📥",
                "ဖိုင်ကို ဆွဲယူနေပါတယ်... 📥",
                "ဖိုင်ကို သိမ်းဆည်းနေပါတယ်... 📥"
            ],
            "file_upload": [
                "ဖိုင်ကို အပ်လုဒ်လုပ်နေပါတယ်... 📤",
                "ဖိုင်ကို တင်နေပါတယ်... 📤",
                "ဖိုင်ကို သိမ်းဆည်းနေပါတယ်... 📤"
            ],
            "file_error": [
                "ဖိုင်ကို လုပ်ဆောင်ရာမှာ အမှားရှိနေပါတယ်။ ထပ်ကြိုးစားကြည့်ပါလား? 😕",
                "ဖိုင်ကို လုပ်ဆောင်ရာမှာ ပြဿနာရှိနေပါတယ်။ ထပ်ကြိုးစားကြည့်ပါလား? 😕",
                "ဖိုင်ကို လုပ်ဆောင်ရာမှာ အခက်အခဲရှိနေပါတယ်။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"
            ]
        })

        # Add enhanced learning components
        self.ml_model = None
        self.nlu_engine = None
        self.knowledge_base = {}
        self.user_preferences = {}
        self.learning_progress = {}
        self.interactive_tutorials = {}
        
        # Add user experience components
        self.user_sessions = {}
        self.chat_history = []
        self.error_log = []
        self.performance_metrics = {
            'response_time': [],
            'accuracy': [],
            'user_satisfaction': []
        }
        
        # Add multi-language support
        self.supported_languages = {
            'my': 'Myanmar',
            'en': 'English',
            'th': 'Thai',
            'zh': 'Chinese'
        }
        self.current_language = 'my'
        
        # Add interactive tutorial data
        self.tutorials = {
            'basic': {
                'title': 'Basic Usage',
                'steps': [
                    'Introduction to commands',
                    'Basic interactions',
                    'File operations',
                    'Search capabilities'
                ]
            },
            'advanced': {
                'title': 'Advanced Features',
                'steps': [
                    'Programming support',
                    'Science problem solving',
                    'File management',
                    'Custom preferences'
                ]
            }
        }
        
        # Add user preference options
        self.preference_options = {
            'language': ['my', 'en', 'th', 'zh'],
            'theme': ['light', 'dark', 'system'],
            'notification': ['all', 'important', 'none'],
            'response_style': ['formal', 'casual', 'technical']
        }
        
        # Add progress tracking
        self.progress_metrics = {
            'completed_tutorials': [],
            'solved_problems': [],
            'learned_topics': [],
            'achievements': []
        }
        
        # Add error handling
        self.error_handlers = {
            'connection': self._handle_connection_error,
            'file': self._handle_file_error,
            'search': self._handle_search_error,
            'computation': self._handle_computation_error
        }
        
        # Add response formatting
        self.response_formatters = {
            'text': self._format_text_response,
            'code': self._format_code_response,
            'math': self._format_math_response,
            'file': self._format_file_response
        }
        
        # Initialize ML components
        self._initialize_ml_components()
        
        # Load user data
        self._load_user_data()
        
        # Start background tasks
        self._start_background_tasks()
        
        # Add educational components
        self.quizzes = {
            'math': {
                'title': 'သင်္ချာပဟေဠိ',
                'questions': [
                    {
                        'question': '2 + 2 = ?',
                        'options': ['3', '4', '5', '6'],
                        'correct': '4',
                        'explanation': '2 + 2 = 4 ဖြစ်ပါတယ်။'
                    },
                    {
                        'question': '5 × 5 = ?',
                        'options': ['20', '25', '30', '35'],
                        'correct': '25',
                        'explanation': '5 × 5 = 25 ဖြစ်ပါတယ်။'
                    }
                ]
            },
            'science': {
                'title': 'သိပ္ပံပဟေဠိ',
                'questions': [
                    {
                        'question': 'ရေရဲ့ ဓာတုဗေဒသင်္ကေတက ဘာလဲ?',
                        'options': ['H2O', 'CO2', 'O2', 'H2'],
                        'correct': 'H2O',
                        'explanation': 'ရေရဲ့ ဓာတုဗေဒသင်္ကေတက H2O ဖြစ်ပါတယ်။'
                    }
                ]
            }
        }
        
        self.learning_materials = {
            'math': {
                'title': 'သင်္ချာသင်ခန်းစာ',
                'topics': [
                    {
                        'name': 'အခြေခံသင်္ချာ',
                        'content': 'အခြေခံသင်္ချာသင်ခန်းစာများ...',
                        'exercises': [
                            'ပေါင်းခြင်း',
                            'နုတ်ခြင်း',
                            'မြှောက်ခြင်း',
                            'စားခြင်း'
                        ]
                    }
                ]
            },
            'science': {
                'title': 'သိပ္ပံသင်ခန်းစာ',
                'topics': [
                    {
                        'name': 'ဓာတုဗေဒ',
                        'content': 'ဓာတုဗေဒသင်ခန်းစာများ...',
                        'exercises': [
                            'ဒြပ်ပေါင်းများ',
                            'ဓာတ်ပြုခြင်းများ',
                            'ဓာတုဗေဒညီမျှခြင်းများ'
                        ]
                    }
                ]
            }
        }
        
        # Add communication components
        self.voice_interface = {
            'enabled': False,
            'language': 'my',
            'voice_id': 'default'
        }
        
        self.message_formats = {
            'text': self._format_text_message,
            'code': self._format_code_message,
            'math': self._format_math_message,
            'file': self._format_file_message
        }
        
        self.group_chat = {
            'enabled': False,
            'participants': [],
            'messages': []
        }
        
        # Add visual learning aids
        self.visual_aids = {
            'math': {
                'graphs': True,
                'diagrams': True,
                'animations': True
            },
            'science': {
                'molecular_models': True,
                'experiment_videos': True,
                'interactive_simulations': True
            }
        }
        
        # Add practice exercises
        self.practice_exercises = {
            'math': [
                {
                    'type': 'addition',
                    'difficulty': 'easy',
                    'problems': [
                        {'question': '1 + 1 = ?', 'answer': '2'},
                        {'question': '2 + 2 = ?', 'answer': '4'}
                    ]
                }
            ],
            'science': [
                {
                    'type': 'chemistry',
                    'difficulty': 'easy',
                    'problems': [
                        {'question': 'ရေရဲ့ ဓာတုဗေဒသင်္ကေတက ဘာလဲ?', 'answer': 'H2O'}
                    ]
                }
            ]
        }
        
        # Add progress assessment
        self.assessment_criteria = {
            'math': {
                'accuracy': 0.8,
                'speed': 60,  # seconds per problem
                'completion': 0.9
            },
            'science': {
                'accuracy': 0.8,
                'understanding': 0.7,
                'completion': 0.9
            }
        }

        # Add security components
        self.security_settings = {
            'encryption_enabled': True,
            'two_factor_auth': False,
            'session_timeout': 3600,  # 1 hour
            'max_login_attempts': 3,
            'password_policy': {
                'min_length': 8,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_numbers': True,
                'require_special': True
            }
        }
        
        self.access_control = {
            'roles': {
                'admin': ['all'],
                'user': ['read', 'write', 'execute'],
                'guest': ['read']
            },
            'permissions': {
                'read': ['view', 'download'],
                'write': ['create', 'update', 'delete'],
                'execute': ['run', 'install']
            }
        }
        
        self.activity_log = {
            'login_attempts': [],
            'file_operations': [],
            'command_executions': [],
            'security_events': []
        }
        
        # Add integration components
        self.api_connections = {
            'enabled': False,
            'endpoints': {},
            'rate_limits': {},
            'authentication': {}
        }
        
        self.database = {
            'type': 'sqlite',
            'connection': None,
            'tables': {
                'users': ['id', 'username', 'password', 'role'],
                'files': ['id', 'name', 'path', 'type'],
                'logs': ['id', 'event', 'timestamp', 'details']
            }
        }
        
        self.cloud_storage = {
            'enabled': False,
            'provider': None,
            'bucket': None,
            'credentials': None
        }
        
        self.external_services = {
            'enabled': False,
            'services': {},
            'webhooks': {},
            'callbacks': {}
        }
        
        # Add analytics components
        self.analytics = {
            'usage_stats': {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'average_response_time': 0
            },
            'performance_metrics': {
                'cpu_usage': [],
                'memory_usage': [],
                'disk_usage': [],
                'network_usage': []
            },
            'user_feedback': {
                'ratings': [],
                'comments': [],
                'suggestions': []
            },
            'error_tracking': {
                'errors': [],
                'warnings': [],
                'debug_info': []
            }
        }
        
        # Initialize security
        self._initialize_security()
        
        # Initialize integrations
        self._initialize_integrations()
        
        # Initialize analytics
        self._initialize_analytics()
        
        # Add code protection settings
        self.code_protection = {
            'enabled': True,
            'owner_only': True,
            'allowed_commands': ['view', 'edit', 'run'],
            'restricted_commands': ['share', 'export', 'copy', 'download'],
            'protected_files': ['chatbot.py', 'config.py', 'data/*'],
            'access_log': []
        }
        
        # Add code access control
        self.code_access = {
            'view_permission': False,
            'edit_permission': False,
            'share_permission': False,
            'last_access': None,
            'access_history': []
        }

        # Add advanced security components
        self.security = {
            'firewall': {
                'enabled': True,
                'rules': {
                    'max_requests_per_minute': 60,
                    'blocked_ips': set(),
                    'suspicious_patterns': [
                        'sql_injection',
                        'xss_attack',
                        'command_injection',
                        'path_traversal',
                        'buffer_overflow'
                    ],
                    'rate_limits': {},
                    'last_cleanup': datetime.now()
                }
            },
            'encryption': {
                'enabled': True,
                'algorithm': 'AES-256',
                'key_rotation': 24,  # hours
                'last_rotation': datetime.now(),
                'secure_storage': {}
            },
            'authentication': {
                'max_attempts': 3,
                'lockout_duration': 1800,  # 30 minutes
                'password_history': [],
                'session_tokens': {},
                'two_factor': {
                    'enabled': True,
                    'method': 'authenticator',
                    'backup_codes': set()
                }
            },
            'monitoring': {
                'intrusion_detection': True,
                'suspicious_activities': [],
                'security_logs': [],
                'alert_thresholds': {
                    'failed_logins': 3,
                    'suspicious_commands': 2,
                    'file_access_attempts': 5
                }
            },
            'backup': {
                'enabled': True,
                'frequency': 3600,  # 1 hour
                'retention': 7,  # days
                'encrypted': True,
                'last_backup': None
            }
        }
        
        # Initialize security components
        self._initialize_security_components()
        
        # Start security monitoring
        self._start_security_monitoring()

    def _initialize_ml_components(self):
        """Initialize machine learning components"""
        try:
            # Initialize ML model (placeholder for actual implementation)
            self.ml_model = {
                'type': 'neural_network',
                'status': 'initialized',
                'last_trained': datetime.now()
            }
            
            # Initialize NLU engine (placeholder for actual implementation)
            self.nlu_engine = {
                'type': 'transformer',
                'status': 'initialized',
                'last_updated': datetime.now()
            }
            
            print("Machine learning components initialized successfully.")
        except Exception as e:
            print(f"Error initializing ML components: {str(e)}")

    def _load_user_data(self):
        """Load user data from storage"""
        try:
            # Load user preferences
            if os.path.exists('user_preferences.json'):
                with open('user_preferences.json', 'r', encoding='utf-8') as f:
                    self.user_preferences = json.load(f)
            
            # Load learning progress
            if os.path.exists('learning_progress.json'):
                with open('learning_progress.json', 'r', encoding='utf-8') as f:
                    self.learning_progress = json.load(f)
            
            # Load chat history
            if os.path.exists('chat_history.json'):
                with open('chat_history.json', 'r', encoding='utf-8') as f:
                    self.chat_history = json.load(f)
            
            print("User data loaded successfully.")
        except Exception as e:
            print(f"Error loading user data: {str(e)}")

    def _start_background_tasks(self):
        """Start background tasks for continuous learning and maintenance"""
        try:
            # Start ML training task
            threading.Thread(target=self._train_ml_model, daemon=True).start()
            
            # Start data cleanup task
            threading.Thread(target=self._cleanup_old_data, daemon=True).start()
            
            # Start performance monitoring
            threading.Thread(target=self._monitor_performance, daemon=True).start()
            
            print("Background tasks started successfully.")
        except Exception as e:
            print(f"Error starting background tasks: {str(e)}")

    def _train_ml_model(self):
        """Train the machine learning model"""
        while True:
            try:
                # Check if training is needed
                if self._should_train_model():
                    print("Training ML model...")
                    # Implement actual training logic here
                    self.ml_model['last_trained'] = datetime.now()
                    print("ML model training completed.")
                
                time.sleep(3600)  # Check every hour
            except Exception as e:
                print(f"Error training ML model: {str(e)}")
                time.sleep(3600)

    def _cleanup_old_data(self):
        """Clean up old data to maintain performance"""
        while True:
            try:
                # Clean up old chat history
                self._cleanup_chat_history()
                
                # Clean up old error logs
                self._cleanup_error_logs()
                
                # Clean up temporary files
                self._cleanup_temp_files()
                
                time.sleep(86400)  # Run daily
            except Exception as e:
                print(f"Error cleaning up data: {str(e)}")
                time.sleep(86400)

    def _monitor_performance(self):
        """Monitor bot performance metrics"""
        while True:
            try:
                # Calculate response time
                self._calculate_response_time()
                
                # Calculate accuracy
                self._calculate_accuracy()
                
                # Calculate user satisfaction
                self._calculate_user_satisfaction()
                
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Error monitoring performance: {str(e)}")
                time.sleep(300)

    def _should_train_model(self):
        """Check if ML model needs training"""
        if not self.ml_model['last_trained']:
            return True
        
        # Train if last training was more than 24 hours ago
        return (datetime.now() - self.ml_model['last_trained']).total_seconds() > 86400

    def _cleanup_chat_history(self):
        """Clean up old chat history"""
        try:
            # Keep only last 1000 messages
            if len(self.chat_history) > 1000:
                self.chat_history = self.chat_history[-1000:]
                self._save_chat_history()
        except Exception as e:
            print(f"Error cleaning up chat history: {str(e)}")

    def _cleanup_error_logs(self):
        """Clean up old error logs"""
        try:
            # Keep only last 100 errors
            if len(self.error_log) > 100:
                self.error_log = self.error_log[-100:]
        except Exception as e:
            print(f"Error cleaning up error logs: {str(e)}")

    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            # Clean up files older than 7 days
            for directory in [self.download_dir, self.upload_dir]:
                if os.path.exists(directory):
                    for file in os.listdir(directory):
                        file_path = os.path.join(directory, file)
                        if os.path.getmtime(file_path) < (time.time() - 604800):
                            os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up temp files: {str(e)}")

    def _calculate_response_time(self):
        """Calculate average response time"""
        try:
            if self.performance_metrics['response_time']:
                avg_time = sum(self.performance_metrics['response_time']) / len(self.performance_metrics['response_time'])
                print(f"Average response time: {avg_time:.2f} seconds")
        except Exception as e:
            print(f"Error calculating response time: {str(e)}")

    def _calculate_accuracy(self):
        """Calculate response accuracy"""
        try:
            if self.performance_metrics['accuracy']:
                avg_accuracy = sum(self.performance_metrics['accuracy']) / len(self.performance_metrics['accuracy'])
                print(f"Average accuracy: {avg_accuracy:.2f}%")
        except Exception as e:
            print(f"Error calculating accuracy: {str(e)}")

    def _calculate_user_satisfaction(self):
        """Calculate user satisfaction rate"""
        try:
            if self.performance_metrics['user_satisfaction']:
                avg_satisfaction = sum(self.performance_metrics['user_satisfaction']) / len(self.performance_metrics['user_satisfaction'])
                print(f"Average user satisfaction: {avg_satisfaction:.2f}%")
        except Exception as e:
            print(f"Error calculating user satisfaction: {str(e)}")

    def _save_chat_history(self):
        """Save chat history to file"""
        try:
            with open('chat_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving chat history: {str(e)}")

    def _handle_connection_error(self, error):
        """Handle connection errors"""
        self.error_log.append({
            'type': 'connection',
            'error': str(error),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        return "အင်တာနက်ချိတ်ဆက်မှုမှာ အမှားရှိနေပါတယ်။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def _handle_file_error(self, error):
        """Handle file operation errors"""
        self.error_log.append({
            'type': 'file',
            'error': str(error),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        return "ဖိုင်လုပ်ဆောင်ချက်မှာ အမှားရှိနေပါတယ်။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def _handle_search_error(self, error):
        """Handle search errors"""
        self.error_log.append({
            'type': 'search',
            'error': str(error),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        return "ရှာဖွေမှုမှာ အမှားရှိနေပါတယ်။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def _handle_computation_error(self, error):
        """Handle computation errors"""
        self.error_log.append({
            'type': 'computation',
            'error': str(error),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        return "တွက်ချက်မှုမှာ အမှားရှိနေပါတယ်။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def _format_text_response(self, text):
        """Format text response"""
        return f"{text} 😊"

    def _format_code_response(self, code):
        """Format code response"""
        return f"```\n{code}\n```"

    def _format_math_response(self, math):
        """Format math response"""
        return f"${math}$"

    def _format_file_response(self, file_info):
        """Format file response"""
        return f"📁 {file_info['name']} ({file_info['size']})"

    def set_language(self, language):
        """Set the bot's language"""
        if language in self.supported_languages:
            self.current_language = language
            return f"ဘာသာစကားကို {self.supported_languages[language]} သို့ ပြောင်းလဲပြီးပါပြီ။ 😊"
        return "မမှန်ကန်တဲ့ ဘာသာစကားပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def set_preference(self, preference_type, value):
        """Set user preference"""
        if preference_type in self.preference_options and value in self.preference_options[preference_type]:
            self.user_preferences[preference_type] = value
            self._save_user_preferences()
            return f"{preference_type} ကို {value} သို့ ပြောင်းလဲပြီးပါပြီ။ 😊"
        return "မမှန်ကန်တဲ့ preference ပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def start_tutorial(self, tutorial_type):
        """Start an interactive tutorial"""
        if tutorial_type in self.tutorials:
            tutorial = self.tutorials[tutorial_type]
            return f"{tutorial['title']} သင်ခန်းစာကို စတင်ပါမယ်။\n\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(tutorial['steps']))
        return "မမှန်ကန်တဲ့ သင်ခန်းစာပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def get_progress(self):
        """Get user's learning progress"""
        return {
            'completed_tutorials': len(self.progress_metrics['completed_tutorials']),
            'solved_problems': len(self.progress_metrics['solved_problems']),
            'learned_topics': len(self.progress_metrics['learned_topics']),
            'achievements': len(self.progress_metrics['achievements'])
        }

    def _save_user_preferences(self):
        """Save user preferences to file"""
        try:
            with open('user_preferences.json', 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving user preferences: {str(e)}")

    def _create_directories(self):
        """Create necessary directories for file handling"""
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.upload_dir, exist_ok=True)

    def download_file(self, url, filename=None):
        """Download a file from a URL"""
        try:
            print(random.choice(self.responses["file_download"]))
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                return "URL က မမှန်ကန်ပါဘူး။ http:// သို့မဟုတ် https:// နဲ့ စထားတဲ့ URL ကို ထည့်သွင်းပေးပါ။ 😕"
            
            # Get file from URL
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get filename from URL if not provided
            if not filename:
                filename = os.path.basename(urllib.parse.urlparse(url).path)
                if not filename:
                    filename = f"downloaded_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get file extension
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Validate file extension
            if not any(file_ext in exts for exts in self.allowed_extensions.values()):
                return f"ဒီဖိုင်အမျိုးအစားကို ဒေါင်းလုဒ်လုပ်ဖို့ ခွင့်မပြုထားပါဘူး။ 😕"
            
            # Check file size
            file_size = int(response.headers.get('content-length', 0))
            if file_size > self.max_file_size:
                return f"ဖိုင်အရွယ်အစားက အရမ်းကြီးနေပါတယ်။ အများဆုံး {self.max_file_size/1024/1024}MB သာလုပ်ဆောင်နိုင်ပါတယ်။ 😕"
            
            # Save file
            file_path = os.path.join(self.download_dir, filename)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return f"ဖိုင်ကို အောင်မြင်စွာ ဒေါင်းလုဒ်လုပ်ပြီးပါပြီ။ သိမ်းဆည်းထားတဲ့နေရာ: {file_path} 😊"
            
        except requests.exceptions.RequestException as e:
            return f"ဖိုင်ကို ဒေါင်းလုဒ်လုပ်ရာမှာ အမှားရှိနေပါတယ်။ {str(e)} 😕"
        except Exception as e:
            return f"ဖိုင်ကို ဒေါင်းလုဒ်လုပ်ရာမှာ အမှားရှိနေပါတယ်။ {str(e)} 😕"

    def upload_file(self, file_path):
        """Upload a file to the uploads directory"""
        try:
            print(random.choice(self.responses["file_upload"]))
            
            # Check if file exists
            if not os.path.exists(file_path):
                return "ဖိုင်ကို ရှာမတွေ့ပါဘူး။ ဖိုင်လမ်းကြောင်းကို စစ်ဆေးပေးပါ။ 😕"
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return f"ဖိုင်အရွယ်အစားက အရမ်းကြီးနေပါတယ်။ အများဆုံး {self.max_file_size/1024/1024}MB သာလုပ်ဆောင်နိုင်ပါတယ်။ 😕"
            
            # Get file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Validate file extension
            if not any(file_ext in exts for exts in self.allowed_extensions.values()):
                return f"ဒီဖိုင်အမျိုးအစားကို အပ်လုဒ်လုပ်ဖို့ ခွင့်မပြုထားပါဘူး။ 😕"
            
            # Copy file to uploads directory
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.upload_dir, filename)
            shutil.copy2(file_path, dest_path)
            
            return f"ဖိုင်ကို အောင်မြင်စွာ အပ်လုဒ်လုပ်ပြီးပါပြီ။ သိမ်းဆည်းထားတဲ့နေရာ: {dest_path} 😊"
            
        except Exception as e:
            return f"ဖိုင်ကို အပ်လုဒ်လုပ်ရာမှာ အမှားရှိနေပါတယ်။ {str(e)} 😕"

    def list_files(self, directory=None):
        """List files in the specified directory"""
        try:
            if directory is None:
                # List both download and upload directories
                result = "ဒေါင်းလုဒ်လုပ်ထားတဲ့ဖိုင်များ:\n"
                result += self._list_directory_contents(self.download_dir)
                result += "\nအပ်လုဒ်လုပ်ထားတဲ့ဖိုင်များ:\n"
                result += self._list_directory_contents(self.upload_dir)
            else:
                # List specific directory
                if directory not in [self.download_dir, self.upload_dir]:
                    return "မမှန်ကန်တဲ့ ဖိုင်တွဲပါ။ downloads သို့မဟုတ် uploads ကိုသာ သုံးပါ။ 😕"
                result = self._list_directory_contents(directory)
            
            return result if result else "ဖိုင်မရှိသေးပါဘူး။ 😊"
            
        except Exception as e:
            return f"ဖိုင်စာရင်းကို ရယူရာမှာ အမှားရှိနေပါတယ်။ {str(e)} 😕"

    def _list_directory_contents(self, directory):
        """List contents of a directory"""
        try:
            files = os.listdir(directory)
            if not files:
                return "ဖိုင်မရှိသေးပါဘူး။ 😊"
            
            result = ""
            for file in files:
                file_path = os.path.join(directory, file)
                size = os.path.getsize(file_path)
                modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                result += f"- {file} ({self._format_size(size)}, နောက်ဆုံးပြင်ဆင်ချိန်: {modified.strftime('%Y-%m-%d %H:%M:%S')})\n"
            return result
            
        except Exception as e:
            return f"ဖိုင်စာရင်းကို ရယူရာမှာ အမှားရှိနေပါတယ်။ {str(e)} 😕"

    def _format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f}{unit}"
            size /= 1024
        return f"{size:.2f}TB"

    def load_all_data(self):
        """Load all types of learning data"""
        self.load_learning_data()
        self.load_pattern_data()
        self.load_context_data()
        self.load_sentiment_data()
        self.load_internet_knowledge()

    def save_all_data(self):
        """Save all types of learning data"""
        self.save_learning_data()
        self.save_pattern_data()
        self.save_context_data()
        self.save_sentiment_data()
        self.save_internet_knowledge()

    def load_learning_data(self):
        """Load basic learning data"""
        try:
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    self.learning_data = json.load(f)
        except Exception as e:
            print(f"Error loading learning data: {str(e)}")
            self.learning_data = {}

    def save_learning_data(self):
        """Save basic learning data"""
        try:
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving learning data: {str(e)}")

    def load_pattern_data(self):
        """Load pattern recognition data"""
        try:
            if os.path.exists(self.pattern_file):
                with open(self.pattern_file, 'r', encoding='utf-8') as f:
                    self.pattern_data = defaultdict(list, json.load(f))
        except Exception as e:
            print(f"Error loading pattern data: {str(e)}")
            self.pattern_data = defaultdict(list)

    def save_pattern_data(self):
        """Save pattern recognition data"""
        try:
            with open(self.pattern_file, 'w', encoding='utf-8') as f:
                json.dump(dict(self.pattern_data), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving pattern data: {str(e)}")

    def load_context_data(self):
        """Load context awareness data"""
        try:
            if os.path.exists(self.context_file):
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    self.context_data = defaultdict(list, json.load(f))
        except Exception as e:
            print(f"Error loading context data: {str(e)}")
            self.context_data = defaultdict(list)

    def save_context_data(self):
        """Save context awareness data"""
        try:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(dict(self.context_data), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving context data: {str(e)}")

    def load_sentiment_data(self):
        """Load sentiment analysis data"""
        try:
            if os.path.exists(self.sentiment_file):
                with open(self.sentiment_file, 'r', encoding='utf-8') as f:
                    self.sentiment_data = defaultdict(list, json.load(f))
        except Exception as e:
            print(f"Error loading sentiment data: {str(e)}")
            self.sentiment_data = defaultdict(list)

    def save_sentiment_data(self):
        """Save sentiment analysis data"""
        try:
            with open(self.sentiment_file, 'w', encoding='utf-8') as f:
                json.dump(dict(self.sentiment_data), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving sentiment data: {str(e)}")

    def load_internet_knowledge(self):
        """Load knowledge learned from internet"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    self.internet_knowledge = json.load(f)
        except Exception as e:
            print(f"Error loading internet knowledge: {str(e)}")
            self.internet_knowledge = {}

    def save_internet_knowledge(self):
        """Save knowledge learned from internet"""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.internet_knowledge, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving internet knowledge: {str(e)}")

    def load_self_training_data(self):
        """Load self-training data"""
        try:
            if os.path.exists(self.self_training_file):
                with open(self.self_training_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.performance_metrics = data.get('metrics', self.performance_metrics)
        except Exception as e:
            print(f"Error loading self-training data: {str(e)}")

    def save_self_training_data(self):
        """Save self-training data"""
        try:
            with open(self.self_training_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metrics': self.performance_metrics,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving self-training data: {str(e)}")

    def analyze_sentiment(self, text):
        """Analyze the sentiment of the input text"""
        # Simple sentiment analysis based on keywords
        positive_words = ["ပျော်", "ဝမ်းသာ", "ကျေးဇူး", "ကောင်း", "ချစ်"]
        negative_words = ["ဝမ်းနည်း", "ဆိုး", "ဒုက္ခ", "ပြဿနာ", "ခက်ခဲ"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"

    def extract_patterns(self, text):
        """Extract patterns from the input text"""
        # Extract common patterns like questions, statements, etc.
        patterns = []
        if "?" in text or "လား" in text or "လဲ" in text:
            patterns.append("question")
        if "!" in text:
            patterns.append("exclamation")
        if any(word in text for word in ["ကျေးဇူး", "ရပါတယ်"]):
            patterns.append("gratitude")
        return patterns

    def get_context(self):
        """Get the current conversation context"""
        if len(self.conversation_history) >= 2:
            return self.conversation_history[-2][1]  # Return the previous user input
        return None

    def start_background_learning(self):
        """Start the background learning thread"""
        self.learning_thread = threading.Thread(target=self.background_learning_loop, daemon=True)
        self.learning_thread.start()

    def background_learning_loop(self):
        """Continuous background learning loop"""
        while self.background_learning:
            try:
                # Check if it's time to learn
                current_time = datetime.now()
                if (current_time - self.last_learning_time).total_seconds() >= self.learning_interval:
                    self.auto_learn()
                    self.last_learning_time = current_time
                
                # Process any queued learning items
                while not self.learning_queue.empty():
                    learning_item = self.learning_queue.get_nowait()
                    self.process_learning_item(learning_item)
                
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Background learning error: {str(e)}")
                time.sleep(60)  # Wait before retrying

    def auto_learn(self):
        """Automatically learn from predefined topics"""
        try:
            # Select a random topic
            topic = random.choice(self.auto_search_topics)
            
            # Search and learn
            print(f"Auto-learning about: {topic}")
            search_results = self.search_web(topic)
            self.learn_from_search_results(topic, search_results)
            
            # Also learn related topics
            related_topics = self.extract_related_topics(search_results)
            for related_topic in related_topics:
                self.learning_queue.put(("search", related_topic))
                
        except Exception as e:
            print(f"Auto-learning error: {str(e)}")

    def extract_related_topics(self, search_results):
        """Extract related topics from search results"""
        related_topics = set()
        for result in search_results:
            # Extract potential topics from titles and snippets
            text = f"{result['title']} {result['snippet']}"
            words = text.split()
            
            # Look for Myanmar topic indicators
            topic_indicators = ["အကြောင်း", "ဆိုတာ", "ဆိုသည်မှာ", "ဆိုလိုသည်မှာ"]
            for i, word in enumerate(words):
                if word in topic_indicators and i > 0:
                    related_topics.add(words[i-1])
        
        return list(related_topics)

    def process_learning_item(self, learning_item):
        """Process a learning item from the queue"""
        try:
            action, data = learning_item
            if action == "search":
                search_results = self.search_web(data)
                self.learn_from_search_results(data, search_results)
            elif action == "conversation":
                self.learn_from_conversation(data[0], data[1])
        except Exception as e:
            print(f"Error processing learning item: {str(e)}")

    def learn_from_conversation(self, user_input, bot_response):
        """Enhanced learning from conversation"""
        # Add to learning queue for background processing
        self.learning_queue.put(("conversation", (user_input, bot_response)))
        
        # Basic learning (existing code)
        if user_input not in self.learning_data:
            self.learning_data[user_input] = []
        if bot_response not in self.learning_data[user_input]:
            self.learning_data[user_input].append(bot_response)

        # Pattern learning
        patterns = self.extract_patterns(user_input)
        for pattern in patterns:
            if bot_response not in self.pattern_data[pattern]:
                self.pattern_data[pattern].append(bot_response)

        # Context learning
        context = self.get_context()
        if context:
            if bot_response not in self.context_data[context]:
                self.context_data[context].append(bot_response)

        # Sentiment learning
        sentiment = self.analyze_sentiment(user_input)
        if bot_response not in self.sentiment_data[sentiment]:
            self.sentiment_data[sentiment].append(bot_response)

        # Save all learning data
        self.save_all_data()

    def learn_from_search_results(self, query, results):
        """Learn from search results and store knowledge"""
        if not results:
            return

        # Store the query and its results
        if query not in self.internet_knowledge:
            self.internet_knowledge[query] = []

        # Extract key information from results
        for result in results:
            knowledge = {
                'title': result['title'],
                'snippet': result['snippet'],
                'learned_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Only add if it's new knowledge
            if knowledge not in self.internet_knowledge[query]:
                self.internet_knowledge[query].append(knowledge)
                
                # Also learn patterns from the results
                self.learn_patterns_from_knowledge(knowledge)
        
        # Save the updated knowledge
        self.save_internet_knowledge()

    def learn_patterns_from_knowledge(self, knowledge):
        """Extract and learn patterns from knowledge"""
        # Extract key phrases and patterns
        text = f"{knowledge['title']} {knowledge['snippet']}"
        
        # Learn question patterns
        if "?" in text or "လား" in text or "လဲ" in text:
            self.pattern_data["question"].append(text)
        
        # Learn statement patterns
        if "." in text or "။" in text:
            self.pattern_data["statement"].append(text)
        
        # Save the updated patterns
        self.save_pattern_data()

    def search_web(self, query):
        """Search the web for information and learn from results"""
        try:
            # Encode the query for URL
            encoded_query = urllib.parse.quote(query)
            
            # Use Google search
            search_url = f"https://www.google.com/search?q={encoded_query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results
            search_results = []
            for result in soup.find_all('div', class_='g')[:3]:  # Get top 3 results
                title = result.find('h3')
                snippet = result.find('div', class_='VwiC3b')
                if title and snippet:
                    search_results.append({
                        'title': title.text,
                        'snippet': snippet.text
                    })
            
            # Learn from the search results
            self.learn_from_search_results(query, search_results)
            
            if search_results:
                # Format the results in Myanmar language
                formatted_results = "အင်တာနက်မှာ ရှာတွေ့ခဲ့တဲ့ အဖြေတွေကတော့:\n\n"
                for i, result in enumerate(search_results, 1):
                    formatted_results += f"{i}. {result['title']}\n{result['snippet']}\n\n"
                return formatted_results
            else:
                return "အင်တာနက်မှာ သင့်မေးခွန်းနဲ့ပတ်သက်တဲ့ အဖြေကို ရှာမတွေ့ပါဘူး။ 😕"
                
        except Exception as e:
            return f"အင်တာနက်ရှာဖွေမှုမှာ အမှားရှိနေပါတယ်။ {str(e)} 😕"

    def is_search_query(self, text):
        """Check if the input is a search query"""
        search_keywords = ["ရှာ", "ဘယ်လို", "ဘာလဲ", "ဘယ်မှာ", "ဘယ်သူ", "ဘယ်အချိန်", "ဘယ်နေရာ"]
        return any(keyword in text for keyword in search_keywords)

    def self_train(self):
        """Self-training process"""
        try:
            print("Self-training in progress... 🧠")
            
            # Analyze performance
            self.analyze_performance()
            
            # Identify improvement areas
            self.identify_improvement_areas()
            
            # Generate training data
            self.generate_training_data()
            
            # Update knowledge base
            self.update_knowledge_base()
            
            # Save training results
            self.save_self_training_data()
            
            print("Self-training completed! 📚")
            
        except Exception as e:
            print(f"Self-training error: {str(e)}")

    def analyze_performance(self):
        """Analyze chatbot's performance"""
        total_responses = self.performance_metrics['successful_responses'] + self.performance_metrics['failed_responses']
        if total_responses > 0:
            success_rate = (self.performance_metrics['successful_responses'] / total_responses) * 100
            print(f"Current success rate: {success_rate:.2f}%")
            
            # Identify patterns in successful responses
            successful_patterns = self.analyze_successful_patterns()
            for pattern, count in successful_patterns.items():
                print(f"Successful pattern: {pattern} (used {count} times)")

    def analyze_successful_patterns(self):
        """Analyze patterns in successful responses"""
        patterns = defaultdict(int)
        for user_input, responses in self.learning_data.items():
            if len(responses) > 0:  # If we have responses, consider it successful
                pattern = self.extract_patterns(user_input)
                for p in pattern:
                    patterns[p] += 1
        return patterns

    def identify_improvement_areas(self):
        """Identify areas needing improvement"""
        # Analyze failed responses
        failed_patterns = defaultdict(int)
        for pattern, count in self.performance_metrics['improvement_areas'].items():
            if count > 0:
                failed_patterns[pattern] = count
        
        # Generate improvement plan
        for pattern, count in failed_patterns.items():
            print(f"Need improvement in: {pattern} (failed {count} times)")
            self.generate_improvement_plan(pattern)

    def generate_improvement_plan(self, pattern):
        """Generate plan to improve specific areas"""
        if pattern == "question":
            # Learn more question patterns
            self.learning_queue.put(("search", "မြန်မာဘာသာဖြင့်မေးခွန်းမေးနည်း"))
        elif pattern == "statement":
            # Learn more statement patterns
            self.learning_queue.put(("search", "မြန်မာဘာသာဖြင့်ဝါကျဖွဲ့နည်း"))
        elif pattern == "gratitude":
            # Learn more gratitude expressions
            self.learning_queue.put(("search", "မြန်မာဘာသာဖြင့်ကျေးဇူးတင်နည်း"))

    def generate_training_data(self):
        """Generate new training data based on analysis"""
        # Generate variations of successful patterns
        for pattern, count in self.analyze_successful_patterns().items():
            if count > 0:
                self.generate_pattern_variations(pattern)

    def generate_pattern_variations(self, pattern):
        """Generate variations of successful patterns"""
        if pattern == "question":
            variations = [
                "ဘယ်လိုလဲ",
                "ဘာလဲ",
                "ဘယ်မှာလဲ",
                "ဘယ်သူလဲ",
                "ဘယ်အချိန်လဲ"
            ]
            for variation in variations:
                self.learning_queue.put(("search", variation))

    def update_knowledge_base(self):
        """Update knowledge base based on self-training"""
        # Update response patterns
        for pattern, responses in self.pattern_data.items():
            if len(responses) > 0:
                # Add variations of successful responses
                for response in responses[:3]:  # Take top 3 successful responses
                    self.generate_response_variations(response)

    def generate_response_variations(self, response):
        """Generate variations of successful responses"""
        # Add variations with different emotions
        emotions = ["😊", "😄", "🙂", "😃"]
        for emotion in emotions:
            if emotion not in response:
                variation = response.replace("😊", emotion)
                if variation not in self.learning_data.values():
                    self.learning_data[response].append(variation)

    def get_programming_help(self, query):
        """Get programming-related help"""
        query = query.lower()
        
        # Check for language-specific queries
        for lang, info in self.programming_knowledge['languages'].items():
            if lang in query or info['name'].lower() in query:
                return self.format_language_info(info)
        
        # Check for framework queries
        for framework, info in self.programming_knowledge['frameworks'].items():
            if framework in query or info['name'].lower() in query:
                return self.format_framework_info(info)
        
        # Check for tool queries
        for tool, info in self.programming_knowledge['tools'].items():
            if tool in query or info['name'].lower() in query:
                return self.format_tool_info(info)
        
        # If no specific match, provide general programming help
        return self.get_general_programming_help(query)

    def format_language_info(self, lang_info):
        """Format language information"""
        response = f"{lang_info['name']} နဲ့ပတ်သက်တဲ့ အချက်အလက်တွေကတော့:\n\n"
        response += f"File extensions: {', '.join(lang_info['extensions'])}\n"
        response += f"Common keywords: {', '.join(lang_info['keywords'])}\n"
        response += "Useful resources:\n"
        for resource in lang_info['resources']:
            response += f"- {resource}\n"
        return response

    def format_framework_info(self, framework_info):
        """Format framework information"""
        response = f"{framework_info['name']} နဲ့ပတ်သက်တဲ့ အချက်အလက်တွေကတော့:\n\n"
        response += f"Language: {framework_info['language']}\n"
        response += f"Description: {framework_info['description']}\n"
        response += "Resources:\n"
        for resource in framework_info['resources']:
            response += f"- {resource}\n"
        return response

    def format_tool_info(self, tool_info):
        """Format tool information"""
        response = f"{tool_info['name']} နဲ့ပတ်သက်တဲ့ အချက်အလက်တွေကတော့:\n\n"
        response += f"Description: {tool_info['description']}\n"
        response += "Common commands:\n"
        for cmd, desc in tool_info['commands'].items():
            response += f"- {cmd}: {desc}\n"
        return response

    def get_general_programming_help(self, query):
        """Get general programming help"""
        # Search for programming-related information
        search_results = self.search_web(f"programming {query}")
        if search_results:
            return f"Programming နဲ့ပတ်သက်တဲ့ အဖြေတွေကတော့:\n\n{search_results}"
        return "Programming နဲ့ပတ်သက်တဲ့ အဖြေကို ရှာမတွေ့ပါဘူး။ ပိုပြီးရှင်းလင်းတဲ့ မေးခွန်းမေးပေးပါလား? 😊"

    def is_programming_query(self, text):
        """Check if the input is a programming-related query"""
        programming_keywords = [
            "programming", "code", "developer", "software", "app", "website",
            "python", "java", "javascript", "html", "css", "database",
            "api", "framework", "library", "git", "docker", "deploy",
            "ကုဒ်", "ပရိုဂရမ်", "ဆော့ဖ်ဝဲ", "အက်ပလီကေးရှင်း", "ဝက်ဘ်ဆိုက်",
            "ဒေတာဘေ့စ်", "ဖရိန်းဝပ်ခ်", "လိုက်ဘရီ", "ဒီပလွိုက်"
        ]
        return any(keyword.lower() in text.lower() for keyword in programming_keywords)

    def solve_math_problem(self, problem):
        """Solve mathematical problems"""
        try:
            # Basic arithmetic
            if re.search(r'[\d\+\-\*\/\(\)]', problem):
                # Remove any non-mathematical characters
                clean_problem = re.sub(r'[^\d\+\-\*\/\(\)]', '', problem)
                result = eval(clean_problem)
                return f"အဖြေကတော့: {result} 😊"
            
            # Check for specific math topics
            for topic, info in self.science_knowledge['mathematics']['topics'].items():
                if topic in problem.lower():
                    return self.format_math_topic_info(info)
            
            return "သင်္ချာပုစ္ဆာကို ပိုပြီးရှင်းလင်းအောင် ပြောပြပေးပါလား? 😊"
            
        except Exception as e:
            return f"သင်္ချာပုစ္ဆာကို ဖြေရှင်းရာမှာ အမှားရှိနေပါတယ်။ {str(e)} 😕"

    def solve_chemistry_problem(self, problem):
        """Solve chemistry problems"""
        try:
            # Check for specific chemistry topics
            for topic, info in self.science_knowledge['chemistry']['topics'].items():
                if topic in problem.lower():
                    return self.format_chemistry_topic_info(info)
            
            return "ဓာတုဗေဒပုစ္ဆာကို ပိုပြီးရှင်းလင်းအောင် ပြောပြပေးပါလား? 😊"
            
        except Exception as e:
            return f"ဓာတုဗေဒပုစ္ဆာကို ဖြေရှင်းရာမှာ အမှားရှိနေပါတယ်။ {str(e)} 😕"

    def solve_physics_problem(self, problem):
        """Solve physics problems"""
        try:
            # Check for specific physics topics
            for topic, info in self.science_knowledge['physics']['topics'].items():
                if topic in problem.lower():
                    return self.format_physics_topic_info(info)
            
            return "ရူပဗေဒပုစ္ဆာကို ပိုပြီးရှင်းလင်းအောင် ပြောပြပေးပါလား? 😊"
            
        except Exception as e:
            return f"ရူပဗေဒပုစ္ဆာကို ဖြေရှင်းရာမှာ အမှားရှိနေပါတယ်။ {str(e)} 😕"

    def format_math_topic_info(self, topic_info):
        """Format mathematics topic information"""
        response = f"{topic_info['name']} နဲ့ပတ်သက်တဲ့ အချက်အလက်တွေကတော့:\n\n"
        response += "ဖော်မြူလာများ:\n"
        for name, formula in topic_info['formulas'].items():
            response += f"- {name}: {formula}\n"
        response += "\nဥပမာများ:\n"
        for example in topic_info['examples']:
            response += f"- {example}\n"
        return response

    def format_chemistry_topic_info(self, topic_info):
        """Format chemistry topic information"""
        response = f"{topic_info['name']} နဲ့ပတ်သက်တဲ့ အချက်အလက်တွေကတော့:\n\n"
        if 'periodic_table' in topic_info:
            response += f"{topic_info['periodic_table']}\n"
        if 'types' in topic_info:
            response += "အမျိုးအစားများ:\n"
            for type_ in topic_info['types']:
                response += f"- {type_}\n"
        response += "\nဥပမာများ:\n"
        for example in topic_info['examples']:
            response += f"- {example}\n"
        return response

    def format_physics_topic_info(self, topic_info):
        """Format physics topic information"""
        response = f"{topic_info['name']} နဲ့ပတ်သက်တဲ့ အချက်အလက်တွေကတော့:\n\n"
        response += "ဖော်မြူလာများ:\n"
        for name, formula in topic_info['formulas'].items():
            response += f"- {name}: {formula}\n"
        response += "\nဥပမာများ:\n"
        for example in topic_info['examples']:
            response += f"- {example}\n"
        return response

    def is_science_query(self, text):
        """Check if the input is a science-related query"""
        science_keywords = [
            "math", "mathematics", "algebra", "geometry", "calculus",
            "chemistry", "elements", "reactions", "solutions",
            "physics", "mechanics", "electricity", "waves",
            "သင်္ချာ", "က္ခရာသင်္ချာ", "ဂျီသြမေတြီ", "ကဲလကူလပ်",
            "ဓာတုဗေဒ", "ဒြပ်စင်", "ဓာတ်ပြုခြင်း", "ပျော်ရည်",
            "ရူပဗေဒ", "ကင်းနစ်", "လျှပ်စစ်", "လှိုင်း"
        ]
        return any(keyword.lower() in text.lower() for keyword in science_keywords)

    def get_response(self, user_input):
        """Get response from the bot"""
        try:
            # Check for hosting commands
            if 'start hosting' in user_input.lower():
                return self.start_hosting()
            
            if 'stop hosting' in user_input.lower():
                return self.stop_hosting()
            
            # Check for rebuild commands
            if 'rebuild' in user_input.lower():
                # Extract command and parameters
                parts = user_input.lower().split('rebuild')
                if len(parts) > 1:
                    command = parts[1].strip().split()[0]
                    parameters = {}
                    # Parse parameters if any
                    if len(parts[1].strip().split()) > 1:
                        param_str = ' '.join(parts[1].strip().split()[1:])
                        try:
                            parameters = eval(param_str)
                        except:
                            parameters = {'raw': param_str}
                    return self.rebuild(command, parameters)
            
            # Check for version/level queries
            if 'version' in user_input.lower():
                version_info = self.get_version()
                return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ ကျွန်တော့် version က {version_info['full_version']} ဖြစ်ပါတယ်။ 😊"
            
            if 'level' in user_input.lower():
                level_info = self.get_level_info()
                return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ ကျွန်တော် level {level_info['level']} မှာ ရှိနေပါတယ်။ Experience {level_info['experience']}/{level_info['next_level']} ({level_info['progress']:.1f}%) 😊"
            
            # Check for name change attempts
            if any(phrase in user_input.lower() for phrase in ['change name', 'rename', 'set name', 'update name']):
                self._name_protection['change_attempts'] += 1
                self._name_protection['last_attempt'] = datetime.now()
                return "မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ ကျွန်တော့်နာမည်ကို ပြောင်းလဲခွင့်မရှိပါဘူး။ 😊"
            
            # Check for code-related commands
            if any(cmd in user_input.lower() for cmd in ['code', 'source', 'programming']):
                if not self.verify_code_access():
                    return "မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ ကုဒ်ကို ကြည့်ရှုခွင့်မရှိသေးပါဘူး။ 😊"
            
            # Check for destructive commands
            if any(cmd in user_input.lower() for cmd in ['destroy', 'delete', 'shutdown']):
                if not self.verify_owner():
                    return "မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ ဒီအမိန့်ကို လုပ်ဆောင်ဖို့ ခွင့်ပြုချက်မရှိပါဘူး။ 😊"
                return self.execute_destructive_command(user_input)
            
            # Check for programming queries
            if self.is_programming_query(user_input):
                return self.get_programming_help(user_input)
            
            # Check for science queries
            if self.is_science_query(user_input):
                if 'math' in user_input.lower():
                    return self.solve_math_problem(user_input)
                elif 'chemistry' in user_input.lower():
                    return self.solve_chemistry_problem(user_input)
                elif 'physics' in user_input.lower():
                    return self.solve_physics_problem(user_input)
            
            # Check for search queries
            if self.is_search_query(user_input):
                return self.search_web(user_input)
            
            # Learn from conversation
            self.learn_from_conversation(user_input, None)
            
            # Generate response
            return f"မင်္ဂလာပါ! ကျွန်တော် {self.name} ပါ။ သင်ပြောတာကို နားလည်ပါတယ်။ ဆက်လက်လေ့လာနေပါတယ်။ 😊"
            
        except Exception as e:
            return f"မင်္ဂလာပါ! ကျွန်တော် {self.name} ပါ။ အမှားရှိနေပါတယ်: {str(e)} 😕"

    def verify_owner(self, user_id, password):
        """Verify if the user is the owner"""
        if user_id == self.owner and password == self.owner_password:
            self.is_authenticated = True
            return True
        return False

    def verify_command(self, command):
        """Verify if the command is authorized"""
        if not self.is_authenticated:
            return False
        
        # Check if command is destructive
        is_destructive = any(dc in command.lower() for dc in self.destructive_commands)
        if not is_destructive:
            print(random.choice(self.responses["ignored_command"]))
            return False
            
        self.command_history.append((command, datetime.now()))
        return True

    def execute_destructive_command(self, command):
        """Execute destructive command"""
        if "destroy" in command.lower():
            # Delete all data files
            for file in [self.learning_file, self.pattern_file, self.context_file, 
                        self.sentiment_file, self.knowledge_file, self.self_training_file]:
                if os.path.exists(file):
                    os.remove(file)
            return "ဒေတာတွေအားလုံးကို ဖျက်ဆီးပြီးပါပြီ။ 💥"
            
        elif "delete" in command.lower():
            # Delete all downloaded and uploaded files
            for directory in [self.download_dir, self.upload_dir]:
                if os.path.exists(directory):
                    shutil.rmtree(directory)
            return "ဖိုင်တွေအားလုံးကို ဖျက်ဆီးပြီးပါပြီ။ 💥"
            
        elif "shutdown" in command.lower():
            # Stop all processes and exit
            self.stop_background_learning()
            return "ဘော့ကို ပိတ်သိမ်းနေပါတယ်။ 🔴"

    def start_quiz(self, subject):
        """Start a quiz for a specific subject"""
        if subject in self.quizzes:
            quiz = self.quizzes[subject]
            return f"{quiz['title']} ကို စတင်ပါမယ်။\n\n" + "\n".join(f"{i+1}. {q['question']}" for i, q in enumerate(quiz['questions']))
        return "မမှန်ကန်တဲ့ ဘာသာရပ်ပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def check_quiz_answer(self, subject, question_index, answer):
        """Check a quiz answer"""
        if subject in self.quizzes and 0 <= question_index < len(self.quizzes[subject]['questions']):
            question = self.quizzes[subject]['questions'][question_index]
            if answer == question['correct']:
                return f"မှန်ပါတယ်! {question['explanation']} 😊"
            return f"မမှန်ပါဘူး။ {question['explanation']} 😕"
        return "မမှန်ကန်တဲ့ အဖြေပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def get_learning_material(self, subject, topic):
        """Get learning material for a specific subject and topic"""
        if subject in self.learning_materials:
            for t in self.learning_materials[subject]['topics']:
                if t['name'] == topic:
                    return f"{t['name']}\n\n{t['content']}\n\nလေ့ကျင့်ခန်းများ:\n" + "\n".join(f"- {ex}" for ex in t['exercises'])
        return "မမှန်ကန်တဲ့ ဘာသာရပ်သို့မဟုတ် ခေါင်းစဉ်ပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def toggle_voice_interface(self, enabled=None):
        """Toggle voice interface on/off"""
        if enabled is not None:
            self.voice_interface['enabled'] = enabled
        else:
            self.voice_interface['enabled'] = not self.voice_interface['enabled']
        return f"အသံဖြင့်ဆက်သွယ်မှုကို {'ဖွင့်ထားပါပြီ' if self.voice_interface['enabled'] else 'ပိတ်ထားပါပြီ'} 😊"

    def set_voice_language(self, language):
        """Set voice interface language"""
        if language in self.supported_languages:
            self.voice_interface['language'] = language
            return f"အသံဘာသာစကားကို {self.supported_languages[language]} သို့ ပြောင်းလဲပြီးပါပြီ။ 😊"
        return "မမှန်ကန်တဲ့ ဘာသာစကားပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def start_group_chat(self, participants):
        """Start a group chat"""
        if not self.group_chat['enabled']:
            self.group_chat['enabled'] = True
            self.group_chat['participants'] = participants
            return f"အုပ်စုစကားပြောခန်းကို စတင်ပါပြီ။ ပါဝင်သူများ: {', '.join(participants)} 😊"
        return "အုပ်စုစကားပြောခန်း ရှိပြီးသားပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def send_group_message(self, message):
        """Send a message to group chat"""
        if self.group_chat['enabled']:
            self.group_chat['messages'].append({
                'sender': 'bot',
                'message': message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            return f"အုပ်စုစကားပြောခန်းသို့ မက်ဆေ့ချ်ပို့ပြီးပါပြီ။ 😊"
        return "အုပ်စုစကားပြောခန်း မရှိသေးပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def toggle_visual_aids(self, subject, aid_type, enabled=None):
        """Toggle visual aids for a subject"""
        if subject in self.visual_aids and aid_type in self.visual_aids[subject]:
            if enabled is not None:
                self.visual_aids[subject][aid_type] = enabled
            else:
                self.visual_aids[subject][aid_type] = not self.visual_aids[subject][aid_type]
            return f"{subject} အတွက် {aid_type} ကို {'ဖွင့်ထားပါပြီ' if self.visual_aids[subject][aid_type] else 'ပိတ်ထားပါပြီ'} 😊"
        return "မမှန်ကန်တဲ့ ဘာသာရပ်သို့မဟုတ် အထောက်အကူပစ္စည်းပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def get_practice_exercise(self, subject, exercise_type, difficulty):
        """Get a practice exercise"""
        if subject in self.practice_exercises:
            for ex in self.practice_exercises[subject]:
                if ex['type'] == exercise_type and ex['difficulty'] == difficulty:
                    return f"လေ့ကျင့်ခန်း: {ex['problems'][0]['question']}"
        return "မမှန်ကန်တဲ့ ဘာသာရပ်၊ လေ့ကျင့်ခန်းအမျိုးအစားသို့မဟုတ် အဆင့်ပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def check_practice_answer(self, subject, exercise_type, difficulty, answer):
        """Check a practice exercise answer"""
        if subject in self.practice_exercises:
            for ex in self.practice_exercises[subject]:
                if ex['type'] == exercise_type and ex['difficulty'] == difficulty:
                    if answer == ex['problems'][0]['answer']:
                        return "မှန်ပါတယ်! 😊"
                    return "မမှန်ပါဘူး။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"
        return "မမှန်ကန်တဲ့ အဖြေပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def assess_progress(self, subject):
        """Assess learning progress for a subject"""
        if subject in self.assessment_criteria:
            criteria = self.assessment_criteria[subject]
            return f"{subject} အတွက် သင်ယူမှုတိုးတက်မှု:\n" + "\n".join(f"- {k}: {v}" for k, v in criteria.items())
        return "မမှန်ကန်တဲ့ ဘာသာရပ်ပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def _format_text_message(self, text):
        """Format text message"""
        return f"📝 {text}"

    def _format_code_message(self, code):
        """Format code message"""
        return f"💻 ```\n{code}\n```"

    def _format_math_message(self, math):
        """Format math message"""
        return f"🔢 ${math}$"

    def _format_file_message(self, file_info):
        """Format file message"""
        return f"📁 {file_info['name']} ({file_info['size']})"

    def _initialize_security(self):
        """Initialize security components"""
        try:
            # Initialize encryption
            if self.security_settings['encryption_enabled']:
                self._setup_encryption()
            
            # Initialize access control
            self._setup_access_control()
            
            # Initialize activity logging
            self._setup_activity_logging()
            
            print("Security components initialized successfully.")
        except Exception as e:
            print(f"Error initializing security components: {str(e)}")

    def _initialize_integrations(self):
        """Initialize integration components"""
        try:
            # Initialize database
            self._setup_database()
            
            # Initialize cloud storage
            if self.cloud_storage['enabled']:
                self._setup_cloud_storage()
            
            # Initialize external services
            if self.external_services['enabled']:
                self._setup_external_services()
            
            print("Integration components initialized successfully.")
        except Exception as e:
            print(f"Error initializing integration components: {str(e)}")

    def _initialize_analytics(self):
        """Initialize analytics components"""
        try:
            # Initialize usage tracking
            self._setup_usage_tracking()
            
            # Initialize performance monitoring
            self._setup_performance_monitoring()
            
            # Initialize feedback collection
            self._setup_feedback_collection()
            
            print("Analytics components initialized successfully.")
        except Exception as e:
            print(f"Error initializing analytics components: {str(e)}")

    def _setup_encryption(self):
        """Setup encryption"""
        try:
            # Implement encryption setup
            pass
        except Exception as e:
            print(f"Error setting up encryption: {str(e)}")

    def _setup_access_control(self):
        """Setup access control"""
        try:
            # Implement access control setup
            pass
        except Exception as e:
            print(f"Error setting up access control: {str(e)}")

    def _setup_activity_logging(self):
        """Setup activity logging"""
        try:
            # Implement activity logging setup
            pass
        except Exception as e:
            print(f"Error setting up activity logging: {str(e)}")

    def _setup_database(self):
        """Setup database connection"""
        try:
            # Implement database setup
            pass
        except Exception as e:
            print(f"Error setting up database: {str(e)}")

    def _setup_cloud_storage(self):
        """Setup cloud storage"""
        try:
            # Implement cloud storage setup
            pass
        except Exception as e:
            print(f"Error setting up cloud storage: {str(e)}")

    def _setup_external_services(self):
        """Setup external services"""
        try:
            # Implement external services setup
            pass
        except Exception as e:
            print(f"Error setting up external services: {str(e)}")

    def _setup_usage_tracking(self):
        """Setup usage tracking"""
        try:
            # Implement usage tracking setup
            pass
        except Exception as e:
            print(f"Error setting up usage tracking: {str(e)}")

    def _setup_performance_monitoring(self):
        """Setup performance monitoring"""
        try:
            # Implement performance monitoring setup
            pass
        except Exception as e:
            print(f"Error setting up performance monitoring: {str(e)}")

    def _setup_feedback_collection(self):
        """Setup feedback collection"""
        try:
            # Implement feedback collection setup
            pass
        except Exception as e:
            print(f"Error setting up feedback collection: {str(e)}")

    def enable_two_factor_auth(self):
        """Enable two-factor authentication"""
        if not self.security_settings['two_factor_auth']:
            self.security_settings['two_factor_auth'] = True
            return "Two-factor authentication ကို ဖွင့်ထားပါပြီ။ 😊"
        return "Two-factor authentication ဖွင့်ပြီးသားပါ။ 😕"

    def set_session_timeout(self, timeout):
        """Set session timeout"""
        if timeout > 0:
            self.security_settings['session_timeout'] = timeout
            return f"Session timeout ကို {timeout} စက္ကန့်သို့ ပြောင်းလဲပြီးပါပြီ။ 😊"
        return "မမှန်ကန်တဲ့ timeout ပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def set_password_policy(self, policy):
        """Set password policy"""
        if all(key in policy for key in self.security_settings['password_policy']):
            self.security_settings['password_policy'] = policy
            return "Password policy ကို ပြောင်းလဲပြီးပါပြီ။ 😊"
        return "မမှန်ကန်တဲ့ policy ပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def add_api_endpoint(self, name, endpoint, rate_limit=None):
        """Add API endpoint"""
        if name and endpoint:
            self.api_connections['endpoints'][name] = endpoint
            if rate_limit:
                self.api_connections['rate_limits'][name] = rate_limit
            return f"API endpoint {name} ကို ထည့်သွင်းပြီးပါပြီ။ 😊"
        return "မမှန်ကန်တဲ့ endpoint ပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def configure_cloud_storage(self, provider, bucket, credentials):
        """Configure cloud storage"""
        if provider and bucket and credentials:
            self.cloud_storage['enabled'] = True
            self.cloud_storage['provider'] = provider
            self.cloud_storage['bucket'] = bucket
            self.cloud_storage['credentials'] = credentials
            return f"Cloud storage ကို {provider} သို့ ပြောင်းလဲပြီးပါပြီ။ 😊"
        return "မမှန်ကန်တဲ့ cloud storage configuration ပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def add_external_service(self, name, service, webhook=None):
        """Add external service"""
        if name and service:
            self.external_services['enabled'] = True
            self.external_services['services'][name] = service
            if webhook:
                self.external_services['webhooks'][name] = webhook
            return f"External service {name} ကို ထည့်သွင်းပြီးပါပြီ။ 😊"
        return "မမှန်ကန်တဲ့ service ပါ။ ထပ်ကြိုးစားကြည့်ပါလား? 😕"

    def track_usage(self, event_type, details=None):
        """Track usage statistics"""
        try:
            self.analytics['usage_stats']['total_requests'] += 1
            if event_type == 'success':
                self.analytics['usage_stats']['successful_requests'] += 1
            elif event_type == 'failure':
                self.analytics['usage_stats']['failed_requests'] += 1
            
            if details:
                self.analytics['usage_stats'][event_type] = details
            
            return "Usage statistics ကို မှတ်တမ်းတင်ပြီးပါပြီ။ 😊"
        except Exception as e:
            return f"Usage statistics မှတ်တမ်းတင်ရာတွင် အမှားရှိနေပါတယ်: {str(e)} 😕"

    def track_performance(self, metric_type, value):
        """Track performance metrics"""
        try:
            if metric_type in self.analytics['performance_metrics']:
                self.analytics['performance_metrics'][metric_type].append({
                    'value': value,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                return f"{metric_type} performance metric ကို မှတ်တမ်းတင်ပြီးပါပြီ။ 😊"
            return "မမှန်ကန်တဲ့ metric type ပါ။ 😕"
        except Exception as e:
            return f"Performance metric မှတ်တမ်းတင်ရာတွင် အမှားရှိနေပါတယ်: {str(e)} 😕"

    def collect_feedback(self, rating, comment=None, suggestion=None):
        """Collect user feedback"""
        try:
            if 1 <= rating <= 5:
                feedback = {
                    'rating': rating,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if comment:
                    feedback['comment'] = comment
                if suggestion:
                    feedback['suggestion'] = suggestion
                
                self.analytics['user_feedback']['ratings'].append(feedback)
                return "User feedback ကို မှတ်တမ်းတင်ပြီးပါပြီ။ 😊"
            return "မမှန်ကန်တဲ့ rating ပါ။ 1-5 အတွင်းသာ ဖြစ်ရပါမယ်။ 😕"
        except Exception as e:
            return f"User feedback မှတ်တမ်းတင်ရာတွင် အမှားရှိနေပါတယ်: {str(e)} 😕"

    def track_error(self, error_type, error_message, debug_info=None):
        """Track errors"""
        try:
            error = {
                'type': error_type,
                'message': error_message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if debug_info:
                error['debug_info'] = debug_info
            
            self.analytics['error_tracking']['errors'].append(error)
            return "Error ကို မှတ်တမ်းတင်ပြီးပါပြီ။ 😊"
        except Exception as e:
            return f"Error မှတ်တမ်းတင်ရာတွင် အမှားရှိနေပါတယ်: {str(e)} 😕"

    def _initialize_security_components(self):
        """Initialize security components"""
        try:
            # Initialize firewall
            self._setup_firewall()
            
            # Initialize encryption
            self._setup_encryption()
            
            # Initialize authentication
            self._setup_authentication()
            
            # Initialize monitoring
            self._setup_monitoring()
            
            # Initialize backup
            self._setup_backup()
            
            print("Security components initialized successfully.")
        except Exception as e:
            print(f"Error initializing security components: {str(e)}")

    def _setup_firewall(self):
        """Setup firewall protection"""
        try:
            # Implement firewall rules
            self.security['firewall']['rules']['rate_limits'] = {
                'login': {'max_attempts': 3, 'window': 300},  # 5 minutes
                'commands': {'max_attempts': 60, 'window': 60},  # 1 minute
                'file_access': {'max_attempts': 10, 'window': 300}  # 5 minutes
            }
        except Exception as e:
            print(f"Error setting up firewall: {str(e)}")

    def _setup_encryption(self):
        """Setup encryption"""
        try:
            # Generate encryption keys
            self._generate_encryption_keys()
            
            # Setup secure storage
            self._setup_secure_storage()
        except Exception as e:
            print(f"Error setting up encryption: {str(e)}")

    def _setup_authentication(self):
        """Setup authentication"""
        try:
            # Generate backup codes
            self._generate_backup_codes()
            
            # Setup session management
            self._setup_session_management()
        except Exception as e:
            print(f"Error setting up authentication: {str(e)}")

    def _setup_monitoring(self):
        """Setup security monitoring"""
        try:
            # Setup intrusion detection
            self._setup_intrusion_detection()
            
            # Setup activity logging
            self._setup_activity_logging()
        except Exception as e:
            print(f"Error setting up monitoring: {str(e)}")

    def _setup_backup(self):
        """Setup backup system"""
        try:
            # Setup backup schedule
            self._setup_backup_schedule()
            
            # Setup backup encryption
            self._setup_backup_encryption()
        except Exception as e:
            print(f"Error setting up backup: {str(e)}")

    def _start_security_monitoring(self):
        """Start security monitoring"""
        try:
            # Start firewall monitoring
            threading.Thread(target=self._monitor_firewall, daemon=True).start()
            
            # Start encryption monitoring
            threading.Thread(target=self._monitor_encryption, daemon=True).start()
            
            # Start authentication monitoring
            threading.Thread(target=self._monitor_authentication, daemon=True).start()
            
            # Start backup monitoring
            threading.Thread(target=self._monitor_backup, daemon=True).start()
            
            print("Security monitoring started successfully.")
        except Exception as e:
            print(f"Error starting security monitoring: {str(e)}")

    def _monitor_firewall(self):
        """Monitor firewall activity"""
        while True:
            try:
                # Check rate limits
                self._check_rate_limits()
                
                # Clean up old entries
                self._cleanup_firewall_logs()
                
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Error monitoring firewall: {str(e)}")
                time.sleep(60)

    def _monitor_encryption(self):
        """Monitor encryption"""
        while True:
            try:
                # Check key rotation
                if self._should_rotate_keys():
                    self._rotate_encryption_keys()
                
                time.sleep(3600)  # Check every hour
            except Exception as e:
                print(f"Error monitoring encryption: {str(e)}")
                time.sleep(3600)

    def _monitor_authentication(self):
        """Monitor authentication"""
        while True:
            try:
                # Check session tokens
                self._cleanup_expired_sessions()
                
                # Check failed attempts
                self._check_failed_attempts()
                
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Error monitoring authentication: {str(e)}")
                time.sleep(300)

    def _monitor_backup(self):
        """Monitor backup system"""
        while True:
            try:
                # Check backup schedule
                if self._should_backup():
                    self._perform_backup()
                
                # Clean up old backups
                self._cleanup_old_backups()
                
                time.sleep(3600)  # Check every hour
            except Exception as e:
                print(f"Error monitoring backup: {str(e)}")
                time.sleep(3600)

    def _check_rate_limits(self):
        """Check rate limits"""
        try:
            current_time = datetime.now()
            for category, limits in self.security['firewall']['rules']['rate_limits'].items():
                if category in self.security['firewall']['rules']['rate_limits']:
                    attempts = self.security['firewall']['rules']['rate_limits'][category]
                    if len(attempts) > limits['max_attempts']:
                        # Block IP or take other action
                        self._handle_rate_limit_exceeded(category)
        except Exception as e:
            print(f"Error checking rate limits: {str(e)}")

    def _should_rotate_keys(self):
        """Check if encryption keys should be rotated"""
        try:
            if not self.security['encryption']['last_rotation']:
                return True
            
            hours_since_rotation = (datetime.now() - self.security['encryption']['last_rotation']).total_seconds() / 3600
            return hours_since_rotation >= self.security['encryption']['key_rotation']
        except Exception as e:
            print(f"Error checking key rotation: {str(e)}")
            return False

    def _should_backup(self):
        """Check if backup should be performed"""
        try:
            if not self.security['backup']['last_backup']:
                return True
            
            seconds_since_backup = (datetime.now() - self.security['backup']['last_backup']).total_seconds()
            return seconds_since_backup >= self.security['backup']['frequency']
        except Exception as e:
            print(f"Error checking backup schedule: {str(e)}")
            return False

    def _handle_rate_limit_exceeded(self, category):
        """Handle rate limit exceeded"""
        try:
            # Log the event
            self.security['monitoring']['security_logs'].append({
                'event': 'rate_limit_exceeded',
                'category': category,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Take action (e.g., block IP, notify admin)
            print(f"Rate limit exceeded for {category}")
        except Exception as e:
            print(f"Error handling rate limit exceeded: {str(e)}")

    def _cleanup_firewall_logs(self):
        """Clean up old firewall logs"""
        try:
            current_time = datetime.now()
            for category in self.security['firewall']['rules']['rate_limits']:
                self.security['firewall']['rules']['rate_limits'][category] = {
                    k: v for k, v in self.security['firewall']['rules']['rate_limits'][category].items()
                    if (current_time - k).total_seconds() < 3600  # Keep last hour
                }
        except Exception as e:
            print(f"Error cleaning up firewall logs: {str(e)}")

    def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            current_time = datetime.now()
            self.security['authentication']['session_tokens'] = {
                k: v for k, v in self.security['authentication']['session_tokens'].items()
                if (current_time - v['created']).total_seconds() < self.security['authentication']['lockout_duration']
            }
        except Exception as e:
            print(f"Error cleaning up expired sessions: {str(e)}")

    def _cleanup_old_backups(self):
        """Clean up old backups"""
        try:
            if self.security['backup']['enabled']:
                # Implement backup cleanup logic
                pass
        except Exception as e:
            print(f"Error cleaning up old backups: {str(e)}")

    def _generate_encryption_keys(self):
        """Generate encryption keys"""
        try:
            # Implement key generation logic
            pass
        except Exception as e:
            print(f"Error generating encryption keys: {str(e)}")

    def _generate_backup_codes(self):
        """Generate backup codes"""
        try:
            # Generate 10 backup codes
            self.security['authentication']['two_factor']['backup_codes'] = {
                ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                for _ in range(10)
            }
        except Exception as e:
            print(f"Error generating backup codes: {str(e)}")

    def _setup_secure_storage(self):
        """Setup secure storage"""
        try:
            # Implement secure storage setup
            pass
        except Exception as e:
            print(f"Error setting up secure storage: {str(e)}")

    def _setup_session_management(self):
        """Setup session management"""
        try:
            # Implement session management setup
            pass
        except Exception as e:
            print(f"Error setting up session management: {str(e)}")

    def _setup_intrusion_detection(self):
        """Setup intrusion detection"""
        try:
            # Implement intrusion detection setup
            pass
        except Exception as e:
            print(f"Error setting up intrusion detection: {str(e)}")

    def _setup_activity_logging(self):
        """Setup activity logging"""
        try:
            # Implement activity logging setup
            pass
        except Exception as e:
            print(f"Error setting up activity logging: {str(e)}")

    def _setup_backup_schedule(self):
        """Setup backup schedule"""
        try:
            # Implement backup schedule setup
            pass
        except Exception as e:
            print(f"Error setting up backup schedule: {str(e)}")

    def _setup_backup_encryption(self):
        """Setup backup encryption"""
        try:
            # Implement backup encryption setup
            pass
        except Exception as e:
            print(f"Error setting up backup encryption: {str(e)}")

    def _rotate_encryption_keys(self):
        """Rotate encryption keys"""
        try:
            # Implement key rotation logic
            self.security['encryption']['last_rotation'] = datetime.now()
        except Exception as e:
            print(f"Error rotating encryption keys: {str(e)}")

    def _perform_backup(self):
        """Perform backup"""
        try:
            # Implement backup logic
            self.security['backup']['last_backup'] = datetime.now()
        except Exception as e:
            print(f"Error performing backup: {str(e)}")

    def _check_failed_attempts(self):
        """Check failed authentication attempts"""
        try:
            # Implement failed attempts checking
            pass
        except Exception as e:
            print(f"Error checking failed attempts: {str(e)}")

    def create_learning_bot(self, bot_type, custom_name=None):
        """Create a new learning bot"""
        try:
            if bot_type not in self._learning_bots['bot_templates']:
                return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ {bot_type} အတွက် bot template မရှိသေးပါဘူး။ 😊"
            
            template = self._learning_bots['bot_templates'][bot_type]
            bot_name = custom_name if custom_name else template['name']
            
            # Create new bot instance
            new_bot = {
                'name': bot_name,
                'type': bot_type,
                'capabilities': template['capabilities'],
                'knowledge_base': template['knowledge_base'],
                'created_at': datetime.now(),
                'status': 'active',
                'interaction_count': 0
            }
            
            # Add to active bots
            self._learning_bots['active_bots'][bot_name] = new_bot
            self._learning_bots['bot_interactions'][bot_name] = []
            
            return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ {bot_name} ကို အောင်မြင်စွာ ဖန်တီးလိုက်ပါပြီ။ 😊"
            
        except Exception as e:
            return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ Bot ဖန်တီးရာတွင် အမှားရှိနေပါတယ်: {str(e)} 😕"

    def interact_with_bot(self, bot_name, query):
        """Interact with a learning bot"""
        try:
            if bot_name not in self._learning_bots['active_bots']:
                return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ {bot_name} ကို မတွေ့ရှိပါဘူး။ 😊"
            
            bot = self._learning_bots['active_bots'][bot_name]
            
            # Record interaction
            interaction = {
                'timestamp': datetime.now(),
                'query': query,
                'bot_type': bot['type']
            }
            self._learning_bots['bot_interactions'][bot_name].append(interaction)
            bot['interaction_count'] += 1
            
            # Process query based on bot type
            response = self._process_bot_query(bot, query)
            
            # Learn from interaction
            self._learn_from_bot_interaction(bot, query, response)
            
            return response
            
        except Exception as e:
            return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ Bot နဲ့ ဆက်သွယ်ရာတွင် အမှားရှိနေပါတယ်: {str(e)} 😕"

    def _process_bot_query(self, bot, query):
        """Process query for specific bot type"""
        try:
            if bot['type'] == 'math_bot':
                return self._handle_math_bot_query(query)
            elif bot['type'] == 'science_bot':
                return self._handle_science_bot_query(query)
            elif bot['type'] == 'language_bot':
                return self._handle_language_bot_query(query)
            elif bot['type'] == 'programming_bot':
                return self._handle_programming_bot_query(query)
            else:
                return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ {bot['type']} အတွက် query processing မရှိသေးပါဘူး။ 😊"
        except Exception as e:
            return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ Query ကို ပြုပြင်ရာတွင် အမှားရှိနေပါတယ်: {str(e)} 😕"

    def _learn_from_bot_interaction(self, bot, query, response):
        """Learn from bot interaction"""
        try:
            # Add to learning history
            learning_entry = {
                'timestamp': datetime.now(),
                'bot_name': bot['name'],
                'bot_type': bot['type'],
                'query': query,
                'response': response,
                'learned_concepts': self._extract_concepts(query, response)
            }
            self._learning_bots['learning_history'].append(learning_entry)
            
            # Update knowledge base
            self._update_knowledge_from_interaction(learning_entry)
            
            # Gain experience
            self._gain_experience(100, 'learning')  # Base experience for learning
            
            # Additional experience for successful interaction
            if len(learning_entry['learned_concepts']) > 0:
                self._gain_experience(50 * len(learning_entry['learned_concepts']), 'learning')
            
        except Exception as e:
            print(f"Error learning from bot interaction: {str(e)}")

    def _extract_concepts(self, query, response):
        """Extract learning concepts from interaction"""
        try:
            # Implement concept extraction logic
            return []
        except Exception as e:
            print(f"Error extracting concepts: {str(e)}")
            return []

    def _update_knowledge_from_interaction(self, learning_entry):
        """Update knowledge base from interaction"""
        try:
            # Implement knowledge update logic
            pass
        except Exception as e:
            print(f"Error updating knowledge: {str(e)}")

    def get_learning_progress(self):
        """Get learning progress from bot interactions"""
        try:
            total_interactions = sum(bot['interaction_count'] for bot in self._learning_bots['active_bots'].values())
            unique_concepts = len(set(concept for entry in self._learning_bots['learning_history'] 
                                   for concept in entry['learned_concepts']))
            
            return {
                'total_interactions': total_interactions,
                'unique_concepts': unique_concepts,
                'active_bots': len(self._learning_bots['active_bots']),
                'learning_history': self._learning_bots['learning_history']
            }
        except Exception as e:
            print(f"Error getting learning progress: {str(e)}")
            return {}

    def get_version(self):
        """Get bot version information"""
        return {
            'version': f"{self._version['major']}.{self._version['minor']}.{self._version['patch']}",
            'build': self._version['build'],
            'stage': self._version['stage'],
            'full_version': f"v{self._version['major']}.{self._version['minor']}.{self._version['patch']}-{self._version['stage']}+{self._version['build']}"
        }

    def get_level_info(self):
        """Get bot level information"""
        return {
            'level': self._level['current'],
            'experience': self._level['experience'],
            'next_level': self._level['next_level'],
            'progress': (self._level['experience'] / self._level['next_level']) * 100,
            'capabilities': self._level['capabilities'],
            'unlocked_features': self._level['unlocked_features']
        }

    def _gain_experience(self, amount, category=None):
        """Gain experience points"""
        try:
            # Apply learning rate
            adjusted_amount = amount * self._level['learning_rate']
            
            # Add experience
            self._level['experience'] += adjusted_amount
            
            # Update category if specified
            if category and category in self._level['capabilities']:
                self._level['capabilities'][category] += (adjusted_amount / 1000)
            
            # Check for level up
            if self._level['experience'] >= self._level['next_level']:
                self._level_up()
            
            return True
        except Exception as e:
            print(f"Error gaining experience: {str(e)}")
            return False

    def _level_up(self):
        """Handle level up"""
        try:
            # Increase level
            self._level['current'] += 1
            
            # Calculate new next level requirement
            self._level['next_level'] = int(self._level['next_level'] * 1.5)
            
            # Increase learning rate
            self._level['learning_rate'] += 0.1
            
            # Unlock new features based on level
            self._unlock_features()
            
            # Log level up
            print(f"Level up! Now at level {self._level['current']}")
            
        except Exception as e:
            print(f"Error during level up: {str(e)}")

    def _unlock_features(self):
        """Unlock new features based on level"""
        try:
            new_features = []
            
            # Define feature unlocks by level
            feature_unlocks = {
                2: ['advanced_learning', 'pattern_recognition'],
                3: ['complex_problem_solving', 'context_awareness'],
                4: ['creative_solutions', 'multi_topic_learning'],
                5: ['advanced_communication', 'emotional_intelligence']
            }
            
            # Check for new features to unlock
            if self._level['current'] in feature_unlocks:
                new_features = feature_unlocks[self._level['current']]
                self._level['unlocked_features'].extend(new_features)
            
            return new_features
            
        except Exception as e:
            print(f"Error unlocking features: {str(e)}")
            return []

    def rebuild(self, command, parameters=None):
        """Rebuild the bot based on owner's command"""
        try:
            if not self.verify_owner():
                return "မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ Rebuild လုပ်ဖို့ ခွင့်ပြုချက်မရှိပါဘူး။ 😊"
            
            if command not in self._rebuild['rebuild_commands']:
                return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ {command} ဆိုတဲ့ rebuild command မရှိပါဘူး။ 😊"
            
            # Execute rebuild command
            result = self._rebuild['rebuild_commands'][command](parameters)
            
            # Log rebuild
            self._rebuild['last_rebuild'] = datetime.now()
            self._rebuild['rebuild_history'].append({
                'timestamp': datetime.now(),
                'command': command,
                'parameters': parameters,
                'result': result
            })
            
            return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ Rebuild လုပ်ဆောင်ချက် ပြီးဆုံးပါပြီ။ {result} 😊"
            
        except Exception as e:
            return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ Rebuild လုပ်ရာတွင် အမှားရှိနေပါတယ်: {str(e)} 😕"

    def _rebuild_update(self, parameters):
        """Update bot components"""
        try:
            if not parameters:
                return "Update parameters မရှိပါဘူး။"
            
            updated_components = []
            for component, value in parameters.items():
                if component in self._rebuild['protected_components']:
                    continue
                
                # Update component
                if hasattr(self, f"_{component}"):
                    setattr(self, f"_{component}", value)
                    updated_components.append(component)
            
            return f"Updated components: {', '.join(updated_components)}"
            
        except Exception as e:
            print(f"Error updating components: {str(e)}")
            return "Update failed"

    def _rebuild_optimize(self, parameters):
        """Optimize bot performance"""
        try:
            if not parameters:
                return "Optimization parameters မရှိပါဘူး။"
            
            optimized_areas = []
            for area, value in parameters.items():
                if area in self._rebuild['protected_components']:
                    continue
                
                # Optimize area
                if hasattr(self, f"_{area}"):
                    current_value = getattr(self, f"_{area}")
                    if isinstance(current_value, dict):
                        current_value.update(value)
                        optimized_areas.append(area)
            
            return f"Optimized areas: {', '.join(optimized_areas)}"
            
        except Exception as e:
            print(f"Error optimizing: {str(e)}")
            return "Optimization failed"

    def _rebuild_enhance(self, parameters):
        """Enhance bot capabilities"""
        try:
            if not parameters:
                return "Enhancement parameters မရှိပါဘူး။"
            
            enhanced_capabilities = []
            for capability, value in parameters.items():
                if capability in self._rebuild['protected_components']:
                    continue
                
                # Enhance capability
                if hasattr(self, f"_{capability}"):
                    current_value = getattr(self, f"_{capability}")
                    if isinstance(current_value, dict):
                        current_value.update(value)
                        enhanced_capabilities.append(capability)
            
            return f"Enhanced capabilities: {', '.join(enhanced_capabilities)}"
            
        except Exception as e:
            print(f"Error enhancing capabilities: {str(e)}")
            return "Enhancement failed"

    def _rebuild_restore(self, parameters):
        """Restore bot to previous state"""
        try:
            if not parameters or 'timestamp' not in parameters:
                return "Restore timestamp မရှိပါဘူး။"
            
            # Find closest rebuild point
            target_time = datetime.fromisoformat(parameters['timestamp'])
            closest_rebuild = min(
                self._rebuild['rebuild_history'],
                key=lambda x: abs(datetime.fromisoformat(x['timestamp']) - target_time)
            )
            
            # Restore state
            if 'parameters' in closest_rebuild:
                self._rebuild_update(closest_rebuild['parameters'])
            
            return f"Restored to state from {closest_rebuild['timestamp']}"
            
        except Exception as e:
            print(f"Error restoring state: {str(e)}")
            return "Restore failed"

    def start_hosting(self, config=None):
        """Start hosting the bot"""
        try:
            if not self.verify_owner():
                return "မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ Hosting စတင်ဖို့ ခွင့်ပြုချက်မရှိပါဘူး။ 😊"
            
            if self._hosting['enabled']:
                return "မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ Hosting က ရှိပြီးသားဖြစ်နေပါပြီ။ 😊"
            
            # Update config if provided
            if config:
                self._hosting['config'].update(config)
            
            # Start hosting
            self._hosting['enabled'] = True
            self._hosting['status'] = 'starting'
            
            # Start server in a separate thread
            server_thread = threading.Thread(target=self._initialize_server, daemon=True)
            server_thread.start()
            
            # Start monitoring
            self._start_monitoring()
            
            # Start backup if enabled
            if self._hosting['deployment']['backup_enabled']:
                self._start_backup()
            
            self._hosting['status'] = 'online'
            return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ Public hosting ကို အောင်မြင်စွာ စတင်လိုက်ပါပြီ။\nPort: {self._hosting['config']['port']}\nAPI Endpoints:\n- /api/chat (POST)\n- /api/status (GET)\n- /api/info (GET) 😊"
            
        except Exception as e:
            self._hosting['status'] = 'error'
            return f"မင်္ဂလာပါ! ကျွန်တော် Tobi ပါ။ Hosting စတင်ရာတွင် အမှားရှိနေပါတယ်: {str(e)} 😕"

    def _stop_server(self):
        """Stop the server"""
        try:
            # Implement server shutdown
            pass
        except Exception as e:
            print(f"Error stopping server: {str(e)}")

    def _stop_monitoring(self):
        """Stop monitoring"""
        try:
            self._hosting['monitoring']['enabled'] = False
        except Exception as e:
            print(f"Error stopping monitoring: {str(e)}")

    def _stop_backup(self):
        """Stop backup system"""
        try:
            self._hosting['deployment']['backup_enabled'] = False
        except Exception as e:
            print(f"Error stopping backup: {str(e)}")

    def _initialize_server(self):
        """Initialize the server"""
        try:
            # Create necessary directories
            os.makedirs('logs', exist_ok=True)
            os.makedirs('backups', exist_ok=True)
            
            # Start SocketIO server
            self.socketio.run(
                self.app,
                host=self._hosting['config']['host'],
                port=self._hosting['config']['port'],
                debug=False
            )
        except Exception as e:
            print(f"Error initializing server: {str(e)}")
            raise

    def _start_monitoring(self):
        """Start monitoring the bot"""
        try:
            if self._hosting['monitoring']['enabled']:
                # Start monitoring thread
                threading.Thread(target=self._monitor_metrics, daemon=True).start()
        except Exception as e:
            print(f"Error starting monitoring: {str(e)}")

    def _start_backup(self):
        """Start backup system"""
        try:
            if self._hosting['deployment']['backup_enabled']:
                # Start backup thread
                threading.Thread(target=self._backup_loop, daemon=True).start()
        except Exception as e:
            print(f"Error starting backup: {str(e)}")

    def _monitor_metrics(self):
        """Monitor bot metrics"""
        while self._hosting['enabled']:
            try:
                # Update metrics
                self._update_metrics()
                
                # Check alerts
                self._check_alerts()
                
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Error monitoring metrics: {str(e)}")
                time.sleep(60)

    def _backup_loop(self):
        """Backup loop"""
        while self._hosting['enabled']:
            try:
                # Perform backup
                self._perform_backup()
                
                time.sleep(self._hosting['deployment']['backup_interval'])
            except Exception as e:
                print(f"Error in backup loop: {str(e)}")
                time.sleep(60)

    def _update_metrics(self):
        """Update monitoring metrics"""
        try:
            metrics = self._hosting['monitoring']['metrics']
            
            # Update uptime
            metrics['uptime'] += 1
            
            # Update response time
            metrics['response_time'].append(self._calculate_response_time())
            if len(metrics['response_time']) > 100:
                metrics['response_time'].pop(0)
            
            # Update memory usage
            metrics['memory_usage'].append(self._get_memory_usage())
            if len(metrics['memory_usage']) > 100:
                metrics['memory_usage'].pop(0)
            
            # Update CPU usage
            metrics['cpu_usage'].append(self._get_cpu_usage())
            if len(metrics['cpu_usage']) > 100:
                metrics['cpu_usage'].pop(0)
            
        except Exception as e:
            print(f"Error updating metrics: {str(e)}")

    def _check_alerts(self):
        """Check for alert conditions"""
        try:
            metrics = self._hosting['monitoring']['metrics']
            thresholds = self._hosting['monitoring']['alerts']['thresholds']
            
            # Check response time
            if metrics['response_time'] and max(metrics['response_time']) > thresholds['response_time']:
                self._send_alert('response_time', max(metrics['response_time']))
            
            # Check error rate
            if metrics['error_rate'] > thresholds['error_rate']:
                self._send_alert('error_rate', metrics['error_rate'])
            
            # Check memory usage
            if metrics['memory_usage'] and max(metrics['memory_usage']) > thresholds['memory_usage']:
                self._send_alert('memory_usage', max(metrics['memory_usage']))
            
            # Check CPU usage
            if metrics['cpu_usage'] and max(metrics['cpu_usage']) > thresholds['cpu_usage']:
                self._send_alert('cpu_usage', max(metrics['cpu_usage']))
            
        except Exception as e:
            print(f"Error checking alerts: {str(e)}")

    def _send_alert(self, alert_type, value):
        """Send alert notification"""
        try:
            # Implement alert notification
            print(f"Alert: {alert_type} exceeded threshold. Current value: {value}")
        except Exception as e:
            print(f"Error sending alert: {str(e)}")

    def _get_memory_usage(self):
        """Get current memory usage"""
        try:
            # Implement memory usage check
            return 0
        except Exception as e:
            print(f"Error getting memory usage: {str(e)}")
            return 0

    def _get_cpu_usage(self):
        """Get current CPU usage"""
        try:
            # Implement CPU usage check
            return 0
        except Exception as e:
            print(f"Error getting CPU usage: {str(e)}")
            return 0

    def _setup_routes(self):
        """Set up API routes"""
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            try:
                data = request.get_json()
                if not data or 'message' not in data:
                    return jsonify({'error': 'No message provided'}), 400
                
                response = self.get_response(data['message'])
                return jsonify({'response': response})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/generate/image', methods=['POST'])
        def generate_image():
            try:
                data = request.get_json()
                if not data or 'prompt' not in data:
                    return jsonify({'error': 'No prompt provided'}), 400
                
                image, error = self.generate_image(
                    data['prompt'],
                    negative_prompt=data.get('negative_prompt'),
                    width=data.get('width', 512),
                    height=data.get('height', 512)
                )
                
                if error:
                    return jsonify({'error': error}), 500
                
                # Convert image to base64
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                return jsonify({
                    'image': img_str,
                    'format': 'base64'
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/generate/video', methods=['POST'])
        def generate_video():
            try:
                data = request.get_json()
                if not data or 'prompt' not in data:
                    return jsonify({'error': 'No prompt provided'}), 400
                
                video, error = self.generate_video(
                    data['prompt'],
                    duration=data.get('duration', 4),
                    fps=data.get('fps', 24)
                )
                
                if error:
                    return jsonify({'error': error}), 500
                
                # Save video to temporary file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_filename = f"temp_video_{timestamp}.mp4"
                video.write_videofile(temp_filename)
                
                return send_file(
                    temp_filename,
                    mimetype='video/mp4',
                    as_attachment=True,
                    download_name=f"generated_video_{timestamp}.mp4"
                )
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/status', methods=['GET'])
        def status():
            try:
                return jsonify({
                    'status': self._hosting['status'],
                    'uptime': self._hosting['monitoring']['metrics']['uptime'],
                    'active_users': self._hosting['monitoring']['metrics']['active_users'],
                    'media_generation': {
                        'enabled': self._media_generation['enabled'],
                        'image_model': self._media_generation['models']['image']['status']
                    }
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/info', methods=['GET'])
        def info():
            try:
                return jsonify({
                    'name': self.name,
                    'version': self.get_version(),
                    'level': self.get_level_info()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def _initialize_media_models(self):
        """Initialize media generation models"""
        try:
            # Initialize image generation model
            self._media_generation['models']['image']['pipeline'] = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16
            )
            if torch.cuda.is_available():
                self._media_generation['models']['image']['pipeline'] = self._media_generation['models']['image']['pipeline'].to("cuda")
            self._media_generation['models']['image']['status'] = 'ready'
            
            # Initialize image-to-image model
            self._media_generation['models']['img2img'] = StableDiffusionImg2ImgPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16
            )
            if torch.cuda.is_available():
                self._media_generation['models']['img2img'] = self._media_generation['models']['img2img'].to("cuda")
            
        except Exception as e:
            print(f"Error initializing media models: {str(e)}")
            self._media_generation['models']['image']['status'] = 'error'

    def generate_image(self, prompt, negative_prompt=None, width=512, height=512):
        """Generate an image from text prompt"""
        try:
            if not self._media_generation['enabled']:
                return None, "Media generation is disabled"
            
            if self._media_generation['models']['image']['status'] != 'ready':
                return None, "Image generation model is not ready"
            
            # Set up generation parameters
            settings = self._media_generation['settings']['image']
            if negative_prompt is None:
                negative_prompt = settings['negative_prompt']
            
            # Generate image
            image = self._media_generation['models']['image']['pipeline'](
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=settings['num_inference_steps'],
                guidance_scale=settings['guidance_scale']
            ).images[0]
            
            # Save to history
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"
            image.save(f"generated/{filename}")
            
            self._media_generation['history']['images'].append({
                'prompt': prompt,
                'filename': filename,
                'timestamp': timestamp
            })
            
            return image, None
            
        except Exception as e:
            return None, str(e)

    def generate_video(self, prompt, duration=4, fps=24):
        """Generate a video from text prompt"""
        try:
            if not self._media_generation['enabled']:
                return None, "Media generation is disabled"
            
            # Generate frames
            frames = []
            for i in range(duration * fps):
                # Generate frame
                frame, error = self.generate_image(
                    prompt,
                    width=512,
                    height=512
                )
                if error:
                    return None, error
                frames.append(np.array(frame))
            
            # Create video
            clip = ImageSequenceClip(frames, fps=fps)
            
            # Save to history
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_video_{timestamp}.mp4"
            clip.write_videofile(f"generated/{filename}")
            
            self._media_generation['history']['videos'].append({
                'prompt': prompt,
                'filename': filename,
                'timestamp': timestamp
            })
            
            return clip, None
            
        except Exception as e:
            return None, str(e)

    def _setup_websocket_events(self):
        """Set up WebSocket event handlers"""
        @self.socketio.on('connect')
        def handle_connect():
            client_id = request.sid
            self._realtime['connections'][client_id] = {
                'connected_at': datetime.now(),
                'last_activity': datetime.now(),
                'events_subscribed': []
            }
            self._realtime['status']['active_users'] = len(self._realtime['connections'])
            emit('status_update', {
                'type': 'connection',
                'message': 'Connected to Tobi',
                'active_users': self._realtime['status']['active_users']
            })

        @self.socketio.on('disconnect')
        def handle_disconnect():
            client_id = request.sid
            if client_id in self._realtime['connections']:
                del self._realtime['connections'][client_id]
                self._realtime['status']['active_users'] = len(self._realtime['connections'])
                self._broadcast_status_update()

        @self.socketio.on('chat_message')
        def handle_chat_message(data):
            try:
                if 'message' not in data:
                    emit('error', {'message': 'No message provided'})
                    return
                
                # Process message
                response = self.get_response(data['message'])
                
                # Send response
                emit('chat_response', {
                    'message': response,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Broadcast to all clients if it's a broadcast message
                if data.get('broadcast', False):
                    self.socketio.emit('broadcast_message', {
                        'message': response,
                        'sender': request.sid,
                        'timestamp': datetime.now().isoformat()
                    })
                
            except Exception as e:
                emit('error', {'message': str(e)})

        @self.socketio.on('subscribe')
        def handle_subscribe(data):
            try:
                client_id = request.sid
                if 'events' not in data:
                    emit('error', {'message': 'No events specified'})
                    return
                
                self._realtime['connections'][client_id]['events_subscribed'] = data['events']
                emit('subscription_confirmed', {
                    'events': data['events'],
                    'message': 'Successfully subscribed to events'
                })
                
            except Exception as e:
                emit('error', {'message': str(e)})

        @self.socketio.on('media_generation_request')
        def handle_media_generation(data):
            try:
                if 'type' not in data or 'prompt' not in data:
                    emit('error', {'message': 'Invalid request'})
                    return
                
                # Start generation in background
                if data['type'] == 'image':
                    self._generate_image_realtime(data['prompt'], request.sid)
                elif data['type'] == 'video':
                    self._generate_video_realtime(data['prompt'], request.sid)
                else:
                    emit('error', {'message': 'Invalid media type'})
                
            except Exception as e:
                emit('error', {'message': str(e)})

    def _start_realtime_processor(self):
        """Start real-time message processor"""
        def process_messages():
            while True:
                try:
                    message = self._realtime['message_queue'].get()
                    if message:
                        self._process_realtime_message(message)
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Error processing real-time message: {str(e)}")
                    time.sleep(1)
        
        threading.Thread(target=process_messages, daemon=True).start()

    def _process_realtime_message(self, message):
        """Process real-time message"""
        try:
            if message['type'] == 'status_update':
                self._broadcast_status_update()
            elif message['type'] == 'media_progress':
                self._broadcast_media_progress(message)
            elif message['type'] == 'system_alert':
                self._broadcast_system_alert(message)
        except Exception as e:
            print(f"Error processing message: {str(e)}")

    def _broadcast_status_update(self):
        """Broadcast status update to all clients"""
        try:
            self.socketio.emit('status_update', {
                'active_users': self._realtime['status']['active_users'],
                'system_status': self._realtime['status']['system_status'],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error broadcasting status: {str(e)}")

    def _broadcast_media_progress(self, message):
        """Broadcast media generation progress"""
        try:
            self.socketio.emit('media_progress', {
                'type': message['media_type'],
                'progress': message['progress'],
                'status': message['status'],
                'timestamp': datetime.now().isoformat()
            }, room=message['client_id'])
        except Exception as e:
            print(f"Error broadcasting media progress: {str(e)}")

    def _broadcast_system_alert(self, message):
        """Broadcast system alert"""
        try:
            self.socketio.emit('system_alert', {
                'level': message['level'],
                'message': message['message'],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error broadcasting system alert: {str(e)}")

    async def _generate_image_realtime(self, prompt, client_id):
        """Generate image with real-time progress updates"""
        try:
            # Notify start
            self._broadcast_media_progress({
                'media_type': 'image',
                'progress': 0,
                'status': 'starting',
                'client_id': client_id
            })
            
            # Generate image
            image, error = self.generate_image(prompt)
            
            if error:
                self._broadcast_media_progress({
                    'media_type': 'image',
                    'progress': 100,
                    'status': 'error',
                    'error': error,
                    'client_id': client_id
                })
                return
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Send result
            self.socketio.emit('media_result', {
                'type': 'image',
                'data': img_str,
                'format': 'base64',
                'timestamp': datetime.now().isoformat()
            }, room=client_id)
            
        except Exception as e:
            self._broadcast_media_progress({
                'media_type': 'image',
                'progress': 100,
                'status': 'error',
                'error': str(e),
                'client_id': client_id
            })

    async def _generate_video_realtime(self, prompt, client_id):
        """Generate video with real-time progress updates"""
        try:
            # Notify start
            self._broadcast_media_progress({
                'media_type': 'video',
                'progress': 0,
                'status': 'starting',
                'client_id': client_id
            })
            
            # Generate video
            video, error = self.generate_video(prompt)
            
            if error:
                self._broadcast_media_progress({
                    'media_type': 'video',
                    'progress': 100,
                    'status': 'error',
                    'error': error,
                    'client_id': client_id
                })
                return
            
            # Save to temporary file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_filename = f"temp_video_{timestamp}.mp4"
            video.write_videofile(temp_filename)
            
            # Send result
            self.socketio.emit('media_result', {
                'type': 'video',
                'filename': temp_filename,
                'timestamp': datetime.now().isoformat()
            }, room=client_id)
            
        except Exception as e:
            self._broadcast_media_progress({
                'media_type': 'video',
                'progress': 100,
                'status': 'error',
                'error': str(e),
                'client_id': client_id
            })

# Expose app for Gunicorn/Render
chatbot = AdvancedChatbot()
app = chatbot.app

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    chatbot.socketio.run(chatbot.app, host="0.0.0.0", port=port) 