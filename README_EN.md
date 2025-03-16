# TeleRelay

A Python-based Telegram channel forwarding tool that uses a regular user account (not a bot) to monitor specified channels and forward messages to other channels.

## Main Features

- Monitor multiple Telegram channels
- Forward messages to multiple target channels
- Manage through a Web interface
- View forwarding history and statistics
- Display the number of messages forwarded today
- Cache dialog list to local database
- Logging system with file rotation
- Custom port configuration
- Docker support for easy deployment
- GitHub Actions automated build

## Installation and Configuration

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the `.env.example` file to `.env` and fill in the following information:

```
# Telegram API Configuration
API_ID=your_api_id
API_HASH=your_api_hash
PHONE=your_phone_number (including country code, e.g., +12025550123)

# Flask Configuration
SECRET_KEY=your_secret_key
DATABASE_URI=sqlite:///telegram_forwarder.db

# Optional Configuration
PORT=5000  # Web service port, default is 5000
```

About API_ID and API_HASH:
1. Visit https://my.telegram.org/ and log in
2. Go to "API development tools"
3. Create a new application to get API_ID and API_HASH

### 3. Run the Application

Standard launch:
```bash
python app.py
```

Launch with a specific port:
```bash
# Method 1: Via command line argument
python app.py 8080

# Method 2: Via environment variable
PORT=8080 python app.py
```

The application will start on the specified port, default is http://127.0.0.1:5000. When using a custom port, the access address will change accordingly.

## Docker Deployment

The project supports Docker deployment, providing a simpler installation and management method.

### Prerequisites

1. Install Docker and Docker Compose
2. Configure the `.env` file (same as configuration above)

### Start with Docker

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

### Use Pre-built Docker Hub Image

You can directly use our pre-built Docker image:

```bash
# Download and start (replace username with actual username)
docker run -d --name telerelay \
  -p 5000:5000 \
  -v ./logs:/app/logs \
  -v ./data:/app/data \
  -v ./.env:/app/.env \
  -v ./sessions:/app/sessions \
  --restart unless-stopped \
  username/telerelay:latest
```

### Docker Configuration Details

Docker deployment automatically maps the following:
- Port: Default 5000 port (can be modified with PORT in .env)
- Log directory: `./logs` → `/app/logs`
- Database: `./data` → `/app/data`
- Configuration file: `./.env` → `/app/.env`
- Telegram sessions: `./sessions` → `/app/sessions`

You can customize these mappings by modifying `docker-compose.yml`.

## GitHub Actions Automated Build

This project uses GitHub Actions to automatically build and publish Docker images to Docker Hub.

### Automation Workflow

1. The build is automatically triggered when code is pushed to the main branch
2. When a version tag is created (e.g., v1.0.0), a versioned image is automatically built
3. Images are automatically pushed to Docker Hub

### How to Use

To enable automated builds in your own GitHub repository, you need to set the following Secrets:

1. `DOCKERHUB_USERNAME`: Docker Hub username
2. `DOCKERHUB_TOKEN`: Docker Hub access token (not your password)

How to set up:
1. On your GitHub repository page, click "Settings"
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret" to add the two keys above

## Usage Guide

1. When running for the first time, you will be asked to verify your Telegram account. Please follow the prompts.
2. In the Web interface, go to the "Channel Management" page to add channels to monitor and forward.
3. Click "Start Service" to begin monitoring and forwarding.
4. Use the "Sync All Dialogs" button on the Channel Management page to retrieve all channels and groups.

## Logging System

The system has a comprehensive logging function. All logs are stored in the `logs` directory:
- `telegram_forwarder.log`: Regular operation logs (INFO level and above)
- `error.log`: Error logs only (ERROR level)

Log features:
- Automatic rotation: Maximum 5MB per log file
- History retention: Keeps the most recent 10 log files
- Hierarchical recording: Detailed debug information is displayed only in the console

## Notes

- Using a regular user account for automated mass forwarding may violate Telegram's Terms of Service. Please use with caution.
- Channel ID format is typically `-100xxxxxxxxx`, or you can use the `@username` format.
- Make sure the account has joined both source and target channels and has sufficient permissions.
- When deploying with Docker, you need to verify your Telegram account on first startup. Please check the logs for instructions.

## FAQ

1. How to get a channel ID?
   - Use the "Sync All Dialogs" feature on the Channel Management page to automatically retrieve
   - Or forward a message from the channel to @username_to_id_bot
   - Or in the web version of Telegram, the numeric part of the channel link is the ID

2. Program cannot connect to Telegram?
   - Check if API_ID and API_HASH are correct
   - Confirm that the network connection is normal
   - Check the logs/error.log file for detailed error information

3. Cannot forward messages?
   - Make sure the account has joined both source and target channels
   - Check if you have forwarding permissions
   - Check the application logs for detailed error information
   
4. How to get all channels and groups?
   - Click the "Sync All Dialogs" button on the Channel Management page
   - The synchronization process may take some time, please be patient
   - Synchronized data will be cached to the local database for faster access

5. How to verify Telegram account when using Docker?
   - View container logs when first starting: `docker-compose logs -f`
   - Follow the prompts in the logs to enter the verification code
   - You can use `docker-compose exec telerelay bash` to enter the container for operation

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2023-2025 YanYu (www.yanyuwangluo.cn) 