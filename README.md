# Mambo
A discord bot for fun

# Invite Mambo to your server
Invite [link](https://discord.com/oauth2/authorize?client_id=1462368773104210116&permissions=8&integration_type=0&scope=applications.commands+bot)

# Features
 - [ ] Find food for user
 - [x] Have a big clock ring every hour

> [!IMPORTANT]
> Prerequisite & Limitations:
> Initial steps require to setup before getting started
> - Currently tested on `Linux`/`WSL` setup only. Welcome to contribute support for Windows/macOS
> - Ensure `Docker` is installed. Checkout [here](https://docs.docker.com/desktop/setup/install/windows-install/)
> Install Python3, (Optional) install `venv` with pip for package management
> Install Python packages running:
> ```bash
> pip install -r requirements.txt
> ```
> Install FFmpeg for audio input
> ```bash
> sudo apt install ffmpeg
> ```

# Quick start guide
Launch the discord bot locally.
- Sign up discord developer portal [here](https://discord.com/developers/home)
- Create a new bot/app
- Invite to your server
    - Go to `Applications` > `Overview` > `OAuth2` > `OAuth2 URL Generator`
    - Tick `application.commands`, `bot`,
    - Copy the `Generated URL` paste it in your browser
- Generate your bot's `DISCORD_TOKEN`
    - Go to `Bot` > `Token`
    - Press `Reset Token` and save it to replace into the repo's `.env`

## Setup
Clone the repo and make a copy of `.env_sample` to `.env`. Fill in the values accordingly.
```
DISCORD_TOKEN=PLACE_HOLDER  # Replace with generated token from discord developer portal
LOGGING_LEVEL=INFO
WEB_HOST=0.0.0.0
WEB_PORT=8080
```

## Building and Running locally
Run the following or check the avaliable commands in the `Makefile`.
```bash
make help
```

### Local build
Local build
```bash
make local
```

### Test
Run
```bash
make test
```

### Docker simulation
Build and run
```bash
make build
```
Remove build
```bash
make clean
```

# Contribution
Checkout the developer contribution guide in `CONTRIBUTE.md`