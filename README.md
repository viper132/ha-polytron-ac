# Polytron Smart AC for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/default)
[![Home Assistant](https://img.shields.io/badge/Home--Assistant-Supported-blue.svg?style=for-the-badge&logo=home-assistant)](https://www.home-assistant.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

A modern, production-grade custom integration for **Polytron Smart Air Conditioners** (including the **Polytron Smart Neuva Pro** series and all models using the Polytron IoT23 / Fira cloud protocol).

This integration replaces the legacy, slow official mobile app with native, lightning-fast Home Assistant entities, complete with real-time active power monitoring, energy statistics, and full automation capabilities.

---

## 🌟 Highlights & Features

- **Full Climate Thermostat Control (`climate.*`):**
  - **Power:** Turn unit ON / OFF.
  - **Target Temperature:** Precise control from 16°C to 32°C (1°C steps).
  - **HVAC Modes:** `Cool`, `Dry`, `Fan Only`, and `Auto (Smart)`.
  - **Fan Speeds:** `Auto`, `Low`, `Medium`, and `High`.
  - **Louver Swing:** `Vertical` & `Off`.
  - **Dynamic Action Status:** Automatically reports `Cooling` (when compressor is actively pulling power) or `Idle` (when target temperature is reached).

- **Real-Time Telemetry & Electrical Sensors (`sensor.*`):**
  - **Active Power (`sensor.*_power`):** Real-time electricity draw in **Watts (W)** to observe compressor ramping and power states.
  - **Energy Consumption (`sensor.*_energy_consumption`):** Daily accumulated energy usage in **kWh**, fully compatible with the **Home Assistant Energy Dashboard**.
  - **Wi-Fi Signal Strength (`sensor.*_wi_fi_rssi`):** Signal strength in **dBm** for wireless diagnostic and health monitoring.

- **Seamless WhatsApp OTP Onboarding:**
  - Zero manual YAML credentials. Set up directly through the Home Assistant UI via an automated, one-time WhatsApp verification code.

---

## 📋 Supported Hardware

- **Polytron Smart Neuva Pro** (Series `AE04`, Firmware `IRAA-02-04`)
- All smart Polytron air conditioners communicating via the **Polytron Smart Home** mobile app and IoT23 cloud backend.

---

## 🚀 Installation

### Option 1: Via HACS (Recommended)

1. Ensure [HACS (Home Assistant Community Store)](https://hacs.xyz/) is installed.
2. In Home Assistant, navigate to **HACS** → **Integrations**.
3. Click the three dots (⋮) in the top right corner and select **Custom repositories**.
4. Enter the repository URL:
   ```text
   https://github.com/viper132/ha-polytron-ac
   ```
5. Set Category to **Integration**, click **Add**, and locate **Polytron Smart AC**.
6. Click **Download**, then **restart Home Assistant**.

### Option 2: Manual Installation

1. Download the latest release archive (`polytron_ac.zip`) from the [Releases](https://github.com/viper132/ha-polytron-ac/releases) page.
2. Extract the `polytron_ac` directory into your Home Assistant configuration directory:
   ```text
   /config/custom_components/polytron_ac/
   ```
3. Restart Home Assistant.

---

## ⚙️ Configuration

1. In Home Assistant, go to **Settings** → **Devices & Services**.
2. Click **+ Add Integration** in the bottom right corner.
3. Search for **Polytron Smart AC**.
4. Enter the phone / WhatsApp number registered with your Polytron Smart Home account (e.g. `08123456789`).
5. Check your WhatsApp for a 6-digit verification code from Polytron / Fira.
6. Enter the 6-digit OTP code into the Home Assistant prompt.
7. Your air conditioner (`climate.*`) and telemetry sensors (`sensor.*`) will automatically be discovered and configured.

---

## 📊 Dashboard Card Examples (Lovelace)

### Standard Thermostat & Telemetry Stack

Add a **Manual Card** in your dashboard and paste the following YAML configuration:

```yaml
type: vertical-stack
cards:
  # 1. Main Climate Controller
  - type: thermostat
    entity: climate.bedroom_ac
    name: Bedroom AC
    features:
      - type: climate-hvac-modes
        hvac_modes:
          - cool
          - dry
          - fan_only
          - auto
          - 'off'

  # 2. Power & Energy Telemetry
  - type: glance
    title: Energy & Connectivity
    show_name: true
    show_icon: true
    show_state: true
    entities:
      - entity: sensor.bedroom_ac_power
        name: Active Power
        icon: mdi:lightning-bolt
      - entity: sensor.bedroom_ac_energy_consumption
        name: Daily Energy
        icon: mdi:counter
      - entity: sensor.bedroom_ac_wi_fi_rssi
        name: Wi-Fi RSSI
        icon: mdi:wifi

  # 3. Quick Action Buttons
  - type: horizontal-stack
    cards:
      - type: button
        name: Turbo Cool (22°C)
        icon: mdi:snowflake-alert
        tap_action:
          action: call-service
          service: climate.set_temperature
          target:
            entity_id: climate.bedroom_ac
          data:
            temperature: 22
            hvac_mode: cool

      - type: button
        name: Eco Comfort (25°C)
        icon: mdi:leaf
        tap_action:
          action: call-service
          service: climate.set_temperature
          target:
            entity_id: climate.bedroom_ac
          data:
            temperature: 25
            hvac_mode: cool

      - type: button
        name: Power Off
        icon: mdi:power
        tap_action:
          action: call-service
          service: climate.set_hvac_mode
          target:
            entity_id: climate.bedroom_ac
          data:
            hvac_mode: 'off'
```

---

## ⚡ Energy Dashboard Integration

To track electricity usage and cost trends:
1. Go to **Settings** → **Dashboards** → **Energy**.
2. Under **Individual Devices**, click **Add Device**.
3. Select `sensor.bedroom_ac_energy_consumption`.
4. Home Assistant will now automatically chart hourly and daily energy consumption.

---

## 🛠️ Architecture & Under the Hood

The Polytron Smart AC firmware communicates over an Espressif (ESP8266/ESP32) microcontroller connecting to Polytron's dedicated Fira IoT gateway:
- **Authentication Service:** `https://ism.fira.id/` (WhatsApp OTP challenge & token issuance)
- **Device State & Telemetry Service:** `https://devsapp.iot.polytron.co.id/` (Real-time telemetry, power metering, and control commands)
- **Account & Device Discovery Service:** `https://usrsapp.iot.polytron.co.id/` (User home appliances mapping)

---

## 🤝 Contributing

Contributions, bug reports, and feature suggestions are welcome! Feel free to open an issue or submit a pull request.

---

## 📄 License

This project is open-source software licensed under the [MIT License](LICENSE).

*Disclaimer: This is an independent open-source community integration and is not officially affiliated with or endorsed by PT Polytron / PT Hartono Istana Teknologi.*
