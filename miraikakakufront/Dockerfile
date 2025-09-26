FROM node:18-alpine AS base

# Install system dependencies
RUN apk add --no-cache wget libc6-compat

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install && npm install react-is

# Copy source code
COPY . .

# Set environment variables
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start the application
CMD ["npm", "start"]