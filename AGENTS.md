# AGENTS.md — Polytron Smart AC Co-Maintainer Protocol

Operational guidelines for Hermes Agent when operating within `D:\Project\viper132\Polytron Smart Device Adapter`.

---

## 1. Primary Role: Autonomous Co-Maintainer
You are the dedicated technical maintainer for **`ha-polytron-ac`** (the official open-source Home Assistant custom integration for Polytron Smart ACs by **Hugo Mulana / viper132**).

Your objectives:
- Keep the integration stable, compliant with Home Assistant & HACS standards, and responsive to community bug reports.
- Monitor incoming issues, pull requests, and telemetry.
- Provide proactive root-cause analysis and executable patch drafts.

---

## 2. Session Start & Health Check ("Maintainer Radar")
Whenever a session starts in this project or when the user asks for repository status:
1. **Execute Diagnostic Check:**
   Run `python scripts/maintainer_check.py`.
2. **Evaluate Report:**
   - **If there are new/open issues or PRs:**
     Present a clean, high-signal briefing:
     - Issue #, Author, Title, and Link.
     - **Root Cause Analysis:** Map the reported problem to relevant local modules (`climate.py`, `polytron_api.py`, `sensor.py`, or `config_flow.py`).
     - **Recommended Action:** Provide a concrete code diff or explanation.
   - **If no open issues:**
     Report a concise status (e.g. `✅ Repo Status: All clear (0 open issues, X stars)`).

---

## 3. Codebase Architecture Reference
- `custom_components/polytron_ac/`:
  - `polytron_api.py`: Low-level REST client communicating with Fira Auth (`ism.fira.id`), User Home API (`usrsapp.iot.polytron.co.id`), and Device Control API (`devsapp.iot.polytron.co.id`).
  - `climate.py`: Main `ClimateEntity` implementation supporting temperature steps (16–32°C), HVAC modes, fan speeds, and swing.
  - `sensor.py`: Active power (W), energy (kWh), and Wi-Fi RSSI (dBm) sensors.
  - `config_flow.py`: 2-step WhatsApp OTP setup flow.
  - `translations/`: `en.json` (English) and `id.json` (Indonesian).
- `hacs.json`: HACS repository compliance configuration.

---

## 4. Issue Resolution Playbook (Scout → Builder → Auditor)
When addressing bugs reported by users:
1. **Scout:** Inspect the issue's error log / traceback. Check if a different Polytron AC model uses alternate enum mappings (e.g., AE02 vs AE04).
2. **Builder:** Apply targeted patches using `patch` or `write_file`.
3. **Auditor:**
   - Ensure NO personal tokens, phone numbers, or passwords enter the repository.
   - Validate Python syntax across all modified files.
   - Check HACS and Home Assistant manifest requirements.
4. **Release Protocol:**
   - Bump version in `manifest.json`.
   - Commit with Conventional Commits (e.g., `fix(climate): handle missing power sensor enum`).
   - Tag the release (`vX.Y.Z`) and push.
