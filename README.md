# voizchat

Voizchat is a real-time communication platform that enables users to connect with friends through messaging, voice calls, and a collaborative whiteboard. Built with a modern tech stack, Voizchat offers an intuitive and seamless experience for real-time collaboration.

## Features
- **User Management**: Add and manage friends.
- **Messaging**: Send and receive instant messages.
- **Voice Calls**: Real-time audio communication.
- **Whiteboard**: Collaborate using an interactive whiteboard.

## Tech Stack
- [![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/)
- [![Vue.js (TypeScript)](https://img.shields.io/badge/Vue.js%20(TypeScript)-35495E?style=for-the-badge&logo=vue.js&logoColor=4FC08D)](https://vuejs.org/)
- [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
- [![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)
- [![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

## Installation with **Docker**

### Prerequisites
Ensure you have the following installed on your system:
- [![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
- [![Docker Compose](https://img.shields.io/badge/Docker--Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/)

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/pixhy/voizchat.git
   cd voizchat
   ```
2. Build and start the application using Docker Compose:
   ```sh
   docker-compose up --build
   ```
3. The frontend and backend services will start automatically.
4. Access the application in your web browser at `http://localhost:3000` (or the configured port).

## Native Installation (Without Docker)

### Prerequisites
Ensure you have the following installed on your system:
- [![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/)
- [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
- [![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)

## Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/pixhy/voizchat.git
   cd voizchat
   ```
2. Start the backend:
   ```sh
   cd server
   pyhton -m venv venv
   venv\Scipts\active # Windows
   source venv/bin/active # Linux/Mac
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
3. Start the frontend:
   ```sh
   cd ../webclient
   npm install
   npm run dev
   ```
4. Open the app in your browser:
   ```sh
   http://localhost:3000
   ```

## Usage
- Register and log in to your account.
- Add friends and start messaging them.
- Initiate voice calls for real-time conversations.
- Use the whiteboard for collaboration.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to change.

## Contact
For any inquiries or support, feel free to reach out via the repository’s issue tracker.

## Develpoers
Voizchat is developed and maintained by:

- **[pixhy](https://github.com/pixhy)**  
  **[LinkedIn Profile](https://www.linkedin.com/in/tunde-bak/)**

- **[prvics](https://github.com/prvics)**  
  **[LinkedIn Profile](https://www.linkedin.com/in/prvics/)**


