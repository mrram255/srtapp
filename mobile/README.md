# SRTAPP Mobile (Expo)

Targets **Expo SDK 54** (`expo ~54`, **Expo Router v6**, **React Native 0.81**, **React 19**). Use **Node.js ≥ 20.19.4** (Metro / RN requirement). Run `npx expo install --fix` after dependency bumps so versions stay aligned.

## Features

- **Expo Router** (`app/` file routes): splash gate → `/login` → `(tabs)` shell  
- **expo-secure-store** tokens (`srtapp_access_token`, `srtapp_refresh_token`) + persisted user JSON  
- **Axios** client with Django **`APIResponse`** envelope parsing on refresh (`data.access`, rotated refresh)  
- **Zustand** auth store, **TanStack Query** provider ready for screens  
- **react-hook-form + zod** login validation  

Copy `.env.example` → `.env` and point `EXPO_PUBLIC_API_URL` at Django **`…/api/v1`** (Android emulator host loopback: `http://10.0.2.2:8000/api/v1`).

```bash
cd mobile
npm install
npx expo install --fix
npm run lint   # tsc --noEmit
npm start      # LAN + sensible packager hostname (fixes bad 172.x QR on WSL/Docker)
# or: npm run start:clear   # same + Metro cache reset
#
# Tunnel (ngrok) when LAN QR / 8081 blocked:
# npm run start:tunnel
# npm run start:tunnel:clear
#
# USB + adb reverse tcp:8081 — then bundler localhost:
# npm run start:localhost:clear
```

`npm start` runs `scripts/dev-server-host.cjs` so the QR targets **Wi‑Fi `192.168…` / `10…`** when possible — on **WSL2 + Windows**, it prefers **Windows DHCP IPv4** via `powershell.exe`. Override anytime: **`REACT_NATIVE_PACKAGER_HOSTNAME=192.168.x.x npm start`**.

### Bina Windows `netsh` / port-proxy — Expo Go LAN fix

QR me sahi **`192.168…:8081`** dikhe aur phir **“Something went wrong”** aaye, to aksar **`8081` WSL tak pohch nahi paata** — isliye **Netsh ki jagah** in me se koi ek use karo.

**1) Metro seedha Windows se chalaana (recommended, admin commands nahi)**

WSL sirf editing ke liye; **Node + Expo Windows par** LAN stack use karte hain, isliye phone **`192.168…:8081`** tak seedha pohch sakta hai.

1. Explorer address bar: `\\wsl$\Ubuntu\home\USERNAME\srtapp\mobile` — `USERNAME` / distro apne hisaab se (`Ubuntu` jagah aur distro naam ho sakta hai).
2. **PowerShell** (normal):

```powershell
cd \\wsl$\Ubuntu\home\USERNAME\srtapp\mobile   # USERNAME ko apna WSL user se replace karo
npm install
npx expo install --fix
$env:EXPO_PUBLIC_API_URL = "http://192.168.x.x:8000/api/v1"   # apna PC Wi‑Fi IP — Django reachable hona chahiye
npm run start:clear
```

`dev-server-host.cjs` Windows par hi chalega aur QR me **Wi‑Fi IP + 8081** sahi advertiser honge; **`8081` ab Windows NIC par sun raha hona chahiye**, jo WSL‑only Metro me nahi hota.

**2) USB debugging + localhost (Wi‑Fi / 8081 forward ki zaroorat nahi)**

Phone USB se, **adb jahan tumhára phone dikhe** — aksar **Windows PowerShell** (jahan `adb devices` OK ho):

```powershell
adb reverse tcp:8081 tcp:8081
adb reverse tcp:8000 tcp:8000
```

Phir Metro **WSL ya Windows** — bundler **`--localhost`** (QR **`exp://127.0.0.1:8081`** wagaira):

```bash
cd ~/srtapp/mobile
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1 npm run start:localhost:clear
```

**Note:** Django bhi **`127.0.0.1:8000`** par phone se reachable hona chahiye jab tak tum dono reverses use kar rahe ho; agar sirf **`8000`** reverse fail ho to API ke liye ab bhi **`http://192.168…:8000/api/v1`** rakho aur sirf **`8081`** reverse rakho (`EXPO_PUBLIC` + Django reachability dekho jo tum pehle se use kar rahe ho).

**3) Tunnel**

Neeche wala **`start:tunnel:clear`** — internet ke through bundler; **Netsh zaroor nahi**.

### LAN QR scan works nahi, lekin `--tunnel -c` se khul jata hai

**LAN** mode me Expo Go **Metro (port `8081`)** se seedha connect karta hai. Kabhi‑kabhi **firewall** (Windows **Inbound TCP 8081**), **guest Wi‑Fi / AP isolation**, **corporate VLAN**, ya **WSL port forward** ki wajah se **QR scan fail** ho sakta hai — **tunnel** internet ke through bundler reach karta hai, isliye **scan / URL chal jati hai**.

Tunnel use karo:

```bash
npm run start:tunnel:clear
```

**Note:** Tunnel sirf **JavaScript bundle** ke liye hai. **`EXPO_PUBLIC_API_URL`** ab bhi tumhara Django hona chahiye (e.g. `http://192.168.x.x:8000/api/v1`) — **`/health/`** phone browser se check karte raho.

### `.env` sahi hai lekin Metro me galat URL / `172.xx` dikhe?

1. Dekho ki shell ne **pehle** se set to nahi kiya: **`echo $EXPO_PUBLIC_API_URL`**. Expo **existing shell env ko `.env` se upar** maanta hai → **`unset EXPO_PUBLIC_API_URL`** phir **`npm run start:tunnel:clear`**. Ya ek shot: **`EXPO_PUBLIC_API_URL=http://192.168.29.208:8000/api/v1 npx expo start --tunnel -c`**.
2. **`grep EXPO_PUBLIC .env`** — sirf **ek active** uncommented line honi chahiye.
3. Cache: **`rm -rf ~/srtapp/mobile/.expo`** phir dubara **`start:tunnel:clear`**.

Tunnel **ngrok**/Expo par depend karta hai — agar `failed to start tunnel` aaye to LAN fix (firewall **`8081`** allow) ya dobara try karo.
