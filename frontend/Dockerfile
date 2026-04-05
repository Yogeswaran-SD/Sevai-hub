# Frontend Dockerfile for Sevai Hub
# Multi-stage build for optimized production image

FROM node:20-alpine as builder

# Set working directory
WORKDIR /app

# Accept build arguments
ARG VITE_API_URL=http://localhost:8000
ARG VITE_ENVIRONMENT=development

# Set as environment variables for build
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_ENVIRONMENT=$VITE_ENVIRONMENT

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy application source
COPY frontend/ .

# Build the Vite application with environment variables
RUN npm run build

# ============================================================================
# Production stage - serve with nginx
FROM nginx:alpine

# Install bash for better debugging (optional)
RUN apk add --no-cache bash curl

# Copy nginx configuration
COPY frontend/nginx.conf /etc/nginx/nginx.conf
COPY frontend/default.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Create non-root user for security
RUN addgroup -g 101 -S nginx || true

# Expose port
EXPOSE 80
EXPOSE 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
