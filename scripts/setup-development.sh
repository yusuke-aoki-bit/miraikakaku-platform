#!/bin/bash
# Development Environment Setup Script for MiraiKakaku

set -e  # Exit on any error

echo "🚀 Setting up MiraiKakaku development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js (v18+) first."
        exit 1
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi

    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi

    print_success "All prerequisites are installed."
}

# Setup environment files
setup_environment_files() {
    print_status "Setting up environment files..."

    # API environment
    if [ ! -f "miraikakakuapi/.env" ]; then
        cp config/templates/api.env.template miraikakakuapi/.env
        print_warning "Created miraikakakuapi/.env from template. Please update with your actual values."
    fi

    # Batch environment
    if [ ! -f "miraikakakubatch/.env" ]; then
        cp config/templates/batch.env.template miraikakakubatch/.env
        print_warning "Created miraikakakubatch/.env from template. Please update with your actual values."
    fi

    # Docker environment
    if [ ! -f ".env.docker.local" ]; then
        cp .env.docker .env.docker.local
        print_warning "Created .env.docker.local from template. Please update with your actual values."
    fi

    print_success "Environment files setup completed."
}

# Install API dependencies
setup_api() {
    print_status "Setting up API dependencies..."

    cd miraikakakuapi

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Created Python virtual environment for API."
    fi

    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r functions/requirements.txt
    pip install pytest pytest-cov black isort flake8 bandit

    deactivate
    cd ..

    print_success "API dependencies installed."
}

# Install Batch dependencies
setup_batch() {
    print_status "Setting up Batch dependencies..."

    cd miraikakakubatch

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Created Python virtual environment for Batch."
    fi

    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r functions/requirements.txt
    pip install pytest pytest-cov black isort flake8 bandit

    deactivate
    cd ..

    print_success "Batch dependencies installed."
}

# Install Frontend dependencies
setup_frontend() {
    print_status "Setting up Frontend dependencies..."

    cd miraikakakufront

    # Install npm dependencies
    npm install

    # Install additional dev dependencies
    npm install --save-dev @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-config-prettier

    cd ..

    print_success "Frontend dependencies installed."
}

# Setup pre-commit hooks
setup_pre_commit() {
    print_status "Setting up pre-commit hooks..."

    # Install pre-commit globally
    pip install pre-commit

    # Install pre-commit hooks
    pre-commit install

    print_success "Pre-commit hooks installed."
}

# Setup database (for local development)
setup_database() {
    print_status "Setting up local database..."

    # Create logs directory
    mkdir -p logs

    # Setup local PostgreSQL with Docker
    docker run --name miraikakaku-postgres \
        -e POSTGRES_DB=miraikakaku_dev \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=dev_password \
        -p 5432:5432 \
        -d postgres:13

    print_success "Local PostgreSQL database setup completed."
    print_warning "Database credentials: postgres/dev_password@localhost:5432/miraikakaku_dev"
}

# Run tests to verify setup
verify_setup() {
    print_status "Verifying setup by running tests..."

    # Test API
    cd miraikakakuapi
    source venv/bin/activate
    pytest tests/ --tb=short || print_warning "API tests failed - check your configuration"
    deactivate
    cd ..

    # Test Batch
    cd miraikakakubatch
    source venv/bin/activate
    pytest tests/ --tb=short || print_warning "Batch tests failed - check your configuration"
    deactivate
    cd ..

    # Test Frontend
    cd miraikakakufront
    npm run lint || print_warning "Frontend linting failed - check your code"
    npm run build || print_warning "Frontend build failed - check your configuration"
    cd ..

    print_success "Setup verification completed."
}

# Main execution
main() {
    print_status "Starting MiraiKakaku development environment setup..."

    check_prerequisites
    setup_environment_files
    setup_api
    setup_batch
    setup_frontend
    setup_pre_commit

    # Optional database setup
    read -p "Do you want to setup a local PostgreSQL database? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_database
    fi

    verify_setup

    print_success "🎉 Development environment setup completed!"
    echo
    echo "Next steps:"
    echo "1. Update environment files with your actual configuration:"
    echo "   - miraikakakuapi/.env"
    echo "   - miraikakakubatch/.env"
    echo "   - .env.docker.local"
    echo
    echo "2. Start development servers:"
    echo "   - API: cd miraikakakuapi && source venv/bin/activate && python functions/main.py"
    echo "   - Frontend: cd miraikakakufront && npm run dev"
    echo "   - Full stack: docker-compose up"
    echo
    echo "3. Run tests:"
    echo "   - make test (if Makefile exists)"
    echo "   - Or run tests individually in each service directory"
    echo
    print_success "Happy coding! 🚀"
}

# Run main function
main "$@"