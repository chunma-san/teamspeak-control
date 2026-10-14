![TeamSpeak Control: animated project banner](assets/banner.svg)

# TeamSpeak Control

A Discord control interface for configured TeamSpeak audio-bot containers and an announcement timer.

**Runtime:** Python 3.11+ · **Configuration:** environment variables · **Deployment:** self-hosted

## Quick start

The supported deployment target is Linux. Create an isolated Python environment:

```sh
python3 -m venv venv
. venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env first. Use shell-compatible quoting for JSON and values with spaces.
set -a
. ./.env
set +a
python control.py
```

Only source a configuration file you created and trust. Starting the application can connect to external services; configure credentials and destinations first.

## Usage

Set CONTROL_ROLE_ID for guild access and DM_CONTROL_USER_ID for optional direct-message access. TS_BOT_CONTAINERS is a JSON array of container names, for example `["audio-bot-1"]`. The command prefix is `;`. Enable the Message Content intent in the Discord Developer Portal. Commands: `;bots` starts configured containers; `;start` starts announcements; `;stop` stops announcements; `;off` stops announcements and containers; `;status` reports timer reachability and configured container counts.

## Configuration

`.env.example` contains placeholders only. Real credentials, IDs, storage locations and account settings belong in your private local configuration.

| Variable | Requirement |
| --- | --- |
| `CONTROL_ROLE_ID` | Discord role permitted to control audio bots. |
| `DISCORD_TOKEN` | Discord bot token; keep it secret. |
| `DM_CONTROL_USER_ID` | User permitted to send control commands in DMs. |
| `TS_BOT_CONTAINERS` | JSON array of audio-bot container names. |

## How it works and operational notes

Requires Linux, Docker CLI access and the timer control FIFO at `/run/teamspeak-ts-timer/control`. Docker access is privileged. The timer and its audio-bot instances must be deployed separately.

## Project layout

- Source files implement the application and integrations.
- `requirements.txt` or the project file declares dependencies.
- `.env.example` documents configuration names without live values.
- `.gitignore` excludes credentials, sessions, generated data and build output.
- `assets/banner.svg` is an original animated vector illustration. It has a static fallback and respects reduced-motion preferences in supporting viewers.

## Verification

See [VALIDATION.md](VALIDATION.md) for the checks performed on this publication snapshot and the remaining deployment checks. A source check is not an end-to-end test of Discord, Telegram, music sites or your host.

## Privacy and upstream services

This repository is a configurable source distribution. It does not include a production database, personal saved-link collection, message archive, credentials, media library or existing Git history. Review local changes before committing them.

Third-party APIs, libraries and products remain the work of their respective maintainers. Review their terms and licenses before redistribution or deployment. The original project artwork is stored locally; it does not depend on a remote GIF or tracking service.
