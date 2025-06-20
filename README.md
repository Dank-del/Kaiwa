# Kaiwa

**Kaiwa** is an experimental chat application built with Django Channels, offering real-time messaging with WebSocket support. The project aims to provide a modern, responsive messaging experience and serves as a playground for new chat features and UI/UX experiments.

## Features

- **Real-Time Messaging:** Instant message delivery using Django Channels and WebSockets.
- **Room-Based Chats:** Create and join chat rooms, manage membership, and exchange messages in real-time.
- **Direct Messaging:** Send private messages to other users.
- **User Authentication:** Register, log in, and manage user profiles with password change support.
- **Invite Links:** Generate and share invite links to bring others into chat rooms.
- **Responsive UI:** Clean and modern interface designed with [BeerCSS](https://www.beercss.com/) for optimal usability across devices.
- **Profile Management:** Update profile information and change your password securely.

## Demo

The latest version is live at: [https://kaiwa.sayanbiswas.in/chat](https://kaiwa.sayanbiswas.in/chat)

## Getting Started

### Prerequisites

- Python 3.8+
- [Django 5.x](https://docs.djangoproject.com/en/5.0/)
- [Django Channels](https://channels.readthedocs.io/en/latest/)
- [Daphne](https://github.com/django/daphne) (ASGI server)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Dank-del/Kaiwa.git
   cd Kaiwa
   ```

2. **Install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

5. **Access the app:**  
   Visit `http://127.0.0.1:8000/chat/` in your browser.

### WebSocket Support

Kaiwa uses Django Channels for WebSocket connections. For production, use an ASGI server like Daphne:

```bash
daphne kaiwa.asgi:application
```

## Project Structure

```
kaiwa/
  asgi.py            # ASGI entrypoint for Channels
  settings.py        # Django settings
  templates/         # Base templates and layout
chat/
  migrations/
  templates/         # Chat room, DM, and user interface templates
  ...
requirements.txt     # All Python dependencies
```

## Main Technologies

- **Backend:** Django, Django Channels, Daphne
- **Frontend:** BeerCSS, HTML5, JavaScript
- **WebSocket:** Real-time communication via Django Channels

## Contributing

Contributions are welcome! Please open issues or submit pull requests for new features, bug fixes, or suggestions.

## License

This project is for experimental and educational purposes. No license is currently provided.

## Author

Developed by [Sayan Biswas](https://github.com/Dank-del)

---

> _Kaiwa_ means "conversation" in Japanese. Enjoy chatting!
