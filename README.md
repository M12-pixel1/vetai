# VetAI - Veterinary AI Application v2.0

AI-powered veterinary diagnostic platform with multi-modal analysis capabilities.

## Features

- 🔬 **Multi-modal AI Diagnostics**: Image, video, and audio analysis
- 🗄️ **PostgreSQL Database**: Robust data persistence with SQLAlchemy ORM
- 💾 **Redis Caching**: High-performance caching layer
- 🎨 **Streamlit Dashboard**: Modern, intuitive web interface
- 🔐 **Authentication & Authorization**: Secure user management
- 💳 **Payment Integration**: Subscription management
- 🐳 **Docker Support**: Easy deployment with Docker Compose

## Project Structure

```
rupestėlis-vet-ai-v2/
├── backend/
│   ├── __init__.py
│   ├── database.py          # PostgreSQL + SQLAlchemy ORM
│   ├── models.py            # DB Models
│   ├── ai_engine.py         # Multi-model AI orchestration
│   ├── processors/
│   │   ├── image_processor.py
│   │   ├── audio_processor.py
│   │   └── video_processor.py
│   └── cache.py             # Redis integration
├── frontend/
│   ├── dashboard.py         # Streamlit UI
│   ├── auth.py             
│   ├── payments.py          
│   └── components/          # Reusable UI components
├── config/
│   ├── settings.py
│   └── logging_config.py
├── tests/
│   ├── test_ai_engine.py
│   ├── test_database.py
│   └── test_integration.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── alembic/                 # DB migrations
```

## Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional but recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/M12-pixel1/vetai.git
cd vetai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize database:
```bash
alembic upgrade head
```

5. Run the application:
```bash
streamlit run frontend/dashboard.py
```

### Docker Deployment

```bash
docker-compose up -d
```

Access the application at http://localhost:8501

## Configuration

Configuration is managed through environment variables. See `config/settings.py` for available options.

Key settings:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `OPENAI_API_KEY`: OpenAI API key for AI models
- `ENVIRONMENT`: development/production

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=backend --cov=frontend
```

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## API Documentation

(To be added when FastAPI backend is implemented)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Copyright (c) 2024 VetAI Team. All rights reserved.

## Support

For support, email support@vetai.example.com or open an issue on GitHub.
