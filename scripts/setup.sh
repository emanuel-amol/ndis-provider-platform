#!/bin/bash

echo "🏥 Setting up NDIS Platform Demo..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create project directory structure
echo "📁 Creating project structure..."
mkdir -p simple-ndis-platform/{backend,frontend,database,automation,deployment,scripts}

# Copy environment files
echo "📄 Setting up environment files..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env 2>/dev/null || echo "DATABASE_URL=postgresql://postgres:password@localhost:5432/ndis_platform" > backend/.env
fi

if [ ! -f frontend/.env ]; then
    echo "REACT_APP_API_URL=http://localhost:5000/api" > frontend/.env
fi

# Install backend dependencies
echo "🐍 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "⚛️ Installing React dependencies..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "  1. Start database: docker-compose up -d database"
echo "  2. Start backend: cd backend && python app.py"
echo "  3. Start frontend: cd frontend && npm start"
echo "  4. Start automation: cd automation && python notification_workflows.py"
echo ""
echo "🌐 Access the application at: http://localhost:3000"
echo "🔐 Demo login: admin@ndis.com / admin123"