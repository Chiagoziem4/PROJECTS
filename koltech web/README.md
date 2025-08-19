# Web3 Airdrop Discovery & Community Platform

A production-ready platform for discovering legitimate Web3 airdrops and connecting with the community. This project focuses on helping users find, learn about, and discuss airdrops safely and ethically.

## 🚀 Features

- Discover legitimate airdrops with detailed information
- Connect wallet for personalized experience
- Community blog and discussion
- Real-time notifications (Discord + Telegram)
- Secure API endpoints
- Research-driven UI/UX

## 🛠 Tech Stack

- Frontend: Next.js + Tailwind CSS
- Web3: ethers.js + web3modal
- Backend: Node.js/Express
- Database: SQLite
- Research: Python (BeautifulSoup, requests)
- Notifications: Discord webhook + Telegram bot

## 🎨 Design

- Primary: #2AA9E0 (Photo Blue)
- Accent: #E5E4E2 (Platinum)
- Dark: #0A0A0A
- Light: #F7F8FA

## 📦 Setup Instructions

### Prerequisites

- Node.js 16+
- Python 3.8+
- SQLite3

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create .env.local from example:
   ```bash
   cp ../.env.example .env.local
   ```

4. Start development server:
   ```bash
   npm run dev
   ```

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up database:
   ```bash
   sqlite3 ../data/airdrops.db < db/schema.sql
   sqlite3 ../data/airdrops.db < db/seed.sql
   ```

4. Start server:
   ```bash
   npm run start
   ```

### Research Script Setup

1. Navigate to research directory:
   ```bash
   cd research
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Run analysis:
   ```bash
   python analyze_references.py
   ```

## 🔒 Security & Ethics

- No automated claiming or transaction automation
- Respects robots.txt and rate limits
- Clear user consent required for all actions
- API key protection
- Input sanitization

## 📝 Manual Steps Before Running

1. [ ] Add required API keys to .env
2. [ ] Run research script to generate report
3. [ ] Seed database with initial data
4. [ ] Set up Web3Modal project
5. [ ] Configure notification webhooks (optional)

## 📄 License

MIT

## ⚠️ Disclaimer

This platform is for information and educational purposes only. Always DYOR (Do Your Own Research) and verify information from official sources before taking any action.
