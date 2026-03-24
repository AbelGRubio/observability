# Backend DAS Device API

## 📋 Project Overview

`backend-das-device` is a RESTful API service designed to manage and control Distributed Acoustic Sensing (DAS) equipment. This backend service provides endpoints to configure DAS devices, control signal processing operations, and handle alarm notifications.

## 🏗️ Project Structure

```
backend-das-device/
├── src/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── configuration.py
│   │   │   │   ├── processing.py
│   │   │   │   └── alarms.py
│   │   │   └── dependencies.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # Configuration management
│   │   │   ├── security.py      # Authentication & authorization
│   │   │   └── das_controller.py # DAS device control logic
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py       # Pydantic models
│   │   │   └── database.py      # Database models
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── signal_processor.py
│   │       ├── alarm_manager.py
│   │       └── device_communication.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_services.py
│   │   └── conftest.py
│   ├── scripts/
│   │   ├── startup.sh
│   │   └── deploy.py
│   └── static/
│       └── docs/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── config.yaml
└── README.md
```

## 🚀 API Endpoints

### Configuration Management

#### Get Current Configuration
```http
GET /api/v1/configuration
```
**Response:**
```json
{
  "device_id": "DAS-001",
  "sample_rate": 1000,
  "sensitivity": 0.85,
  "filter_settings": {
    "low_cut": 1.0,
    "high_cut": 100.0,
    "filter_type": "bandpass"
  },
  "alarm_thresholds": {
    "amplitude": 2.5,
    "frequency": 50.0,
    "duration": 5.0
  }
}
```

#### Update Configuration
```http
PUT /api/v1/configuration
Content-Type: application/json

{
  "sample_rate": 2000,
  "sensitivity": 0.9,
  "filter_settings": {
    "low_cut": 0.5,
    "high_cut": 150.0,
    "filter_type": "highpass"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Configuration updated successfully",
  "updated_fields": ["sample_rate", "sensitivity", "filter_settings"]
}
```

### Signal Processing Control

#### Start Signal Processing
```http
POST /api/v1/processing/start
Content-Type: application/json

{
  "processing_mode": "realtime",
  "data_output": "websocket",
  "buffer_size": 1024
}
```

**Response:**
```json
{
  "status": "started",
  "processing_id": "proc_12345",
  "started_at": "2024-01-15T10:30:00Z",
  "estimated_memory_usage": "256MB"
}
```

#### Stop Signal Processing
```http
POST /api/v1/processing/stop
```

**Response:**
```json
{
  "status": "stopped",
  "processing_id": "proc_12345",
  "stopped_at": "2024-01-15T10:35:00Z",
  "total_processing_time": "5 minutes"
}
```

#### Get Processing Status
```http
GET /api/v1/processing/status
```

**Response:**
```json
{
  "status": "running",
  "processing_id": "proc_12345",
  "started_at": "2024-01-15T10:30:00Z",
  "data_points_processed": 150000,
  "current_throughput": "1000 samples/sec"
}
```

### Alarm Management

#### Send Alarm Command
```http
POST /api/v1/alarms/send
Content-Type: application/json

{
  "alarm_type": "amplitude_threshold",
  "severity": "high",
  "location": "segment_45",
  "timestamp": "2024-01-15T10:32:15Z",
  "metadata": {
    "amplitude": 3.2,
    "frequency": 45.5,
    "duration": 2.1
  }
}
```

**Response:**
```json
{
  "alarm_id": "alarm_67890",
  "status": "sent",
  "server_response": "Alarm received and logged",
  "timestamp": "2024-01-15T10:32:16Z"
}
```

#### Get Alarm History
```http
GET /api/v1/alarms/history?hours=24&severity=high
```

**Query Parameters:**
- `hours`: Time range in hours (default: 24)
- `severity`: Filter by severity level (low, medium, high, critical)

**Response:**
```json
{
  "alarms": [
    {
      "alarm_id": "alarm_67890",
      "type": "amplitude_threshold",
      "severity": "high",
      "timestamp": "2024-01-15T10:32:15Z",
      "location": "segment_45",
      "resolved": false
    }
  ],
  "total_count": 1,
  "time_range": "24 hours"
}
```

### Device Information

#### Get Device Status
```http
GET /api/v1/device/status
```

**Response:**
```json
{
  "device_id": "DAS-001",
  "status": "online",
  "firmware_version": "2.1.4",
  "uptime": "15 days, 6 hours",
  "cpu_usage": 45.2,
  "memory_usage": 62.8,
  "temperature": 42.5,
  "last_calibration": "2024-01-10T08:00:00Z"
}
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.9+
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy (if using database)

### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/your-org/backend-das-device.git
cd backend-das-device
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your settings
```

4. **Run the application:**
```bash
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Deployment

```bash
docker-compose up -d
```

## 🛡️ Authentication

The API uses JWT tokens for authentication. Include the token in the header:

```http
Authorization: Bearer <your_jwt_token>
```

## 📊 WebSocket Support

### Real-time Data Streaming

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/data');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received DAS data:', data);
};
```

### Real-time Alarms

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/alarms');

ws.onmessage = function(event) {
  const alarm = JSON.parse(event.data);
  console.log('New alarm detected:', alarm);
};
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

Test specific components:

```bash
pytest tests/test_api.py -v
pytest tests/test_services.py -v
```

## 🔄 API Workflow Example

1. **Configure the DAS device:**
```bash
curl -X PUT http://localhost:8000/api/v1/configuration \\
  -H "Content-Type: application/json" \\
  -d '{"sample_rate": 2000, "sensitivity": 0.9}'
```

2. **Start signal processing:**
```bash
curl -X POST http://localhost:8000/api/v1/processing/start \\
  -H "Content-Type: application/json" \\
  -d '{"processing_mode": "realtime"}'
```

3. **Monitor processing status:**
```bash
curl http://localhost:8000/api/v1/processing/status
```

4. **Send alarm when event detected:**
```bash
curl -X POST http://localhost:8000/api/v1/alarms/send \\
  -H "Content-Type: application/json" \\
  -d '{"alarm_type": "amplitude_threshold", "severity": "high", "location": "segment_45"}'
```

5. **Stop processing:**
```bash
curl -X POST http://localhost:8000/api/v1/processing/stop
```

## 📈 Monitoring & Logging

### Health Check
```http
GET /health
```

### Metrics Endpoint
```http
GET /metrics
```

### Log Files
- Application logs: `logs/app.log`
- Access logs: `logs/access.log`
- Error logs: `logs/error.log`

## 🔗 Dependencies

### Core Dependencies
- `fastapi>=0.104.0` - Web framework
- `uvicorn>=0.24.0` - ASGI server
- `pydantic>=2.0.0` - Data validation
- `python-jose[cryptography]` - JWT tokens
- `python-multipart` - Form data handling

### Optional Dependencies
- `sqlalchemy>=2.0.0` - Database ORM
- `websockets>=12.0` - WebSocket support
- `pytest>=7.0.0` - Testing framework
- `requests>=2.31.0` - HTTP client

## 🐛 Troubleshooting

### Common Issues

1. **Device Connection Failed**
   - Check physical connections
   - Verify device power and status
   - Review communication protocol settings

2. **High Memory Usage**
   - Reduce buffer sizes
   - Adjust processing parameters
   - Monitor system resources

3. **Alarm Notifications Not Sent**
   - Verify server connectivity
   - Check alarm threshold settings
   - Review network configuration

### Debug Mode

Enable debug mode for detailed logging:

```bash
UVICORN_LOG_LEVEL=debug uvicorn src.app.main:app --reload
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check API documentation at `/docs` endpoint
- Review troubleshooting guide in documentation

---

**API Version:** v1.0.0
**Last Updated:** January 2024
**Maintainer:** DAS Development Team
