# 🎒 E-Learning Academy — Python learning project (v0.1)

A Python-first, family-focused educational application for Preschool, Kindergarten and Grades 1–5.

## Features that work in v0.1

- Android/Windows-friendly **Flet UI source**, also intended for use in a browser (not packaged or device-tested yet)
- Seven grade levels (Preschool, Kindergarten, Grades 1–5)
- Seven subjects (English, Mathematics, Urdu, Science, General Knowledge, Islamiyat, Computer)
- Child profiles with a nickname, **avatar emoji**, grade and English/Urdu preference
- 14 seeded sample lessons, quizzes, scored attempts, stars and per-child progress
- PIN-gated parent lesson creator/editor with multiple questions, and delete
- **FastAPI + SQLite** API, automated API tests, JSON validation

## Not yet implemented

- Real child photographs/camera capture, automatic face recognition (requires parent approval)
- Spoken greetings, audio narration, Urdu/English TTS and microphone conversations
- Animations beyond standard UI interactions, drag-and-drop games
- Offline synchronization, production authentication, secure public hosting
- AI tutor, LLMs, RAG, agents and cloud deployment

**Do not expose this prototype to the public internet.** The parent PIN is for a trusted local demo, not a production security system, and learner endpoints are not authenticated. Use a stronger production access model before public launch. No photo/biometric data is collected in this build.

## Run locally on Windows

Python 3.11+ recommended. From the extracted `learning_academy` directory:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:ACADEMY_PARENT_PIN = "CHANGE-THIS-TO-YOUR-OWN-PIN"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open **another PowerShell terminal**, activate the same virtual environment, and run:

```powershell
flet run main.py
```

For browser testing instead:

```powershell
flet run --web main.py
```

Backend documentation: <http://127.0.0.1:8000/docs>

If PowerShell blocks activation, use the `.venv\Scripts\python.exe` and `.venv\Scripts\flet.exe` paths directly, or adjust your process execution policy appropriately.

**Why two processes?** The frontend calls FastAPI using Python `requests`. This keeps the Python UI, REST APIs and database as separate learning areas. The backend defaults to localhost (not reachable by another device). Later we'll add controlled LAN testing and mobile packaging.

## Test backend

```powershell
python -m pytest -q
```

## Android and deployment notes

Source is structured for Flet. **No APK/EXE has been built or tested** in this environment. Building with Flet requires the appropriate Flutter/Android toolchain and further configuration. An Android app cannot call the Windows machine's `127.0.0.1`; configure `ACADEMY_API_URL` with a reachable, appropriately secured backend address for device testing. Do not expose the demo PIN or API to the internet.

## Learning roadmap

1. Python classes, module imports, types, exceptions, collections — explore `backend/store.py`.
2. FastAPI route handlers, Pydantic validation and HTTP codes — explore `backend/main.py`.
3. SQL tables, keys, migrations (future) — explore `backend/store.py`.
4. Flet event handling, UI state and forms — explore `frontend/main.py`.
5. Unit tests, validation and edge cases — explore `tests/test_api.py`.
6. Next: voice narration and static learning assets; real photos with deletion; robust parent access.
7. Later: LLM APIs, grounded RAG content, speech models, evaluation and supervised AI tutor.

## License

The source code in this project is provided under the MIT License (see LICENSE). Third-party framework and content licenses remain their own. Before selling or publishing, review licenses of all future assets, AI models, fonts, audio, and other dependencies.
