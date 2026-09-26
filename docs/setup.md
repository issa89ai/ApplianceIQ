# Run ApplianceIQ on Windows

## Prerequisites

Use Python (the existing environment uses Python 3.13), Android Studio with its bundled JDK, Android SDK 36, and an Android device with USB debugging enabled. The app minimum SDK is 24. The Gradle wrapper is included.

The Python requirements are an existing pinned environment snapshot. A fresh installation has not been verified as part of the documentation cleanup. Initial package installation, Gradle dependency resolution, and the embedding model's first load require network access. Once downloaded, the embedding model runs locally.

## Python environment

Open PowerShell in the repository root: the directory containing `backend`, `android`, and `data_pipeline`. Existing users can skip environment creation and installation.

```powershell
py -3.13 -m venv data_pipeline\venv
.\data_pipeline\venv\Scripts\python.exe -m pip install -r requirements.txt
```

The checked-in processed JSON and embeddings are enough to run the app. There is no need to fetch source pages or rebuild embeddings for a demo.

## Backend

From the repository root:

```powershell
.\data_pipeline\venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Keep this terminal open and wait for `Application startup complete`. In a second terminal:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/health'
$result = Invoke-RestMethod 'http://127.0.0.1:8000/search?q=my%20dryer%20tumbles%20but%20does%20not%20heat&top_k=3'
$result.results | Select-Object title, brand, score | Format-Table
```

The health endpoint reports status and ranking weights. It does not prove that every query or repair guide is correct.

## Android phone

1. Open the repository's `android` directory in Android Studio and allow Gradle sync to finish.
2. Connect and unlock the phone; enable USB debugging and approve the computer on the phone.
3. In PowerShell, list devices:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices
```

4. Replace `PHONE_SERIAL` below with the serial marked `device`:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" -s PHONE_SERIAL reverse tcp:8000 tcp:8000
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" -s PHONE_SERIAL reverse --list
```

5. Select the phone and click Run in Android Studio. Query `my dryer tumbles but does not heat` and follow the heating guide's type choice.

The Android base URL is `http://127.0.0.1:8000/`. USB reverse connects that phone address to the computer's backend. Repeat the reverse command after a disconnect if needed. Backend edits reload with `--reload`; Android code edits require rebuilding/reinstalling the app.

## Checks

Run from the repository root:

```powershell
.\data_pipeline\venv\Scripts\python.exe -m data_pipeline.test_brand_filter_policy
.\data_pipeline\venv\Scripts\python.exe -m unittest data_pipeline.test_guide_branches
.\data_pipeline\venv\Scripts\python.exe data_pipeline\audit_dataset.py
```

The first two import the backend and load the model, but do not need a separate HTTP server. Use `-m` for these tests so Python can find the root `backend` package. Historical evaluation scripts use direct file commands shown in [evaluation](evaluation.md), because some import sibling modules.

For a command-line Android build, from `android`:

```powershell
$env:JAVA_HOME = 'C:\Program Files\Android\Android Studio\jbr'
.\gradlew.bat --no-daemon assembleDebug
```

Adjust the JDK path if Android Studio is installed elsewhere. The debug APK is generated at `android/app/build/outputs/apk/debug/app-debug.apk` relative to the repository root.

## Rebuild data only when needed

These commands overwrite the generated JSON and embedding files. Run both in sequence and restart the backend after changes to guide content or ordering:

```powershell
.\data_pipeline\venv\Scripts\python.exe data_pipeline\build_dataset.py
.\data_pipeline\venv\Scripts\python.exe data_pipeline\build_embeddings.py
```

Guide vectors, metadata, and lexical document order must correspond. Current builders rely on matching order; they are not a general incremental database system.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Backend cannot be reached | Confirm `/health` works on the computer, then check `adb devices` and reverse mapping |
| Port 8000 already in use | An existing backend may be running; check health before starting another |
| `No module named backend` | Use the module test command from the repository root |
| Data file not found | Confirm the working directory is the repository root |
| Run button disabled | Wait for Gradle sync; inspect its error output if it fails |
| Old interface on the phone | Reinstall by clicking Run after Android code changes |
| Saved result shown | This is a cached response, not proof of a live backend connection |

Search caching retains up to 20 normalized queries. It is a fallback when a search fails; separately selected branch guides are not saved by that cache.
