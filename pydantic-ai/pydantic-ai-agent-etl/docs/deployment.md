# Deployment Guide

This guide covers deployment configurations and procedures for the FastAPI boilerplate.

## Environment Setup

### Environment Variables

Create a `.env` file with the following configurations:

```env
# Application
APP_NAME="FastAPI Boilerplate"
APP_DESCRIPTION="FastAPI Boilerplate for Microservices"
APP_VERSION="0.1.0"
ENVIRONMENT="development"  # development, staging, production
APP_PORT=8000

# FastStream (Kafka)
FASTSTREAM_PROVIDER="localhost:9092"
FASTSTREAM_ENABLE=true
```

### Environment Types

The application supports three environment types:
1. Development (`development`)
2. Staging (`staging`)
3. Production (`production`)

Each environment can have different configurations by creating specific `.env` files:
- `.env.development`
- `.env.staging`
- `.env.production`

## Docker Deployment

### Local Development

1. Build and start services:
```bash
docker-compose up -d --build
```

2. Services included:
   - FastAPI application
   - Kafka
   - Zookeeper

### Production Deployment

1. Create production Docker Compose file `docker-compose.prod.yaml`:
```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - ENVIRONMENT=production
      - FASTSTREAM_PROVIDER=kafka:9092
    ports:
      - "8000:8000"
    depends_on:
      - kafka

  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper

  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
```

2. Deploy using production configuration:
```bash
docker-compose -f docker-compose.prod.yaml up -d
```

## Kubernetes Deployment

### Prerequisites

1. Kubernetes cluster
2. kubectl configured
3. Kafka cluster (or use a managed service)

### Deployment Files

1. Create application deployment (`k8s/deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi-app
        image: your-registry/fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: FASTSTREAM_PROVIDER
          value: "kafka-service:9092"
```

2. Create service (`k8s/service.yaml`):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi-app
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

3. Deploy to Kubernetes:
```bash
kubectl apply -f k8s/
```

## Monitoring and Logging

### Application Logs

1. Docker logs:
```bash
# View application logs
docker-compose logs -f app

# View Kafka logs
docker-compose logs -f kafka
```

2. Kubernetes logs:
```bash
# View pod logs
kubectl logs -f deployment/fastapi-app

# View logs for specific pod
kubectl logs -f pod/fastapi-app-xyz
```

### Health Checks

The application provides health check endpoints:

1. Liveness probe: `/health/live`
2. Readiness probe: `/health/ready`

Configure in Kubernetes:
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

## Scaling

### Docker Compose Scaling

Scale services using Docker Compose:
```bash
docker-compose up -d --scale app=3
```

### Kubernetes Scaling

Scale deployment:
```bash
kubectl scale deployment fastapi-app --replicas=5
```

## Backup and Recovery

### Kafka Topics

1. Create topic backup:
```bash
kafka-topics.sh --bootstrap-server kafka:9092 --describe > topics-backup.txt
```

2. Export messages:
```bash
kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic your-topic --from-beginning \
  --property print.key=true \
  --property print.timestamp=true \
  > messages-backup.txt
```

## Security Considerations

1. **Environment Variables**
   - Use secrets management in production
   - Never commit .env files to version control
   - Rotate sensitive credentials regularly

2. **Network Security**
   - Use TLS for all communications
   - Implement proper firewall rules
   - Use private networks when possible

3. **Access Control**
   - Implement authentication if needed
   - Use proper RBAC in Kubernetes
   - Secure Kafka with authentication

## Troubleshooting

Common issues and solutions:

1. **Kafka Connection Issues**
   - Check FASTSTREAM_PROVIDER configuration
   - Verify Kafka is running and accessible
   - Check network connectivity

2. **Application Startup Failures**
   - Verify environment variables
   - Check logs for startup errors
   - Ensure dependencies are available

3. **Performance Issues**
   - Monitor resource usage
   - Check for memory leaks
   - Optimize Kafka consumer configurations