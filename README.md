# Polytron Smart AC for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/default)
[![Home Assistant](https://img.shields.io/badge/Home--Assistant-Supported-blue.svg?style=for-the-badge&logo=home-assistant)](https://www.home-assistant.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

Integrasi kustom Home Assistant untuk AC pintar Polytron (seperti seri **Polytron Smart Neuva Pro** dan model IoT23 lainnya) menggunakan protokol cloud resmi Polytron Fira IoT.

Integrasi ini menggantikan aplikasi resmi Polytron Smart Home yang lambat dan jadul dengan kontrol Home Assistant yang responsif, modern, serta mendukung pemantauan daya listrik dan otomasi penuh.

---

## ✨ Fitur Utama (Features)

- **Kontrol Penuh Thermostat (`climate.*`):**
  - Daya: ON / OFF
  - Pengatur Suhu: 16°C – 32°C (Step 1°C)
  - Mode Operasi: `Cool`, `Dry`, `Fan Only`, `Auto (Smart)`
  - Kecepatan Kipas: `Auto`, `Low`, `Medium`, `High`
  - Ayunan Angin (Swing): `Vertical` & `Off`
  - Status Aksi Dinamis: Otomatis menampilkan status `Cooling` saat kompresor aktif atau `Idle` saat suhu tercapai.
- **Telemetri Daya Listrik & Energi (`sensor.*`):**
  - **Daya Aktif (Watt):** Memantau tarikan listrik kompresor secara *real-time*.
  - **Konsumsi Energi (kWh):** Akumulasi pemakaian listrik harian yang kompatibel langsung dengan **Home Assistant Energy Dashboard**.
  - **Kekuatan Sinyal Wi-Fi (dBm):** Memantau kestabilan koneksi Wi-Fi modul AC.
- **Login Otomatis via WhatsApp OTP:**
  - Setup langsung dari antarmuka Home Assistant tanpa perlu mengetik token manual atau konfigurasi YAML yang rumit.

---

## 📦 Cara Pemasangan (Installation)

### Metode 1: Melalui HACS (Direkomendasikan)
1. Pastikan [HACS](https://hacs.xyz/) sudah terpasang di Home Assistant Anda.
2. Buka **HACS** → **Integrations** → Klik menu titik tiga (⋮) di pojok kanan atas → Pilih **Custom repositories**.
3. Masukkan URL repository ini:
   ```
   https://github.com/hugomulana/ha-polytron-ac
   ```
   Pilih Kategori: **Integration**.
4. Klik **Add**, lalu cari **Polytron Smart AC** dan klik **Download**.
5. Restart Home Assistant Anda.

### Metode 2: Pemasangan Manual
1. Unduh file `polytron_ac.zip` dari halaman [Releases](https://github.com/hugomulana/ha-polytron-ac/releases).
2. Ekstrak folder `polytron_ac` ke dalam direktori konfigurasi Home Assistant Anda:
   ```
   /config/custom_components/polytron_ac/
   ```
3. Restart Home Assistant Anda.

---

## ⚙️ Cara Menghubungkan (Configuration)

1. Di Home Assistant, buka **Settings** → **Devices & Services** (Perangkat & Layanan).
2. Klik tombol **+ Add Integration** di pojok kanan bawah.
3. Cari: **Polytron Smart AC**.
4. Masukkan nomor telepon / WhatsApp yang terdaftar pada aplikasi resmi Polytron Anda (contoh: `08123456789`).
5. Periksa pesan masuk di WhatsApp dari Polytron/Fira yang berisi 6 digit kode OTP.
6. Masukkan kode OTP tersebut pada dialog verifikasi Home Assistant.
7. Selesai! Entitas `climate.bedroom_ac` dan sensor telemetri akan otomatis terdeteksi.

---

## 📱 Contoh Tampilan Dashboard (Lovelace Card)

Anda dapat menambahkan kartu kontrol AC modern ke dashboard Lovelace Anda dengan kode YAML berikut:

```yaml
type: vertical-stack
cards:
  # 1. Kontrol Thermostat Utama
  - type: thermostat
    entity: climate.bedroom_ac
    name: Bedroom AC (Polytron Neuva Pro)
    features:
      - type: climate-hvac-modes
        hvac_modes:
          - cool
          - dry
          - fan_only
          - auto
          - 'off'

  # 2. Ringkasan Daya & Energi
  - type: glance
    title: Telemetri Listrik
    show_name: true
    show_icon: true
    show_state: true
    entities:
      - entity: sensor.bedroom_ac_power
        name: Daya Aktif
        icon: mdi:lightning-bolt
      - entity: sensor.bedroom_ac_energy_consumption
        name: Total Hari Ini
        icon: mdi:counter
      - entity: sensor.bedroom_ac_wi_fi_rssi
        name: Sinyal Wi-Fi
        icon: mdi:wifi

  # 3. Tombol Preset Cepat
  - type: horizontal-stack
    cards:
      - type: button
        name: Dingin Cepat (22°C)
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
        name: Eco 25°C
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
        name: Matikan AC
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

## ⚡ Integrasi Home Assistant Energy Dashboard

Untuk melacak biaya listrik harian/bulanan AC ini:
1. Buka **Settings** → **Dashboards** → **Energy**.
2. Pada bagian **Individual Devices**, klik **Add Device**.
3. Pilih entitas: `sensor.bedroom_ac_energy_consumption`.
4. Anda sekarang dapat melihat konsumsi kWh dan grafik pemakaian listrik AC secara otomatis!

---

## 🛠️ Perangkat yang Didukung (Supported Devices)

- **Polytron Smart Neuva Pro** (Model: `AE04`, `IRAA-02-04`)
- Semua AC Polytron yang terhubung dengan aplikasi **Polytron Smart Home** (protokol IoT23).

---

## 📄 Lisensi (License)

Proyek ini dilisensikan di bawah [MIT License](LICENSE).

*Disclaimer: Integrasi ini merupakan proyek open-source independen dan tidak berafiliasi secara resmi dengan PT Polytron / PT Hartono Istana Teknologi.*
