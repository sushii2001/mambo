# Contribute to the project
Guide on setting up development environment and contributing to the project.

# Prerequisite
- Initial steps require to setup before getting started

## Discord developer portal
- Sign up [here](https://discord.com/developers)
- Create your bot
- Set OAuth2:
    - application.commands
    - bot
    - Administrator
    - // Copy URL link and invite to your server
- Enable Intents:
    - Server Members
    - Message Content
    - Presence

## Clone the Project
- Github [link](https://github.com/sushii2001/mambo.git)
- Make a copy of `.env_sample` to `.env`

## Python setup
- Install Python3
- (Optional) Install `venv` with pip from Python for package management
- Install Python packages running:
    ```bash
    pip install -r requirements.txt
    ```

# Building and Running locally
Checkout the avaliable commands in the `Makefile`

## Build
Run
```bash
make start
```

## Test
Run
```bash
make test
```

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