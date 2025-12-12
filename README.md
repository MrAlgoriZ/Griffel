# Griffel

A Telegram bot built with aiogram that provides AI-powered conversations, configurable settings, and administrative controls.

## Features

- **AI Conversations**: Interact with various AI models (SMART, AGRESSIVE, KAWAII, etc.) using the `/ask` command
- **Configurable Settings**: Admins can customize bot behavior per chat:
  - History length (max 10 without premium, 25 with premium)
  - Bot mode (predefined models or custom)
  - Custom prompts (premium feature)
  - Bot name
  - OpenRouter API key
- **Database Integration**: PostgreSQL backend with OOP Table abstraction
- **Message History**: Per-chat conversation history with configurable length
- **Admin Controls**: Restricted configuration access to chat administrators
- **Premium Features**: Extended limits and custom prompt editing

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Telegram Bot Token
- OpenRouter API key (optional, for enhanced AI responses)

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd declist-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the following variables:
   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token
   OPEN_ROUTER_TOKEN=your_openrouter_api_key
   DATABASE_USER=your_db_user
   DATABASE_USER_PASSWORD=your_db_password
   DATABASE_NAME=your_db_name
   DATABASE_HOST=your_db_host
   TABLE_NAME=chat_configs
   ```

4. Set up the database table:
   ```sql
   CREATE TABLE chat_configs (
       id BIGINT PRIMARY KEY,
       prompt TEXT,
       historyMaxlen SMALLINT DEFAULT 10,
       isPremium BOOLEAN DEFAULT FALSE,
       botName TEXT,
       botMode TEXT DEFAULT 'SMART',
       chatRules TEXT,
       openRouterKey TEXT
   );
   ```

5. Run the bot:
   ```bash
   python main.py
   ```

## Usage

### Commands
- `/start` - Welcome message
- `/help` - Help information
- `/config` - Open configuration menu (admins only)
- `/ask <question>` - Ask the AI a question
- `/kick` - Kick a user
- `/ban <time>` - Ban a user
- `/mute <time>` - Mute a user

### Configuration
Use `/config` to access the inline keyboard for settings:
- **History Length**: Set conversation history size (1, 5, 10, or custom)
- **Bot Mode**: Choose from predefined models (SMART, AGRESSIVE, KAWAII) or CUSTOM
- **Custom Prompt**: Edit system prompt (premium only)
- **Bot Name**: Set display name (max 15 characters)
- **OpenRouter Key**: Provide API key for better responses

### AI Models
- **SMART**: Balanced, intelligent responses
- **AGRESSIVE**: More direct and assertive
- **KAWAII**: Cute and friendly style
- **CUSTOM**: Use your own system prompt

## Architecture

- **Routers**: Modular handlers for different bot functions
  - `base_router`: Basic commands and configuration
  - `ai_router`: AI conversation handling
  - `moderator_router`: Moderation features
- **Database Layer**: OOP `Table` class with async PostgreSQL operations
- **AI Service**: Integration with OpenRouter API using various models
- **Storage**: In-memory message history with configurable limits
- **Middleware**: Automatic message logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the Apache License - see the LICENSE file for details.