# Bujji AI Chatbot 🤖

A friendly and empathetic AI chatbot inspired by Bujji from Kalki 2898 AD, built with Flask and Google's Gemini AI.

## 🌟 Features

- **Natural Telugu Conversations**: Responds in conversational Telugu using English script
- **Emotion Detection**: Understands and responds to user emotions
- **Contextual Memory**: Maintains conversation history for personalized interactions
- **Knowledge Base**: Provides relevant information based on user queries
- **Friendly Personality**: Witty, empathetic, and encouraging responses
- **Content Safety**: Built-in content filtering for appropriate interactions

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google Gemini API key
- Flask

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bujji-ai-chatbot.git
cd bujji-ai-chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export GENIE_API_KEY="your-gemini-api-key"
```

4. Run the application:
```bash
python app2.py
```

The server will start at `http://localhost:5050`

## 🛠️ Technology Stack

- **Backend**: Flask
- **AI Model**: Google Gemini AI
- **Language**: Python 3.9
- **Memory Storage**: JSON-based file system
- **Deployment**: Vercel-ready

## 📁 Project Structure

```
bujji-ai-chatbot/
├── app2.py              # Main application file
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel deployment configuration
├── templates/          # HTML templates
│   └── index.html     # Main chat interface
└── user_memories/     # Directory for storing chat histories
```

## 🔧 Configuration

### Environment Variables

- `GENIE_API_KEY`: Your Google Gemini API key
- `PORT`: Server port (default: 5050)

### Memory Settings

- `MAX_MEMORY_EXCHANGES`: Number of conversation turns to remember (default: 6)

## 🌐 API Endpoints

### GET /
- Renders the main chat interface

### POST /chat
- Handles chat messages
- Request body:
  ```json
  {
    "message": "user message",
    "userId": "unique-user-id"
  }
  ```
- Response:
  ```json
  {
    "response": "bujji's reply"
  }
  ```

## 🚀 Deployment

### Local Development
```bash
python app2.py
```

### Vercel Deployment
1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- Inspired by Bujji from Kalki 2898 AD
- Powered by Google's Gemini AI
- Built with Flask

## 📧 Contact

Your Name - Pavan Kumar

Project Link: https://bujz-01.onrender.com
