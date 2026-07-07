<div dir="rtl">

# 🤖 چت‌بات هوشمند فروشگاه — Store Chatbot

> یک چت‌بات با **Python + Flask + Groq**، طراحی‌شده برای اینکه فقط و فقط به سوالات مرتبط با فروشگاه شما پاسخ دهد. با ویرایش یک فایل JSON تمام اطلاعات فروشگاه(محصولات، قیمت‌ها، سیاست‌ها، ساعات کاری، آدرس و…) را به چت‌بات معرفی می‌کند و چت‌بات به‌صورت خودکار در حوزه همان فروشگاه پاسخ می‌دهد

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM-F55036)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 📑 فهرست

- [ویژگی‌ها](#-ویژگیها)
- [معماری](#-معماری-پروژه)
- [پیش‌نیازها](#-پیشنیازها)
- [مرحله ۱ — نصب](#-مرحله-۱--نصب)
- [مرحله ۲ — دریافت کلید API از Groq](#-مرحله-۲--دریافت-کلید-api-از-groq)
- [مرحله ۳ — تنظیم فایل env.](#-مرحله-۳--تنظیم-فایل-env)
- [مرحله ۴ — تنظیم اطلاعات فروشگاه (store_config.json)](#-مرحله-۴--تنظیم-اطلاعات-فروشگاه-store_configjson)
- [مرحله ۵ — اجرای چت‌بات](#-مرحله-۵--اجرای-چتبات)
- [استفاده از API](#-استفاده-از-api)
- [پنل ادمین](#-پنل-ادمین)
- [تست](#-تست)
- [استقرار (Deployment)](#-استقرار-deployment)
- [عیب‌یابی](#-عیبیابی-troubleshooting)
- [ساختار فایل‌ها](#-ساختار-فایلها)
- [مجوز](#-مجوز)

---

## ✨ ویژگی‌ها

- 🎯 **پاسخگویی محدود به فروشگاه**: با Prompt Engineering دقیق، چت‌بات فقط به سؤالات مرتبط با فروشگاه شما پاسخ می‌دهد. سؤالات off-topic (مثل «۲+۲ چند می‌شه؟» یا «کد پایتون بنویس») مؤدبانه رد می‌شوند.
- ⚡ **متصل به Groq**: سریع‌ترین inference موجود برای LLM (پشتیبانی از Llama 3.3 70B، Llama 3.1 8B، Mixtral و Gemma).
- 🌍 **دوزبانه (فارسی + انگلیسی)**: تشخیص خودکار زبان کاربر و پاسخ به همان زبان.
- 🧠 **حافظه گفتگو**: با SQLite تاریخچه‌ی گفتگوها به‌صورت پایدار ذخیره می‌شود.
- 🔥 **Hot-reload تنظیمات**: هرگونه تغییر در `store_config.json` بدون restart سرور بلافاصله اعمال می‌شود.
- 🛡️ **Rate limiting** و مدیریت خطا و retry خودکار در برابر خطاهای Groq.
- 🎨 **رابط کاربری مدرن**: چت UI ریسپانسیو با تم روشن/تاریک، فونت وزیرمتن، پشتیبانی از RTL/LTR.
- 🐳 **آماده Docker**: فایل `Dockerfile` و `docker-compose.yml` برای استقرار سریع.
- 🧪 **تست‌های واحد**: پوشش تست برای بخش‌های حیاتی.
- 🔐 **پنل ادمین**: مشاهده آمار، ویرایش کانفیگ فروشگاه به‌صورت زنده از طریق API.

---

## 🏗 معماری پروژه

```
User ──▶ Flask API ──▶ ChatService ──▶ PromptBuilder ──▶ Groq API
              │                              ▲
              │                              │
              ▼                    reads from store_config.json
          SQLite DB
      (sessions + messages)
```

**جریان یک پیام:**
1. کاربر پیام می‌فرستد → `/api/chat/message`
2. `ChatService` تاریخچه گفتگو را از SQLite می‌خواند
3. `PromptBuilder` اطلاعات فروشگاه را از `store_config.json` به system prompt تبدیل می‌کند
4. `GroqService` درخواست را به Groq می‌فرستد
5. پاسخ در دیتابیس ذخیره و به کاربر برگردانده می‌شود

---

## 🔧 پیش‌نیازها

- **Python 3.10 یا بالاتر**
- **pip** (مدیر بسته پایتون)
- **کلید API از Groq** (رایگان — [console.groq.com](https://console.groq.com/keys))
- (اختیاری) **Docker** برای استقرار containerized

---

## 📥 مرحله ۱ — نصب

### الف) کلون پروژه

```bash
git clone https://github.com/ImMrShervin/store-ai-chatbot
```

یا اگر فایل‌ها را به‌صورت zip دارید، آن را اکسترکت کنید و وارد پوشه شوید.

### ب) ایجاد محیط مجازی (Virtual Environment)

<div dir="ltr">

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# Windows (CMD)
python -m venv venv
venv\Scripts\activate.bat
```

</div>

### ج) نصب پکیج‌ها

<div dir="ltr">

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

</div>

---

## 🔑 مرحله ۲ — دریافت کلید API از Groq

Groq یک سرویس LLM بسیار سریع است که در پلن رایگان هم quota قابل‌قبولی می‌دهد.

1. به آدرس **[https://console.groq.com/keys](https://console.groq.com/keys)** بروید
2. با ایمیل یا گوگل اکانت رایگان بسازید
3. روی **"Create API Key"** کلیک کنید
4. یک نام برای کلید انتخاب کنید (مثلاً `store-chatbot`)
5. کلید تولیدشده را کپی کنید (فرمت آن `gsk_...` است)

> ⚠️ **دقت کنید:** این کلید فقط یک‌بار نمایش داده می‌شود. جای امنی ذخیره کنید و در `git` **commit نکنید**.

---

## ⚙️ مرحله ۳ — تنظیم فایل `.env`

فایل نمونه را کپی کنید:

<div dir="ltr">

```bash
cp .env.example .env
```

</div>

سپس `.env` را با ویرایشگر باز کنید و مقادیر زیر را تنظیم کنید:

<div dir="ltr">

```env
GROQ_API_KEY=gsk_کلیدی_که_از_Groq_گرفتید
GROQ_MODEL=llama-3.3-70b-versatile

FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_SECRET_KEY=یک_رشته_تصادفی_طولانی_برای_production

MAX_TOKENS=1024
TEMPERATURE=0.4
MAX_HISTORY_MESSAGES=20
SESSION_TIMEOUT_MINUTES=60

DATABASE_PATH=data/chatbot.db
STORE_CONFIG_PATH=data/store_config.json

RATE_LIMIT_PER_MINUTE=20
```

</div>

### مدل‌های پیشنهادی Groq

| مدل | توضیح | سرعت | کیفیت |
|---|---|---|---|
| `llama-3.3-70b-versatile` ⭐ | **پیش‌فرض** — بهترین تعادل | خیلی خوب | عالی |
| `llama-3.1-8b-instant` | سبک، پاسخ خیلی سریع | فوق‌العاده | خوب |
| `mixtral-8x7b-32768` | context طولانی (32k) | خوب | خوب |
| `gemma2-9b-it` | جایگزین کم‌مصرف | عالی | خوب |

---

## 🏪 مرحله ۴ — تنظیم اطلاعات فروشگاه (`store_config.json`)

**این مهم‌ترین مرحله است.** تمام «هویت» چت‌بات از این فایل می‌آید.

فایل `data/store_config.json` را باز کنید و اطلاعات فروشگاه واقعی خود را جایگزین مقادیر نمونه کنید. ساختار به این شکل است:

<div dir="ltr">

```jsonc
{
  "store": {
    "name": "نام فروشگاه شما",
    "name_en": "Your Store Name",
    "tagline": "شعار فروشگاه",
    "description": "توضیحات کامل فروشگاه",
    "established_year": 1400,
    "website": "https://your-store.com"
  },
  "contact": {
    "phone": "021-...",
    "mobile": "0912...",
    "email": "info@your-store.com",
    "address": "آدرس کامل",
    "instagram": "@your_store"
  },
  "business_hours": {
    "saturday": "9:00 - 21:00",
    ...
  },
  "categories": [
    { "id": "cat_1", "name": "...", "name_en": "..." }
  ],
  "products": [
    {
      "id": "prod_1",
      "name": "نام محصول",
      "category_id": "cat_1",
      "price": 1500000,
      "currency": "IRR",
      "stock": 25,
      "description": "...",
      "features": ["ویژگی ۱", "..."],
      "warranty_months": 12
    }
  ],
  "shipping": { ... },
  "payment_methods": [ ... ],
  "policies": { ... },
  "faq": [ ... ],
  "chatbot_settings": {
    "bot_name": "دستیار فروشگاه",
    "welcome_message": "سلام! 👋 من دستیار {store_name} هستم...",
    "off_topic_response": "من فقط به سوالات مرتبط با {store_name} پاسخ می‌دهم.",
    "primary_color": "#0ea5e9",
    "accent_color": "#0284c7"
  }
}
```

</div>

### 💡 نکات مهم

- **{store_name}**: در فیلدهای `welcome_message` و `off_topic_response` به‌صورت خودکار با نام فروشگاه جایگزین می‌شود.
- **زبان دوگانه**: فیلدهای `_en` برای پاسخ‌های انگلیسی به مشتریان استفاده می‌شوند.
- **قیمت‌ها**: به ریال بنویسید (بدون کاما).
- **موجودی (stock)**: اگر ۰ باشد، چت‌بات محصول را ناموجود اعلام می‌کند.
- **Hot-reload**: هر تغییری در این فایل انجام دهید، **بدون restart سرور** بلافاصله اعمال می‌شود ✨

---

## 🚀 مرحله ۵ — اجرای چت‌بات

### حالت توسعه (Development)

<div dir="ltr">

```bash
python run.py
```

</div>

خروجی مورد انتظار:

<div dir="ltr">

```
============================================================
🚀 Store Chatbot running on http://0.0.0.0:5000
🤖 Model: llama-3.3-70b-versatile
📁 Store config: data/store_config.json
💾 Database:     data/chatbot.db
============================================================
```

</div>

حالا مرورگر را باز کنید و به آدرس زیر بروید:

**👉 [http://localhost:5000](http://localhost:5000)**

### حالت Production (با Gunicorn)

<div dir="ltr">

```bash
gunicorn "run:app" -b 0.0.0.0:5000 -w 4 --timeout 120
```

</div>

---

## 📡 استفاده از API

اگر می‌خواهید چت‌بات را در اپ خودتان جاسازی کنید:

### ۱) ایجاد session جدید

<div dir="ltr">

```bash
curl -X POST http://localhost:5000/api/chat/session/new
```

</div>

پاسخ:
<div dir="ltr">

```json
{
  "session_id": "uuid-here",
  "welcome_message": "سلام! ...",
  "bot_name": "دستیار فروشگاه"
}
```

</div>

### ۲) ارسال پیام

<div dir="ltr">

```bash
curl -X POST http://localhost:5000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"سلام، محصولاتتون چیه؟","session_id":"uuid-here"}'
```

</div>

پاسخ:
<div dir="ltr">

```json
{
  "reply": "سلام! ما در حال حاضر دو محصول داریم...",
  "session_id": "uuid-here",
  "tokens_used": 145,
  "model": "llama-3.3-70b-versatile"
}
```

</div>

### ۳) دریافت تاریخچه

<div dir="ltr">

```bash
curl http://localhost:5000/api/chat/session/<session_id>/history
```

</div>

### ۴) پاک‌کردن تاریخچه

<div dir="ltr">

```bash
curl -X POST http://localhost:5000/api/chat/session/<session_id>/clear
```

</div>

---

## 🔐 پنل ادمین

برای حفاظت از endpoint‌های ادمین، در `.env` این مقدار را اضافه کنید:

<div dir="ltr">

```env
ADMIN_API_KEY=your_secret_admin_key
```

</div>

سپس در تمام درخواست‌های ادمین، هدر `X-Admin-Key` را ارسال کنید.

### دریافت آمار

<div dir="ltr">

```bash
curl -H "X-Admin-Key: your_secret_admin_key" http://localhost:5000/api/admin/stats
```

</div>

### به‌روزرسانی کانفیگ (بدون restart)

<div dir="ltr">

```bash
curl -X PUT http://localhost:5000/api/admin/config \
  -H "X-Admin-Key: your_secret_admin_key" \
  -H "Content-Type: application/json" \
  -d @data/store_config.json
```

</div>

---

## 🧪 تست

<div dir="ltr">

```bash
pip install pytest
pytest tests/ -v
```

</div>

---

## 🐳 استقرار (Deployment)

### گزینه ۱: Docker Compose (پیشنهادی)

<div dir="ltr">

```bash
# ابتدا .env را تنظیم کنید
docker compose up -d --build
```

</div>

چت‌بات روی `http://localhost:5000` در دسترس خواهد بود.

### گزینه ۲: Docker ساده

<div dir="ltr">

```bash
docker build -t store-chatbot .
docker run -d -p 5000:5000 --env-file .env -v $(pwd)/data:/app/data store-chatbot
```

</div>

### گزینه ۳: استقرار روی سرور (systemd)

فایل `/etc/systemd/system/store-chatbot.service` بسازید:

<div dir="ltr">

```ini
[Unit]
Description=Store Chatbot
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/store_chatbot
Environment="PATH=/opt/store_chatbot/venv/bin"
ExecStart=/opt/store_chatbot/venv/bin/gunicorn "run:app" -b 0.0.0.0:5000 -w 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now store-chatbot
```

</div>

### گزینه ۴: Nginx + HTTPS

<div dir="ltr">

```nginx
server {
    listen 443 ssl http2;
    server_name chat.your-store.com;

    ssl_certificate     /etc/letsencrypt/live/chat.your-store.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/chat.your-store.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

</div>

---

## 🩹 عیب‌یابی (Troubleshooting)

| مشکل | راه‌حل |
|---|---|
| ❌ `GROQ_API_KEY is not configured` | مطمئن شوید `.env` وجود دارد و `GROQ_API_KEY` مقدار درست دارد. |
| ❌ `store_config.json not found` | مسیر فایل در `.env` را چک کنید یا فایل نمونه را در `data/` بسازید. |
| ❌ `Rate limited` از Groq | مقدار `RATE_LIMIT_PER_MINUTE` را کاهش دهید یا به پلن بالاتر Groq بروید. |
| 🌐 صفحه چت لود نمی‌شود | مطمئن شوید Flask روی پورت درست اجرا شده و فایروال باز است. |
| 💬 چت‌بات به سؤالات فروشگاه پاسخ نمی‌دهد | ‏`store_config.json` را دقیق پر کنید — هرچه کامل‌تر، پاسخ‌ها بهتر. |
| 🇮🇷 پاسخ‌ها به زبان اشتباه | Prompt به‌صورت خودکار زبان را تشخیص می‌دهد. اگر مشکل ادامه دارد، سؤال را واضح‌تر بپرسید. |
| 🔄 تغییرات در `store_config.json` اعمال نمی‌شود | فایل مستقیماً از disk خوانده می‌شود. اگر hot-reload کار نکرد، سرور را restart کنید. |

---

## 📂 ساختار فایل‌ها

<div dir="ltr">

```
store_chatbot/
├── app/
│   ├── __init__.py           # App factory
│   ├── config.py             # Configuration
│   ├── models/
│   │   └── database.py       # SQLite layer
│   ├── routes/
│   │   ├── main.py           # Landing page
│   │   ├── chat.py           # Chat API
│   │   └── admin.py          # Admin API
│   └── services/
│       ├── groq_service.py      # Groq API wrapper
│       ├── store_service.py     # Config loader
│       ├── prompt_builder.py    # System prompt generator
│       ├── chat_service.py      # Orchestrator
│       └── rate_limiter.py      # In-memory rate limiter
├── data/
│   ├── store_config.json     # ★ Your store data
│   └── chatbot.db            # SQLite (auto-created)
├── static/
│   ├── css/style.css
│   └── js/chat.js
├── templates/
│   └── index.html
├── tests/
│   ├── test_prompt_builder.py
│   └── test_store_service.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py                    # Entry point
└── README.md
```

</div>

---

## 🔒 توصیه‌های امنیتی برای Production

1. **کلید ADMIN_API_KEY** حتماً تنظیم شود.
2. **FLASK_SECRET_KEY** را با یک رشته تصادفی طولانی جایگزین کنید (`python -c "import secrets;print(secrets.token_hex(32))"`).
3. CORS را در `app/__init__.py` روی دامنه واقعی خود محدود کنید.
4. Rate limiter در حال حاضر in-memory است — برای مقیاس بالا از Redis استفاده کنید.
5. HTTPS با Let's Encrypt استفاده کنید.

---

## 📜 مجوز

MIT License — آزادانه استفاده، تغییر و توزیع کنید.

---

<div align="center">

**ساخته شده با ❤️**

اگر سوال یا پیشنهادی داشتید issue باز کنید
</div>

</div>
