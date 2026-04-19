# Contribute to the project
Guide on setting up development environment and contributing to the project.

# Project structure
Overview of the whats and hows work from where. This guide should help with applying change.

## Project root
All local/prodcution devlopment control `./Makefile`

## Project environment
All environment variables and management can be found in `src/utils/`

## Bot source code
All functionalites of the bot can be found in `src/bot`

### Initialization
Creating the bot is configured at `src/bot/client.py`

### Custom handlers
Custom handlers are found at `src/bot/handlers.py`

This is where all the event related handlers are implemented. E.g. `on_message`, `on_member_join`, `on_error`, etc.

### Custom commands
Custom commands are found at `src/bot/commands.py`

To add *prefix* command use:
```python
    @commands.command(name=COMMAND_NAME)
    async def COMMAND_NAME(self, ctx):
        """Custom prefix command description. Usage !CMD"""
```
To add *slash* command use:
```python
    @app_commands.command(name=COMMAND_NAME, description="")
    async def COMMAND_NAME(self, interaction: discord.Interaction):
        """Custom slash command description. Usage /CMD"""
```

### Big clock scheduler flow
- Slash command `/setbigclock` configures guild state in `BIG_CLOCK_LIST_EN`
- Scheduler logic lives in `src/bot/tasks.py`
- Voice helpers live in `src/bot/voice.py`

### Test locations
- Command tests: `tests/bot/test_commands.py`
- Scheduler unit tests: `tests/bot/test_tasks.py`
- Scheduler integration tests: `tests/bot/test_integration_scheduler.py`
- Bot lifecycle/loading tests: `tests/bot/test_client.py`

When changing `/setbigclock`, update command and scheduler tests together.

# Local run and build guide
- `make local` runs `python3 -m src`
- `make build` runs `docker-compose up --build -d`
- `make test` runs `pytest tests/ -v`

Use module-mode execution (`python3 -m src`) to keep package imports consistent.

# Version control guide (Git)
Version control practices adapted in this project

## Pull changes
```bash
git pull --rebase --autostash
```

## Branching
Create a new branch
```bash
git checkout -b develop/my-new-branch
```

## Push changes
After done modifying your changes, add them running:
```bash
git add /path/to/files
```

> [!CAUTION]
> Avoid adding changes running:
> ```bash
> git add .
> ```

Provide a semantic commit message, E.g. `chore, docs, feat, fix, refactor, style, or test`
```
feat: add hat wobble
^--^  ^------------^
|     |
|     +-> Summary in present tense.
|
+-------> Type: chore, docs, feat, fix, refactor, style, or test.
```

Proceed to push running:
```bash
git push -u origin develop/my-new-branch
```

Create a pull request
- Go to GitHub repo, Click `"Compare & pull request"`
- Select "base: `target_branch`", "compare: `develop/my-new-branch`"
- Submit the PR