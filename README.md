# 🐍 tg_bot_assistant

`tg_bot_assistant` is a Python-based microservice designed to interact with Telegram and manage authorized group members. It works alongside [`tg_bot_backend`](https://github.com/allenflux/tg_bot_backend) to help assign tasks and control permissions in Telegram group chats.

---

## 🌍 Features

- Interfaces with Telegram via Pyrogram
- Extracts and verifies group members
- Supports bot-authenticated login via Telegram Web login code
- Exposes REST API for retrieving member data

---

## 🚀 Quick Start

### 📦 Prerequisites

Before building the Docker image, you **must edit** the `app.py` file to insert your own Telegram API credentials:

```python
api_id = 1233     # <-- Replace with your own API ID
api_hash = 'xxx'  # <-- Replace with your own API hash
```

You can obtain these credentials from https://my.telegram.org.

---

## 🐳 Running with Docker

To build the Docker image:

```bash
docker build -t tg_bot_assistant .
```

To run the service:

```bash
docker run -p 5000:5000 tg_bot_assistant
```

After starting the container, navigate to:

```
http://localhost:5000/login
```

Enter your phone number and the code sent by Telegram to initialize the session file. This step is required before the API becomes functional.

---

## 📖 API Usage

### `GET /get_members`

Retrieves the list of members in a given group.

#### Parameters:

- `group_link`: The public link to the Telegram group (e.g., `https://t.me/mygroup`)

#### Example:

```bash
curl 'http://localhost:5000/get_members?group_link=https://t.me/mygroup'
```

Returns JSON array of usernames or member data.

---

## 🧾 Configuration Notes

- All session files are stored locally in the container volume.
- Multiple sessions or multi-user modes are not supported in the current version.
- Debug logs are printed to stdout.

---

## 🧭 Roadmap

Planned improvements:

- [ ] OAuth-style login with session expiration
- [ ] Support for private group invitation-based access
- [ ] Pagination and filtering on API output
- [ ] Rate limiting and caching

---

## 🤝 Contributing

We welcome contributions! To get started:

```bash
# 1. Fork the repository
# 2. Create your feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes and commit
git commit -am 'Add new feature'

# 4. Push to your fork
git push origin feature/your-feature-name

# 5. Open a Pull Request on GitHub
```

---

## 📄 License

This project is released under the [MIT License](./LICENSE).