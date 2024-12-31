# CryptoSim: Modern Microservices Mining Simulator

A modern, educational cryptocurrency mining simulator built with microservices architecture. This project demonstrates key concepts in distributed systems, containerization, and cloud-native applications.

## 🌟 Features

This simulator recreates the cryptocurrency mining process through a distributed system of microservices:

- Random Number Generation Service (Python/FastAPI)
- Hash Computing Service (Go)
- Worker Coordination Service (Python/FastAPI)
- Real-time Monitoring Dashboard (React/Tailwind)
- Redis-based Data Storage

## 🚀 Technology Stack

- **Backend Services**: Python 3.11 with FastAPI
- **Frontend**: React 18 with Tailwind CSS
- **Database**: Redis
- **Container Runtime**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions

## 🛠️ Architecture

```
                   ┌──────────┐
                   │  WebUI   │
                   └────┬─────┘
                        │
                   ┌────┴─────┐
                   │  Redis   │
                   └────┬─────┘
                        │
┌──────────┐      ┌────┴─────┐      ┌──────────┐
│   RNG    │◄─────│  Worker  │─────►│  Hasher  │
└──────────┘      └──────────┘      └──────────┘
```

## 🎯 Educational Goals

This project serves as a practical demonstration of:

- Microservices Architecture
- Container Orchestration
- Service Discovery
- Load Balancing
- Horizontal Scaling
- Monitoring and Metrics
- CI/CD Practices

## 🚦 Getting Started

### Prerequisites

- Docker Desktop
- kubectl
- Node.js 18+
- Python 3.11+

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/syntax2/cryptosim.git
   cd cryptosim
   ```

2. Start with Docker Compose:
   ```bash
   docker compose up
   ```

3. Access the WebUI:
   Open `http://localhost:3000` in your browser

### Kubernetes Deployment

```bash
kubectl apply -f k8s/
```

## 📊 Performance Monitoring

Monitor your mining operation through the web interface at `http://localhost:3000`, which provides:

- Real-time mining rate
- System resource usage
- Service health status
- Historical performance data


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by DockerCoin Miner
- Built with modern best practices and current technology stack
- Designed for educational purposes

## 📧 Contact

Your Name - Ashish Kadian [ashishkadian884@gmail.com]
Project Link: [https://github.com/syntax2/cryptosim](https://github.com/syntax2/cryptosim)