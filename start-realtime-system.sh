#!/bin/bash

# Phase 3.1 - リアルタイムAI推論システム起動スクリプト
# Start Realtime AI Inference System

echo "🚀 Starting MiraiKakaku Phase 3.1 - Realtime AI System"
echo "=================================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Redis is running
check_redis() {
    echo -e "${BLUE}🔍 Checking Redis server...${NC}"

    if command -v redis-cli &> /dev/null; then
        if redis-cli ping > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Redis is running${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Redis is not running, starting local instance...${NC}"
            # Start Redis in background (if available)
            if command -v redis-server &> /dev/null; then
                redis-server --daemonize yes --port 6379 > /dev/null 2>&1
                sleep 2
                if redis-cli ping > /dev/null 2>&1; then
                    echo -e "${GREEN}✅ Redis started successfully${NC}"
                    return 0
                fi
            fi
            echo -e "${YELLOW}⚠️  Redis not available, continuing without cache${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  Redis CLI not found, continuing without cache${NC}"
        return 1
    fi
}

# Install Python dependencies
install_python_deps() {
    echo -e "${BLUE}📦 Installing Python WebSocket dependencies...${NC}"
    cd miraikakakuapi

    if [ -f "requirements-websocket.txt" ]; then
        pip3 install -r requirements-websocket.txt > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Python dependencies installed${NC}"
        else
            echo -e "${RED}❌ Failed to install Python dependencies${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  requirements-websocket.txt not found${NC}"
    fi

    cd ..
    return 0
}

# Start WebSocket server
start_websocket_server() {
    echo -e "${BLUE}🌐 Starting WebSocket server...${NC}"
    cd miraikakakuapi

    # Check if websocket_main.py exists
    if [ ! -f "websocket_main.py" ]; then
        echo -e "${RED}❌ websocket_main.py not found${NC}"
        cd ..
        return 1
    fi

    echo -e "${GREEN}🚀 Starting WebSocket server on port 8080...${NC}"
    python3 websocket_main.py &
    WEBSOCKET_PID=$!

    # Wait for server to start
    sleep 3

    # Check if server is running
    if ps -p $WEBSOCKET_PID > /dev/null; then
        echo -e "${GREEN}✅ WebSocket server started (PID: $WEBSOCKET_PID)${NC}"
        echo $WEBSOCKET_PID > websocket_server.pid
        cd ..
        return 0
    else
        echo -e "${RED}❌ Failed to start WebSocket server${NC}"
        cd ..
        return 1
    fi
}

# Start Next.js frontend
start_frontend() {
    echo -e "${BLUE}🎨 Starting Next.js frontend...${NC}"
    cd miraikakakufront

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
        npm install > /dev/null 2>&1
    fi

    echo -e "${GREEN}🚀 Starting frontend on port 3000...${NC}"
    npm run dev > /dev/null 2>&1 &
    FRONTEND_PID=$!

    # Wait for frontend to start
    sleep 5

    if ps -p $FRONTEND_PID > /dev/null; then
        echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
        echo $FRONTEND_PID > frontend.pid
        cd ..
        return 0
    else
        echo -e "${RED}❌ Failed to start frontend${NC}"
        cd ..
        return 1
    fi
}

# Health check
health_check() {
    echo -e "${BLUE}🏥 Performing health check...${NC}"

    # Check WebSocket server
    if curl -s http://localhost:8080/health > /dev/null; then
        echo -e "${GREEN}✅ WebSocket server is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  WebSocket server health check failed${NC}"
    fi

    # Check Frontend
    if curl -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}✅ Frontend is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend health check failed${NC}"
    fi
}

# Display access information
show_access_info() {
    echo ""
    echo "🎯 System Access Information"
    echo "=================================================="
    echo -e "${GREEN}🌐 Frontend (Next.js):${NC} http://localhost:3000"
    echo -e "${GREEN}📊 Realtime Dashboard:${NC} http://localhost:3000/realtime"
    echo -e "${GREEN}🔌 WebSocket API:${NC} ws://localhost:8080/ws"
    echo -e "${GREEN}📋 WebSocket Health:${NC} http://localhost:8080/health"
    echo -e "${GREEN}📈 WebSocket Stats:${NC} http://localhost:8080/stats"
    echo -e "${GREEN}📖 WebSocket Docs:${NC} http://localhost:8080/docs"
    echo ""
    echo -e "${BLUE}💡 Usage:${NC}"
    echo "1. Open http://localhost:3000/realtime in your browser"
    echo "2. Add stock symbols (e.g., AAPL, MSFT, GOOGL)"
    echo "3. Watch real-time AI predictions appear"
    echo "4. Monitor system performance metrics"
    echo ""
}

# Cleanup function
cleanup() {
    echo -e "${YELLOW}🛑 Shutting down services...${NC}"

    # Kill WebSocket server
    if [ -f "miraikakakuapi/websocket_server.pid" ]; then
        WEBSOCKET_PID=$(cat miraikakakuapi/websocket_server.pid)
        kill $WEBSOCKET_PID 2>/dev/null
        rm miraikakakuapi/websocket_server.pid
        echo -e "${GREEN}✅ WebSocket server stopped${NC}"
    fi

    # Kill frontend
    if [ -f "miraikakakufront/frontend.pid" ]; then
        FRONTEND_PID=$(cat miraikakakufront/frontend.pid)
        kill $FRONTEND_PID 2>/dev/null
        rm miraikakakufront/frontend.pid
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi

    echo -e "${GREEN}✅ All services stopped cleanly${NC}"
    exit 0
}

# Trap cleanup on script exit
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    check_redis
    install_python_deps || echo -e "${YELLOW}⚠️  Continuing without all dependencies${NC}"

    start_websocket_server || {
        echo -e "${RED}❌ Failed to start WebSocket server${NC}"
        exit 1
    }

    start_frontend || {
        echo -e "${RED}❌ Failed to start frontend${NC}"
        cleanup
        exit 1
    }

    health_check
    show_access_info

    echo -e "${GREEN}🎉 Phase 3.1 Realtime AI System is running!${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

    # Keep script running
    while true; do
        sleep 10

        # Basic health monitoring
        if [ -f "miraikakakuapi/websocket_server.pid" ]; then
            WEBSOCKET_PID=$(cat miraikakakuapi/websocket_server.pid)
            if ! ps -p $WEBSOCKET_PID > /dev/null; then
                echo -e "${RED}❌ WebSocket server died, restarting...${NC}"
                start_websocket_server
            fi
        fi

        if [ -f "miraikakakufront/frontend.pid" ]; then
            FRONTEND_PID=$(cat miraikakakufront/frontend.pid)
            if ! ps -p $FRONTEND_PID > /dev/null; then
                echo -e "${RED}❌ Frontend died, restarting...${NC}"
                start_frontend
            fi
        fi
    done
}

# Run main function
main "$@"