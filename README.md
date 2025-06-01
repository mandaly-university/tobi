# Simple Chatbot

A simple command-line chatbot that can respond to basic queries and maintain a conversation in both English and Myanmar (Burmese) languages.

## Features

- Responds to basic greetings and questions in Myanmar language
- Provides current time and date in Myanmar language
- Has multiple response variations for more natural conversation
- Simple command-line interface
- Full Myanmar language support with proper Unicode handling

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the chatbot using:
```
python chatbot.py
```

### Example Commands
- "hello" (မင်္ဂလာပါ)
- "how are you" (နေကောင်းလား)
- "what's your name" (နာမည်ဘယ်လိုခေါ်လဲ)
- "what time is it" (ဘယ်နှစ်နာရီရှိပြီလဲ)
- "what's the date" (ဒီနေ့ဘယ်နေ့လဲ)
- "bye" (ဘိုင့်ဘိုင့်)

## Myanmar Language Support

The chatbot supports Myanmar language with proper Unicode encoding. Make sure your terminal supports UTF-8 encoding to display Myanmar characters correctly.

### Common Myanmar Phrases
- မင်္ဂလာပါ (Mingalaba) - Hello
- နေကောင်းလား (Ne kaung lar) - How are you?
- ဘိုင့်ဘိုင့် (Bye bye) - Goodbye

## Customization

You can easily customize the chatbot by modifying the `responses` dictionary in `chatbot.py`. Add new keywords and responses in either English or Myanmar language to expand the chatbot's capabilities. 