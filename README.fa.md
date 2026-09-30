<div align="center">

# DeepSeek Web API

**یک API رایگان و خودمیزبان (self-hosted) برای مدل زبانی که حساب شخصی DeepSeek شما را به یک اندپوینت سازگار با OpenAI تبدیل می‌کند.**

بدون API key، بدون اعتبار و بدون پلن پولی — فقط همان نشست (session) معمولی شما در [chat.deepseek.com](https://chat.deepseek.com) که به‌صورت یک REST API در دسترس قرار می‌گیرد.

[![Build](https://github.com/hasan-ahani/deepseek-web-api/actions/workflows/build.yml/badge.svg)](https://github.com/hasan-ahani/deepseek-web-api/actions/workflows/build.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/hassanahani/deepseek-web-api)](https://hub.docker.com/r/hassanahani/deepseek-web-api)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

[English](README.md) · **فارسی**

</div>

---

## معرفی

این پروژه، وب‌اپ مصرفی DeepSeek را به APIهای استاندارد متصل می‌کند. می‌توانید از آن به دو شکل استفاده کنید:

- 🐍 **به‌عنوان یک کتابخانه‌ی پایتونی** — با `client.chat("سلام")` یک گفت‌وگوی تک‌مرحله‌ای یا چندمرحله‌ای با پشتیبانی از streaming داشته باشید.
- 🔌 **به‌عنوان یک سرور سازگار با OpenAI** — یک سرور HTTP محلی که پروتکل OpenAI را پیاده‌سازی می‌کند؛ بنابراین SDK رسمی `openai` و هر کلاینت سازگار با OpenAI بدون تغییر کار می‌کند، فقط کافی است `base_url=http://localhost:8000/v1` را تنظیم کنید.

فقط **یک‌بار** در مرورگر وارد حساب می‌شوید؛ پس از آن نشست ذخیره شده و به‌صورت خودکار تازه‌سازی می‌شود.

> **پروژه‌ی غیررسمی.** این پروژه هیچ وابستگی یا تأییدیه‌ای از سوی DeepSeek ندارد. هدف آن خودکارسازی تجربه‌ی وب مصرفی DeepSeek برای استفاده‌ی شخصی است؛ آن را مسئولانه و در چارچوب قوانین DeepSeek استفاده کنید.

### ویژگی‌ها

هر آنچه برای اجرای آن به‌عنوان یک سرویس واقعی و احراز هویت‌شده لازم است:

| قابلیت | آن‌چه فراهم می‌کند |
| --- | --- |
| **احراز هویت با API key** | هر درخواست `/v1` باید هدر `Authorization: Bearer <WEUI_AI_API_KEY>` را بفرستد؛ مقایسه به‌صورت constant-time و در غیر این صورت پاسخ `401` (`server/security.py`). |
| **ایمیج Docker** | یک کانتینر headless که API را سرو می‌کند و برای `linux/amd64` و `linux/arm64` منتشر شده است. |
| **CI/CD** | GitHub Actions در هر push/tag یک ایمیج multi-arch می‌سازد و روی GHCR و Docker Hub پوش می‌کند (`.github/workflows/build.yml`). |
| **اندپوینت وضعیت نشست** | `GET /v1/session/status` برای گزارش این‌که نشست فعلی DeepSeek معتبر است یا نه، جهت مانیتورینگ و health check. |
| **محدودسازی نرخ به تفکیک کلید** | محدودکننده‌ی پنجره‌ی لغزان، درخواست‌ها را بر اساس API key (و در صورت نبود آن، بر اساس IP کلاینت) دسته‌بندی می‌کند (`server/api.py`). |
| **قابل‌انتقال بودن نشست** | اسکریپت `scripts/push-session.sh` فایل `session.json` تازه را به یک میزبان Remote منتقل می‌کند تا کانتینر headless بتواند از آن استفاده کند. |

---

## فهرست مطالب

- [چرا از این پروژه استفاده کنیم؟](#چرا-از-این-پروژه-استفاده-کنیم)
- [پیش‌نیازها](#پیشنیازها)
- [شروع سریع](#شروع-سریع)
- [روش ۱ — در پایتون (بدون سرور)](#روش-۱--در-پایتون-بدون-سرور)
- [روش ۲ — به‌عنوان سرور سازگار با OpenAI](#روش-۲--بهعنوان-سرور-سازگار-با-openai)
- [احراز هویت](#احراز-هویت)
- [تنظیمات](#تنظیمات)
- [اجرا در Docker](#اجرا-در-docker)
- [چرخه‌ی عمر نشست و استقرار headless](#چرخهی-عمر-نشست-و-استقرار-headless)
- [بررسی انسانی و proof-of-work (خودکار)](#بررسی-انسانی-و-proof-of-work-خودکار)
- [مدل‌ها، DeepThink و جست‌وجوی وب](#مدلها-deepthink-و-جستوجوی-وب)
- [اندپوینت‌ها](#اندپوینتها)
- [همروندی (Concurrency)](#همروندی-concurrency)
- [محدودسازی نرخ درخواست](#محدودسازی-نرخ-درخواست)
- [CI/CD و ایمیج‌های کانتینر](#cicd-و-ایمیجهای-کانتینر)
- [ساختار پروژه](#ساختار-پروژه)
- [نکات و محدودیت‌ها](#نکات-و-محدودیتها)
- [مجوز](#مجوز)

---

## چرا از این پروژه استفاده کنیم؟

- **رایگان** — از حساب معمول و واردشده‌ی DeepSeek استفاده می‌کند، بدون هزینه‌ی API.
- **جایگزین مستقیم OpenAI** — هر کلاینت OpenAI را به `/v1` بدهید و بدون تغییر کار می‌کند.
- **تمام ابزارهای DeepSeek** — انتخاب مدل سریع یا expert و فعال/غیرفعال کردن DeepThink و جست‌وجوی وب به‌ازای هر درخواست.
- **Streaming و گفت‌وگو** — خروجی توکن‌به‌توکن و رشته‌های چندمرحله‌ای با `conversation_id`.
- **قابل استقرار** — احراز هویت‌شده، محدودشده، داکرایز‌شده و ساخته‌شده برای x86_64 و arm64.

---

## پیش‌نیازها

- **Python 3.9+**
- یک **حساب DeepSeek** (همان حساب رایگانی که برای [chat.deepseek.com](https://chat.deepseek.com) استفاده می‌کنید)
- سازگار با Windows، macOS و Linux
- Docker (اختیاری، برای استقرار کانتینری)

---

## شروع سریع

```bash
# ۱. کلون کردن این مخزن
git clone https://github.com/hasan-ahani/deepseek-web-api.git
cd deepseek-web-api
```

**۲. ساخت و فعال‌سازی محیط مجازی**

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

> در Windows ممکن است لازم باشد یک‌بار اجرای اسکریپت‌ها را مجاز کنید:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. در `cmd.exe` به‌جای آن
> از `venv\Scripts\activate.bat` استفاده کنید.

**۳. نصب وابستگی‌ها و ورود**

```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# نصب مرورگری که Playwright لازم دارد (یک‌بار)
playwright install chromium

# ورود یک‌باره: یک مرورگر باز می‌شود، وارد حساب DeepSeek خود شوید
python -m deepseek.auth
```

پنجره‌ی ورود باز می‌شود تا به‌صورت دستی وارد شوید و یک‌بار بررسی انسانی را حل کنید. پس از آن، نشست شما (bearer token + کوکی‌ها) در پوشه‌ی `session/` ذخیره می‌شود (در git نادیده گرفته می‌شود و هرگز به اشتراک گذاشته نمی‌شود) و در هر اجرا مورد استفاده قرار می‌گیرد — نشست ذخیره‌شده به‌طور خودکار تازه می‌شود، پس اولین درخواست بلافاصله کار می‌کند.

> سرور می‌تواند در صورت نیاز و در همان لحظه نیز این پنجره را برای شما باز کند
> (به `SERVER_INTERACTIVE_LOGIN` مراجعه کنید)، بنابراین برای استفاده‌ی محلی و
> تک‌کاربره این مرحله اختیاری است.

**۴. اجرای سرور**

```bash
cp .env.example .env          # سپس WEUI_AI_API_KEY را به یک مقدار تصادفی قوی تغییر دهید
python app.py                 # -> http://127.0.0.1:8000
```

---

## روش ۱ — در پایتون (بدون سرور)

ساده‌ترین راه اگر کد شما از قبل پایتون است.

```python
from deepseek import DeepSeekClient

client = DeepSeekClient()                # نشست واردشده‌ی شما را بارگذاری می‌کند

# دریافت پاسخ کامل
reply = client.chat("در یک جمله‌ی کوتاه سلام کن.")
print(reply.text)

# ادامه‌ی همان گفت‌وگو — شناسه را برگردانید
reply2 = client.chat("و حالا به فرانسوی؟", conversation_id=reply.conversation_id)
print(reply2.text)

# پخش پاسخ به‌صورت streaming
for chunk in client.stream("یک لطیفه‌ی کوتاه بگو"):
    print(chunk, end="", flush=True)
```

متد `chat()` متن کامل به‌همراه یک `conversation_id` برمی‌گرداند؛ برای ادامه‌ی همان رشته این شناسه را برگردانید، یا برای شروع تازه آن را حذف کنید. متد `stream()` پاسخ را تکه‌تکه برمی‌گرداند.

👉 نمونه‌های بیشتر: [`examples/01_direct_chat.py`](examples/01_direct_chat.py)، [`02_direct_conversation.py`](examples/02_direct_conversation.py)، [`03_direct_stream.py`](examples/03_direct_stream.py)

---

## روش ۲ — به‌عنوان سرور سازگار با OpenAI

یک سرور محلی اجرا کنید که با API استاندارد OpenAI صحبت می‌کند، تا ابزارها و SDKهای موجود OpenAI بدون تغییر کار کنند.

```bash
python app.py
# -> DeepSeek OpenAI-compatible API on http://127.0.0.1:8000
```

سپس هر کلاینت OpenAI را به آن متصل کنید. پس از فعال‌سازی احراز هویت، API key الزامی است (به بخش [احراز هویت](#احراز-هویت) مراجعه کنید):

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="your-secret")

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "سلام!"}],
)
print(resp.choices[0].message.content)
```

یا با HTTP ساده / `curl` فراخوانی کنید:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret" \
  -d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "سلام!"}]}'
```

> آدرس اتصال را با متغیرهای محیطی تغییر دهید: `HOST=0.0.0.0 PORT=8080 python app.py`،
> یا `uvicorn server.api:app --host 0.0.0.0 --port 8080` را اجرا کنید.

👉 نمونه‌های بیشتر: [`examples/04_server_http.py`](examples/04_server_http.py)، [`examples/05_server_stream.py`](examples/05_server_stream.py)، [`examples/06_server_openai_sdk.py`](examples/06_server_openai_sdk.py)

---

## احراز هویت

سرور مستقرشده توسط یک bearer token ثابت محافظت می‌شود. هر درخواست زیر `/v1` باید آن را بفرستد:

```
Authorization: Bearer <WEUI_AI_API_KEY>
```

- درخواست‌هایی با کلید ناموجود یا اشتباه پاسخ `401 Unauthorized` می‌گیرند.
- مقایسه به‌صورت **constant-time** (`secrets.compare_digest`) انجام می‌شود تا کلید از طریق زمان‌سنجی لو نرود (`server/security.py`).
- مسیر `/healthz` عمداً باز گذاشته شده تا health checkهای کانتینر کار کنند.
- اگر `WEUI_AI_API_KEY` تنظیم نشده باشد، سرور **از راه‌اندازی خودداری می‌کند** — مگر این‌که `WEUI_AI_ALLOW_UNAUTH=1` مقداردهی شود؛ این یک راه فرار است که فقط برای توسعه‌ی محلی در نظر گرفته شده است.

برای ساخت یک کلید قوی:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## تنظیمات

همه‌ی تنظیمات از محیط (و فایل `.env` به‌کمک `python-dotenv`) خوانده می‌شوند. برای قالب مستندشده به [`.env.example`](.env.example) مراجعه کنید.

| متغیر | پیش‌فرض | کاربرد |
| --- | --- | --- |
| `WEUI_AI_API_KEY` | *(خالی)* | توکن bearer که در هر درخواست `/v1` الزامی است. بدون آن (و بدون `WEUI_AI_ALLOW_UNAUTH=1`) سرور بالا نمی‌آید. |
| `WEUI_AI_ALLOW_UNAUTH` | `0` | **فقط توسعه‌ی محلی.** اجازه‌ی فراخوانی `/v1` بدون کلید. هرگز در محیط production فعال نکنید. |
| `HOST` | `127.0.0.1` | آدرس اتصال برای `app.py`. |
| `PORT` | `8000` | پورت اتصال برای `app.py`. |
| `RATE_LIMIT_PER_MINUTE` | `30` | تعداد درخواست مجاز در دقیقه، به تفکیک API key (یا IP کلاینت). |
| `SERVER_INTERACTIVE_LOGIN` | `1` | در نبود نشست، یک مرورگر مرئی برای ورود باز می‌کند. برای استقرار headless آن را `0` کنید (در عوض `503` برمی‌گرداند). |
| `SESSION_MAX_AGE` | `21600` | مدت اعتماد به `session.json` ذخیره‌شده (ثانیه) پیش از تلاش برای تازه‌سازی (۶ ساعت). |
| `DEEPSEEK_PROFILE_DIR` | `session/profile` | استفاده‌ی مجدد از یک پروفایل Chrome واردشده‌ی موجود. |
| `DEEPSEEK_BROWSER_ARGS` | *(خالی)* | فلگ‌های اضافی Chromium (مثلاً `--no-sandbox --disable-dev-shm-usage`). |

```bash
RATE_LIMIT_PER_MINUTE=60 python app.py          # افزایش محدودیت نرخ
SERVER_INTERACTIVE_LOGIN=0 python app.py        # headless: بدون باز شدن مرورگر
```

---

## اجرا در Docker

یک ایمیج multi-arch آماده روی Docker Hub و GHCR منتشر می‌شود:

```bash
docker pull hassanahani/deepseek-web-api:latest
# یا: docker pull ghcr.io/hasan-ahani/deepseek-web-api:latest
```

کانتینر فقط API را سرو می‌کند — **نمی‌تواند** نشست بسازد، چون بررسی انسانی یک‌باره به یک پنجره‌ی مرورگر واقعی نیاز دارد (کانتینر نمایشگر ندارد). ابتدا روی دسکتاپ وارد شوید، سپس `session.json` حاصل را به کانتینر بدهید:

```bash
# ۱. روی ماشین خودتان، با یک مرورگر: فایل session/session.json نوشته می‌شود
python -m deepseek.auth

# ۲. اجرای سرور با mount کردن همان نشست
docker run --rm -it -p 8000:8000 \
  -v "$PWD/session:/app/session" \
  -e WEUI_AI_API_KEY=your-secret \
  hassanahani/deepseek-web-api:latest
```

نکات کلیدی:

- `session.json` **تنها** آرتیفکت قابل‌انتقال است. پروفایل Chromium بین سیستم‌عامل‌ها قابل‌انتقال نیست (کوکی‌هایش با کلید مخصوص هر OS رمزنگاری می‌شوند)، بنابراین فقط `session.json` برای جابه‌جایی در نظر گرفته شده است.
- پیش از انقضای `SESSION_MAX_AGE`، `session.json` را دوباره بسازید و پوش کنید — کانتینر نمی‌تواند آن را به‌صورت headless تازه کند و پس از انقضا API پاسخ `503 login_required` می‌دهد.
- ایمیج با یک کاربر غیرروت (uid 1000) اجرا می‌شود، پس حجم mount‌شده‌ی نشست باید برای آن uid قابل‌نوشتن باشد.
- داخل ایمیج **دستور `python -m deepseek.auth` را اجرا نکنید**؛ این کار به‌طور عمدی با خطای «Missing X server or $DISPLAY» شکست می‌خورد.

ساخت ایمیج به‌صورت دستی:

```bash
docker build -t deepseek-web-api:local .
```

---

## چرخه‌ی عمر نشست و استقرار headless

نشست DeepSeek ترکیبی از یک bearer token و کوکی‌هایی است که از یک مرورگر واردشده ضبط می‌شود. چرخه‌ی عمر آن به این شکل است:

۱. **ورود اولیه (دسکتاپ):** دستور `python -m deepseek.auth` یک مرورگر واقعی باز می‌کند تا یک‌بار وارد شوید و بررسی انسانی را حل کنید.
۲. **استفاده‌ی مجدد از نشست ذخیره‌شده:** نشست ضبط‌شده در `session/session.json` ذخیره و در هر درخواست استفاده می‌شود.
۳. **تازه‌سازی headless:** در صورت امکان، توکن بدون باز کردن پنجره از پروفایل ذخیره‌شده‌ی Chrome دوباره ضبط می‌شود.
۴. **انقضا:** اگر نشست کاملاً منقضی شود و ورود تعاملی مجاز نباشد، API پاسخ `503 login_required` می‌دهد و از شما می‌خواهد مرحله‌ی ورود را دوباره اجرا کنید.

برای یک میزبان Remote/headless، نشست را به‌صورت محلی ضبط کرده و منتقل کنید. اسکریپت همراه پروژه همین کار را می‌کند (عمداً هرگز پروفایل مرورگر را کپی نمی‌کند):

```bash
# کپی session/session.json به یک میزبان Remote و اصلاح مالکیت برای کانتینر
SSH_HOST=user@host ./scripts/push-session.sh

# بازنویسی‌های اختیاری
REMOTE_DIR=/srv/deepseek/session LOCAL_FILE=./session/session.json \
  SSH_HOST=user@host ./scripts/push-session.sh
```

هر زمان می‌توانید نشست فعال را بررسی کنید:

```bash
curl http://localhost:8000/v1/session/status
# {"status":"ok","session_age_seconds":42}
```

---

## بررسی انسانی و proof-of-work (خودکار)

چت DeepSeek پشت دو دروازه قرار دارد که هر دو برای شما مدیریت می‌شوند:

- **بررسی انسانی AWS WAF:** دسترسی نیازمند یک نشست مرورگر واردشده است که بررسی «تأیید کنید ربات نیستید» را رد کرده باشد. دستور `python -m deepseek.auth` یک مرورگر واقعی باز می‌کند تا یک‌بار وارد شوید و آن را حل کنید؛ توکن و کوکی‌های حاصل در پوشه‌ی `session/` ذخیره و در هر درخواست استفاده می‌شوند.
- **Proof-of-work:** هر تکمیل درخواست با یک چالش PoW کنترل می‌شود. پل (bridge) آن را با اجرای ماژول `sha3_wasm_bg.wasm` خود DeepSeek — همان ماژولی که مرورگر بارگذاری می‌کند — داخل یک سندباکس `wasmtime` حل می‌کند؛ پس از سمت شما کاری لازم نیست.

نشست ذخیره‌شده حدوداً ۶ ساعت (`SESSION_MAX_AGE`) استفاده می‌شود و در صورت امکان به‌صورت headless از پروفایل Chrome شما تازه می‌شود؛ فقط انقضای کامل شما را به مرورگر برمی‌گرداند.

---

## مدل‌ها، DeepThink و جست‌وجوی وب

نام `model` انتخاب می‌کند **کدام مدل** پاسخ دهد. DeepThink و جست‌وجوی وب مدل نیستند — آن‌ها کلیدهای مستقل (toggles) هستند که به‌ازای هر درخواست ارسال می‌شوند.

| مدل | حالت DeepSeek | توضیح |
| --- | --- | --- |
| `deepseek-chat` | Instant | مدل پیش‌فرض سریع |
| `deepseek-expert` | Expert | قوی‌تر و کندتر |

مقدار `thinking: true` (استدلال DeepThink) و/یا `search: true` (جست‌وجوی وب) را در بدنه‌ی درخواست بفرستید — یا از طریق `extra_body` در SDK رسمی OpenAI:

```python
resp = client.chat.completions.create(
    model="deepseek-expert",
    messages=[{"role": "user", "content": "امروز چه خبر تازه‌ای بود؟"}],
    extra_body={"thinking": True, "search": True},
)
```

سه پارامتر `conversation_id`، `thinking` و `search` افزوده‌هایی خارج از استاندارد OpenAI هستند. مدل یک رشته در زمان ساخت ثابت می‌شود، بنابراین در ادامه‌دادن گفت‌وگو نمی‌توان `model` را همراه `conversation_id` فرستاد. نام مدل ناشناخته پاسخ `404` می‌گیرد (بدون fallback خاموش). به [`server/config.py`](server/config.py) مراجعه کنید.

---

## اندپوینت‌ها

| متد | مسیر | احراز هویت | توضیح |
| --- | --- | --- | --- |
| `POST` | `/v1/chat/completions` | ✅ | چت. از `"stream": true` و به‌صورت اختیاری `"conversation_id"`، `"thinking"` و `"search"` پشتیبانی می‌کند. |
| `GET` | `/v1/models` | ✅ | فهرست مدل‌های موجود. |
| `GET` | `/v1/session/status` | ✅ | گزارش می‌دهد که آیا نشست قابل‌استفاده‌ی DeepSeek موجود است (`ok` / `login_required` / `error`). |
| `GET` | `/healthz` | ❌ | پروب سلامت (liveness). معاف از احراز هویت و محدودسازی نرخ. |

---

## همروندی (Concurrency)

سرور یک **تک** حساب واردشده‌ی DeepSeek را پشت یک کلاینت مشترک پل می‌زند. مخزن `wasmtime` مربوط به حل‌کننده‌ی PoW قابل‌ورود مجدد (reentrant) نیست، بنابراین فراخوانی‌های upstream **سریال** می‌شوند: درخواست‌های HTTP موازی پشت یک قفل صف می‌کشند و یکی‌یکی اجرا می‌شوند (به [`server/api.py`](server/api.py) مراجعه کنید). این رفتار عمدی است — توان عملیاتی متوالی است، نه موازی. تعداد درخواست‌های همزمان در پرواز را کم نگه دارید و لطفاً به حساب خود فشار نیاورید.

---

## محدودسازی نرخ درخواست

علاوه بر سریال‌سازی، پل یک محدودیت نرخ خود-تحمیلی با یک محدودکننده‌ی پنجره‌ی لغزانِ بدون وابستگی اعمال می‌کند ([`server/ratelimit.py`](server/ratelimit.py)): تعداد درخواست‌های پذیرفته‌شده را به تفکیک API key — و در حالت بدون احراز هویت بر اساس IP کلاینت — محدود می‌کند و در صورت عبور، پاسخ استاندارد `429` به‌همراه `Retry-After` می‌دهد. مسیر `/healthz` معاف است.

```bash
RATE_LIMIT_PER_MINUTE=60 python app.py   # افزایش آن
```

**در سمت کلاینت از backoff نمایی استفاده کنید.** خطاهای گذرای `429` با تلاش مجدد و تأخیرهای فزاینده (مثلاً ۱، ۲ و ۴ ثانیه) برطرف می‌شوند. SDK رسمی `openai` این کار را به‌طور خودکار و با احترام به `Retry-After` انجام می‌دهد؛ در HTTP ساده خودتان چند بار تلاش مجدد اضافه کنید.

---

## CI/CD و ایمیج‌های کانتینر

فایل [`.github/workflows/build.yml`](.github/workflows/build.yml) یک ایمیج چندپلتفرمی می‌سازد و آن را در دو رجیستری منتشر می‌کند:

- **GHCR:** `ghcr.io/hasan-ahani/deepseek-web-api`
- **Docker Hub:** `hassanahani/deepseek-web-api`

| رویداد | تگ‌ها |
| --- | --- |
| Push به `main` / `master` | `latest`، `<branch>`، `sha-<short>` |
| Push تگ `v*.*.*` | `v1.2.3`، `1.2.3`، `1.2`، `1`، `sha-<short>` |
| Pull request | فقط build (بدون push) |
| اجرای دستی (dispatch) | build + push |

ایمیج‌ها برای `linux/amd64` **و** `linux/arm64` ساخته می‌شوند (arm64 از طریق QEMU)، بنابراین همان manifest list روی سرورهای x86_64 و ماشین‌های Apple Silicon اجرا می‌شود. بیلدها دارای provenance (attestation) و شامل SBOM هستند. انتشار به سکرت‌های مخزن `DOCKERHUB_USERNAME` و `DOCKERHUB_TOKEN` نیاز دارد؛ GHCR از `GITHUB_TOKEN` داخلی استفاده می‌کند.

---

## ساختار پروژه

| مسیر | کار آن |
| --- | --- |
| [`deepseek/`](deepseek/) | کتابخانه‌ی اصلی: `DeepSeekClient`، ورود مرورگری ([`auth.py`](deepseek/auth.py))، درایور HTTP ([`client.py`](deepseek/client.py)) و حل‌کننده‌ی PoW ([`pow.py`](deepseek/pow.py)). |
| [`server/`](server/) | سرور FastAPI سازگار با OpenAI: [`api.py`](server/api.py)، [`config.py`](server/config.py)، [`security.py`](server/security.py)، [`ratelimit.py`](server/ratelimit.py)، [`openai_format.py`](server/openai_format.py)، [`schemas.py`](server/schemas.py). |
| [`examples/`](examples/) | نمونه‌های اجرایی برای هر قابلیت ([`examples/README.md`](examples/README.md)). |
| [`scripts/`](scripts/) | ابزارهای عملیاتی مانند [`push-session.sh`](scripts/push-session.sh). |
| [`Dockerfile`](Dockerfile) | ایمیج کانتینر headless. |
| [`.github/workflows/build.yml`](.github/workflows/build.yml) | خط لوله‌ی ساخت و انتشار multi-arch. |
| [`app.py`](app.py) | سرور را اجرا می‌کند. |

---

## نکات و محدودیت‌ها

- **یک‌بار وارد شوید، سپس استفاده کنید.** نشست ذخیره‌شده به‌طور خودکار تازه می‌شود؛ فقط در صورت انقضای کامل باید دوباره وارد شوید.
- **منصفانه رفتار کنید.** لطفاً در حد معقول استفاده کنید و با درخواست‌های انبوه خودکار، سرویس را اسپم یا تحت فشار نگذارید.
- **شمارش دقیق توکن وجود ندارد.** مقدار `usage` در پاسخ‌ها یک تخمین تقریبی حدوداً ۴ کاراکتر بر توکن است.
- **بیشتر پارامترهای OpenAI پذیرفته اما نادیده گرفته می‌شوند** (`temperature`، `top_p`، `max_tokens`)؛ تنها `model`، `messages`، `stream`، `conversation_id`، `thinking` و `search` واقعاً اثر دارند.
- **قابلیت بینایی (Vision) به تعویق افتاده است.** به زیرساخت بارگذاری تصویر نیاز دارد که هنوز ساخته نشده است.
- **نشست شما خصوصی است.** همه‌چیز در پوشه‌ی `session/` (کوکی‌ها + توکن) روی ماشین شما می‌ماند و در git نادیده گرفته می‌شود.

---

## مجوز

تحت [مجوز MIT](LICENSE) منتشر شده است. از آنجا که این یک پروژه‌ی غیررسمی است، مسئولیت رعایت قوانین سرویس DeepSeek بر عهده‌ی خود شماست.
