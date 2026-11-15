# 🎒 E-Learning Academy — v0.2

Python learning project for children from Preschool and Kindergarten through Grade 5. Built using **Flet (UI), FastAPI (REST backend), SQLite (database)** and fully free local tools.

## What's new in 0.2

- **Separate parent registration and login** with email/password (hashed in SQLite).
- **Child registration by a logged-in parent** (display name, username, 4–8 digit PIN, grade, language, emoji avatar). Children then log in independently with username and PIN. Child self-registration is intentionally disabled.
- **Bright, larger touch-friendly welcome, login, dashboard and quiz screens** designed for tablets/laptops.
- **One question at a time**, visual feedback for right/wrong answers, progress bar, stars and repeat challenges.
- **49 new curated topic lessons (7 levels × 7 subjects) and 294 questions**, 6 questions per starter lesson. Existing v0.1 lessons are preserved, so upgraded databases may have additional lessons.
- **Parent lesson builder** can create or edit up to 30 questions per lesson, plus edit child account settings and view progress.
- **Role-scoped API**: parent controls children and lessons; child can submit attempts and view only their own progress. Parents can view progress of children in their family.
- **Upgrade of existing SQLite data**: the first parent registration links v0.1 child profiles to that parent. Parent must open **Manage student accounts → Edit / Set login PIN** for each existing child before they can sign in.

## Important limitations

This is a **local development prototype**, **not a production-ready public platform**. Session tokens are kept in memory; there is no password reset, verification, login throttling, audit trail, HTTPS termination, multi-device session management, or child-safety compliance review. Do **not** expose this API to the public Internet or use a publicly accessible host until those features are designed, implemented and tested. A parent registration is open to anyone who can access the local backend; shared lessons are globally editable by parent accounts in this prototype. Use only on your trusted computer/local environment. Keep child names and login credentials private.

**Not yet included:** real child photos, camera-based recognition (requires your explicit approval), recorded voice greetings, speech-to-text, Urdu/English narration, AI conversations, animations/game engine, real offline sync and mobile packaging validation.

Sample lessons are introductory practice materials, not a complete formally validated curriculum. Parents should review them for their children's age and needs.

## Windows quick start (Python 3.12 standard 64-bit)

Extract the ZIP and open PowerShell in the `learning_academy` folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If you have an **old `.venv` created by free-threaded Python 3.13**, deactivate it, remove only that `.venv` folder and recreate it with the standard Python 3.12 interpreter. The earlier `cp313t` build lacked compatible prebuilt packages and attempted to compile libraries using MSVC.

Start FastAPI in terminal #1:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Leave it running. Swagger API docs: http://127.0.0.1:8000/docs

Start Flet in terminal #2 (activate the same venv):

```powershell
cd D:\Learning\learning_academy
.\.venv\Scripts\Activate.ps1
flet run main.py
```

Browser preview:

```powershell
flet run --web main.py
```

**First-time setup:** From the landing page, choose **Create parent account**, then **Manage student accounts → Register child**. Log out and choose **Student login** using that child's username and PIN. If upgrading from v0.1, your existing child profiles and quiz history are stored in `academy.sqlite3`; first parent registration links those legacy profiles to your parent account, after which you should set a child username and PIN.

## Keep your existing quiz history when upgrading

If you already used v0.1, **back up** your `academy.sqlite3` before replacing code. Extract v0.2 **over the old project folder** (do not delete the SQLite database) or copy the old `academy.sqlite3` into the v0.2 project directory while FastAPI is stopped. Start the new backend: schema updates and question seeding run automatically.

If a child username is not set on an older profile, they can't log in until a parent assigns one in the parent dashboard.

## Running tests

```powershell
python -m pytest -q
```

## Architecture

- `backend/content.py`: ready-made question bank, organized by level and subject.
- `backend/store.py`: database tables, legacy schema upgrade and starter lesson seeding.
- `backend/main.py`: password/PIN hashing, session tokens, authenticated FastAPI endpoints and grading.
- `frontend/api.py`: HTTP JSON client.
- `frontend/main.py`: Flet screens, form inputs, event handlers, guided quiz UI.
- `tests/test_api.py`: backend regression tests.
- `main.py`: desktop/web client entry point.

## Learning goals

Python dataclasses and functions (future), typed models and API validation, SQL migrations, PBKDF2 password hashing, Flet state/controls, HTTP requests, pytest and deployment. Later we can explore offline audio (English/Urdu), AI APIs, embeddings, RAG, agents, evaluations and supervised child-safe conversational tutoring. Face recognition is postponed pending explicit user approval.

## Android note

Android deployment has not been tested. A device cannot reach your laptop's `127.0.0.1`; cross-device access needs deliberate network configuration and security hardening. Do not publish this development backend.

## Licensing

This project's original source is under MIT (see `LICENSE`); dependencies retain their own licenses. No subscription is needed to develop or test locally. Hosting/store distribution may incur independent charges later.
