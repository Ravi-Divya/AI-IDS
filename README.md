# AI-IDS — AI-Driven Intrusion Detection System

A full-stack web application for real-time network security monitoring, powered by machine learning. Designed and developed as a college capstone project.

---

## 1. Introduction

### 1.1 Problem Statement

Network intrusions and cyber attacks are increasing in both frequency and sophistication. Traditional signature-based Intrusion Detection Systems (IDS) like Snort and Suricata rely on predefined rules to detect attacks. This approach has a critical limitation: **it can only detect known threats**. Novel attacks, zero-day exploits, and sophisticated variants often bypass signature-based detection entirely.

Additionally, most enterprise IDS solutions are:
- **Expensive** — requiring significant hardware and licensing costs
- **Complex** — needing dedicated teams to manage rules and alerts
- **Not adaptive** — unable to learn from new traffic patterns without manual rule updates

### 1.2 Proposed Solution

AI-IDS addresses these limitations by using **Machine Learning** to detect network threats. Instead of matching traffic against predefined signatures, the system learns the characteristics of normal vs. malicious traffic from data. This allows it to:

- Detect **novel attacks** that don't match any known signature
- **Adapt** to new traffic patterns through retraining
- Provide **confidence scores** for each detection, reducing false positives
- Extract **80+ features** per network flow for deep analysis

The system is built as a modern web application with an intuitive dashboard, making it accessible to security analysts without requiring deep ML expertise.

---

## 2. System Architecture

### 2.1 High-Level Overview

The application follows a **three-tier client-server architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION TIER                        │
│              React SPA (Single Page Application)             │
│         ┌──────────┬──────────┬──────────┬──────────┐       │
│         │Dashboard │ Packets  │  Alerts  │ Settings │       │
│         │  Charts  │  Table   │  Manage  │  Config  │       │
│         └──────────┴──────────┴──────────┴──────────┘       │
│                     │ Axios HTTP / JWT Auth                  │
├─────────────────────┼───────────────────────────────────────┤
│                   APPLICATION TIER                          │
│               FastAPI Web Server (Python)                    │
│  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐   │
│  │ Auth   │ │  ML      │ │  Alert   │ │  Simulation    │   │
│  │ Module │ │ Pipeline │ │  Engine  │ │  Engine        │   │
│  └────────┘ └──────────┘ └──────────┘ └────────────────┘   │
│                     │ SQLAlchemy ORM                         │
├─────────────────────┼───────────────────────────────────────┤
│                     DATA TIER                               │
│              PostgreSQL Database                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ packets  │ │  flows   │ │ threats  │ │  users/roles  │   │
│  │ alerts   │ │  audit   │ │ ml_models│ │  settings     │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
1. Network packets are captured or simulated
         │
         ▼
2. Packets are grouped into bidirectional flows
         │
         ▼
3. Feature extractor computes 80+ features per flow
         │
         ▼
4. ML model classifies each flow as normal or threat
         │
         ▼
5. If threat → Alert is created in the database
         │
         ▼
6. Alert Engine dispatches notifications (Discord, Slack, etc.)
         │
         ▼
7. Frontend polls API and updates dashboard in real-time
```

---

## 3. Technology Stack

### 3.1 Frontend

| Technology | Purpose | Why it was chosen |
|---|---|---|
| **React 18** | UI framework | Component-based architecture for reusable UI elements |
| **TypeScript** | Type safety | Prevents runtime errors through static type checking |
| **Vite** | Build tool | Fast HMR (Hot Module Replacement) for rapid development |
| **Tailwind CSS** | Styling | Utility-first CSS framework for consistent, responsive design |
| **TanStack React Query** | Data fetching | Automatic caching, background refetching, and mutation management |
| **Zustand** | State management | Lightweight, boilerplate-free alternative to Redux |
| **React Router** | Routing | Client-side navigation with protected route guards |
| **Recharts** | Charts | Responsive, composable chart components for traffic analytics |
| **Framer Motion** | Animations | Declarative animation library for page transitions and micro-interactions |
| **Axios** | HTTP client | Interceptors for automatic JWT token refresh on 401 responses |

### 3.2 Backend

| Technology | Purpose | Why it was chosen |
|---|---|---|
| **Python 3.12+** | Core language | Extensive ML ecosystem (scikit-learn, pandas, numpy) |
| **FastAPI** | Web framework | Async performance, automatic OpenAPI docs, Pydantic validation |
| **SQLAlchemy 2.0** | ORM | Async database operations with repository pattern |
| **PostgreSQL** | Database | JSONB support for flexible schema, excellent async performance |
| **Alembic** | Migrations | Version-controlled database schema changes |
| **Pydantic V2** | Validation | Request/response validation with automatic serialization |
| **python-jose** | JWT | Secure token-based authentication with refresh token rotation |
| **passlib + bcrypt** | Password security | Industry-standard password hashing |

### 3.3 Machine Learning

| Technology | Purpose |
|---|---|
| **Scikit-learn** | Random Forest, Gradient Boosting, Isolation Forest implementations |
| **XGBoost** | Optimized gradient boosting for structured data |
| **Pandas** | Data manipulation and preprocessing |
| **NumPy** | Numerical computing for feature extraction |
| **Joblib / Pickle** | Model serialization and persistence |

### 3.4 Notification Channels

| Channel | Protocol | Configuration Required |
|---|---|---|
| Discord | Webhook (HTTP POST) | `DISCORD_WEBHOOK_URL` |
| Slack | Webhook (HTTP POST) | `SLACK_WEBHOOK_URL` |
| Telegram | Bot API (HTTPS) | `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` |
| Email | SMTP | `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` |
| Desktop | OS-native API | None (Win32 MessageBox / notify-send / osascript) |
| Firebase | FCM (HTTP v1) | `FIREBASE_CREDENTIALS_PATH` |

---

## 4. Machine Learning Pipeline

### 4.1 Overview

The ML pipeline is the core of the detection system. It provides a complete workflow from raw data to trained models to real-time predictions.

### 4.2 Supported Algorithms

| Algorithm | Type | Strengths |
|---|---|---|
| **Random Forest** | Ensemble (Bagging) | Handles non-linear relationships, resistant to overfitting, provides feature importance |
| **Gradient Boosting** | Ensemble (Boosting) | High accuracy, handles mixed data types, built-in regularization |
| **XGBoost** | Gradient Boosting (Optimized) | Best performance on structured/tabular data, GPU support, built-in cross-validation |
| **Isolation Forest** | Anomaly Detection | Unsupervised — detects novel attack patterns without labeled training data |

### 4.3 Pipeline Stages

```
Load Dataset (CSV/Parquet)
       │
       ▼
Clean Data (replace NaN/Inf, handle missing columns)
       │
       ▼
Preprocess (LabelEncode categories, StandardScale numeric)
       │
       ▼
Split (80% train / 20% test)
       │
       ▼
Train all 4 models in parallel
       │
       ▼
Select best model (highest F1 score)
       │
       ▼
Evaluate (accuracy, precision, recall, F1, ROC-AUC, confusion matrix)
       │
       ▼
Serialize (pickle: model + scaler + encoder + features + metrics)
       │
       ▼
Load for inference → predict(flow_features) → {label, confidence, is_threat}
```

### 4.4 Feature Set

The feature extractor computes **80+ features** per network flow, inspired by the KDD99 dataset:

| Category | Examples | Count |
|---|---|---|
| Basic features | Duration, protocol type, service, src/dst bytes | ~10 |
| Content features | Failed logins, root shell, file creations | ~8 |
| Time-based traffic | Count/rate of connections in last 2s to same host/service | ~12 |
| Host-based traffic | Same stats aggregated per destination host (last 100 connections) | ~12 |
| Packet statistics | Mean/min/max/std of packet sizes, TTL, window size | ~20 |
| TCP flags | Count of SYN, ACK, FIN, RST, PSH, URG flags | ~6 |
| Derived features | Entropy, burst rate, idle/active time, port scan heuristics | ~12 |

### 4.5 Pre-trained Model

A Gradient Boosting model has been pre-trained on a sample dataset of 1000 labeled flows (`datasets/sample_ids_data.csv`) and saved to `trained_models/model_gradient_boosting.pkl`. This allows the system to work immediately without requiring initial training.

---

## 5. Database Schema

The database uses a **soft-delete pattern**: records are never permanently deleted, only marked with `is_deleted = True` and `deleted_at` timestamp. This ensures data integrity and auditability.

### 5.1 Core Tables

| Table | Purpose | Key Columns |
|---|---|---|
| **users** | User accounts | email, username, hashed_password, company_name, roles (M:M) |
| **roles** | RBAC roles | name (admin/analyst/viewer) |
| **packets** | Raw network packets | timestamp, src/dst IP:port, protocol, size, tcp_flags (40+ columns) |
| **flows** | Bidirectional flows | flow_key, src/dst IP:port, protocol, start/end time, packet/byte counts, statistics (80+ columns) |
| **threats** | Detected threats | threat_type, severity, confidence, src/dst IP, description, explanation, recommendation |
| **alerts** | Security alerts | threat_id (FK), title, message, severity, is_read, is_acknowledged, delivery_status (JSONB) |
| **ml_models** | Trained ML models | name, model_type, version, accuracy, f1_macro, is_active, is_trained, file_path, metrics (JSONB) |
| **predictions** | Model predictions | flow_id, model_id, predicted_class, confidence, is_threat, prediction_time_ms |
| **audit_logs** | User activity trail | action, resource, ip_address, status, duration_ms |
| **settings** | Key-value config | key (unique), value (JSONB), category, description |
| **notification_history** | Alert delivery log | user_id, alert_id, channel, status, error_message, retry_count |

### 5.2 Key Relationships

```
users ────< user_roles >──── roles
users ────< refresh_tokens
users ────< audit_logs
users ────< notification_history

packets ──> flows (grouped by 5-tuple)

flows ────> threats (detected from flow)
flows ────> predictions

threats ──> alerts (one threat can trigger multiple alerts)
threats ──> predictions

alerts ───> notification_history (delivery tracking per channel)
```

---

## 6. API Endpoints

The backend exposes a **RESTful API** under the `/api/v1` base path. All endpoints (except login/register) require a JWT access token sent as a Bearer token in the `Authorization` header.

### 6.1 Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Create a new user account | No |
| POST | `/auth/login` | Login, returns access + refresh tokens | No |
| POST | `/auth/refresh` | Exchange refresh token for new access token | No |
| POST | `/auth/logout` | Revoke refresh token | Yes |
| GET | `/auth/me` | Get current user profile | Yes |
| POST | `/auth/setup-company` | Set company name for workspace | Yes |

### 6.2 Packet & Flow Data

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/packets/` | List packets (paginated, filterable by IP/protocol) | Yes |
| GET | `/packets/stats` | Packet statistics for last N hours | Yes |
| GET | `/packets/flows` | List flows (paginated, filterable by active status) | Yes |
| GET | `/packets/flows/stats` | Flow statistics for last N hours | Yes |

### 6.3 Threats & Predictions

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/threats/` | List threats (paginated, filterable by type/severity) | Yes |
| GET | `/threats/{id}` | Get single threat with full details | Yes |
| GET | `/threats/stats` | Threat statistics (distribution by type/severity) | Yes |
| GET | `/threats/predictions/all` | List all predictions (paginated) | Yes |
| GET | `/threats/predictions/stats` | Prediction statistics | Yes |

### 6.4 Alerts

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/alerts/` | List alerts (paginated, filter by unread/severity) | Yes |
| GET | `/alerts/{id}` | Get single alert | Yes |
| POST | `/alerts/{id}/read` | Mark alert as read | Yes |
| POST | `/alerts/{id}/acknowledge` | Acknowledge alert (records who acknowledged) | Yes |
| GET | `/alerts/channels/status` | Check which notification channels are configured | Yes |

### 6.5 Machine Learning

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/ml/models` | List all trained ML models | Yes |
| GET | `/ml/models/active` | Get currently active model | Yes |
| POST | `/ml/train` | Train a new model on a dataset | Yes |
| POST | `/ml/predict` | Run prediction on flow features | Yes |
| POST | `/ml/models/{id}/activate` | Set a model as active | Yes |
| POST | `/ml/generate-sample` | Generate a 1000-row sample CSV dataset | Yes |
| POST | `/ml/upload-dataset` | Upload a CSV file for training | Yes |

### 6.6 Dashboard

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/dashboard/stats` | Aggregate statistics (packets, flows, threats, alerts) | Yes |
| GET | `/dashboard/recent-threats` | Most recent N threats | Yes |
| GET | `/dashboard/traffic-timeline` | Hourly packet/threat counts for charting | Yes |

### 6.7 User Management

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/users/` | List all users (paginated) | Yes |
| GET | `/users/{id}` | Get user by ID | Yes |
| PUT | `/users/{id}` | Update user details | Yes |
| DELETE | `/users/{id}` | Soft-delete a user | Yes |
| PUT | `/users/{id}/roles` | Assign roles to a user | Yes |
| GET | `/users/roles` | List all available roles | Yes |

### 6.8 System

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/settings/` | List application settings | Yes |
| PUT | `/settings/{key}` | Update a setting value | Yes |
| GET | `/logs/` | List audit logs (paginated, filterable) | Yes |
| POST | `/simulation/generate` | Generate simulated traffic batch | Yes |
| POST | `/simulation/populate` | Populate historical data for N hours | Yes |

---

## 7. Simulation Engine

The simulation engine generates realistic network traffic for testing and demonstration purposes. It creates **both normal and malicious traffic** mimicking real-world network patterns.

### 7.1 Attack Types

| Attack | Technique | Indicators |
|---|---|---|
| **Port Scan** | Rapid connection attempts to multiple ports on the same host | High number of unique ports in short time, many SYN packets |
| **DDoS** | High volume of traffic from multiple sources to a single target | Packet rate spikes, distributed source IPs |
| **Brute Force** | Repeated login attempts with different credentials | High rate of failed connections, small packet sizes |
| **DNS Amplification** | Small queries to DNS servers with spoofed source IP | Mismatched query/response sizes, UDP traffic |
| **ARP Spoofing** | Fake ARP replies to intercept traffic | Duplicate IP addresses on different MACs |
| **Botnet Beaconing** | Periodic communication with C2 server | Regular interval connections, small payloads |
| **Data Exfiltration** | Large outbound data transfer to external host | Unusual outbound traffic volume, odd hours |
| **Man-in-the-Middle** | Interception of traffic between two endpoints | ARP anomalies, SSL certificate mismatches |
| **SQL Injection** | Malicious SQL queries in HTTP requests | Suspicious URL patterns, database error responses |
| **XSS** | Cross-site scripting payloads | Script tags in HTTP requests, unusual referrers |
| **Malware Download** | Download of executable files | Unusual file types in HTTP, connections to known malicious IPs |
| **ICMP Flood** | High volume of ICMP echo requests | ICMP packet rate spikes, large packet sizes |

### 7.2 Traffic Generation

The engine generates traffic in configurable batches:
- **Normal traffic**: Web browsing, DNS queries, email, file transfers, database queries
- **Attack traffic**: Random selection from 12 attack profiles with configurable ratio
- **Background noise**: Legitimate traffic mixed with attacks for realistic testing

---

## 8. Notification System

### 8.1 Architecture

When a threat is detected, the **Alert Engine** dispatches notifications through all configured channels simultaneously:

```
Threat Detected → Alert Created → AlertEngine.send_alert()
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
             Discord Webhook      Slack Webhook        Telegram Bot
                    │                    │                    │
                    ▼                    ▼                    ▼
             Rich Embed (color    Block Kit (section,   Markdown (severity,
             coded by severity)   fields, divider)      threat details)
                    │                    │                    │
                    ▼                    ▼                    ▼
             SMTP Email          Desktop Notification   Firebase Push
             (HTML template)     (OS-native popup)      (mobile device)
```

### 8.2 Delivery Tracking

Each alert's delivery status is recorded in the `delivery_status` JSONB column:

```json
{
  "discord": { "sent": true, "timestamp": "2024-01-15T10:30:00Z" },
  "email": { "sent": false, "error": "SMTP connection timeout", "retry_count": 2 },
  "desktop": { "sent": true, "timestamp": "2024-01-15T10:30:01Z" }
}
```

### 8.3 Frontend Notifications

The frontend provides two notification layers:

1. **Browser Notifications** — After the user grants permission in Settings, the app polls `GET /alerts?unread_only=true` every 10 seconds. New alerts trigger browser desktop notifications with severity icon, threat details, and a click handler that navigates to the Alerts page.

2. **Notification Bell** — A persistent bell icon in the top-right header showing the unread alerts count. Clicking it navigates to `/alerts`. The count updates automatically via React Query's polling mechanism.

---

## 9. Frontend Application

### 9.1 Route Structure

The application has **14 pages** organized into public and protected routes:

```
Public Routes (no authentication required)
├── /              → Landing page (marketing, features, CTA)
├── /login         → Login form
├── /signup        → Registration form
└── /setup-company → First-time company name setup

Protected Routes (authentication required)
├── /dashboard     → Main dashboard with stats and charts
├── /packets       → Live packet capture viewer
├── /flows         → Network flow records
├── /threats       → Detected threats list
├── /alerts        → Alert management
├── /analytics     → Charts and analytics
├── /ml            → ML model training and management
├── /users         → User administration
├── /settings      → Application settings
└── /logs          → Audit log viewer
```

### 9.2 Authentication Flow

1. User logs in → backend validates credentials → returns JWT access token + refresh token
2. Frontend stores tokens in Zustand (persisted to localStorage via `zustand/middleware/persist`)
3. Axios interceptor automatically attaches the access token to all requests
4. If a request returns 401, the interceptor tries to refresh the token using the refresh token
5. If refresh fails, the user is logged out and redirected to `/login`

### 9.3 Data Fetching Pattern

All data fetching uses **TanStack React Query** with the following pattern:

- **Queries**: Auto-refetch at intervals (5s for packets, 10s for dashboard/alerts, 15s for threats)
- **Mutations**: Optimistic updates where applicable, cache invalidation on success
- **Stale time**: 30 seconds (default), prevents unnecessary refetches
- **Retry**: 1 retry on failure, no retry on 4xx errors
- **Window focus**: Refetching on window focus is disabled (to avoid noise during development)

### 9.4 UI Components

The frontend uses **Radix UI** primitives for accessible, customizable components:

| Component | Usage |
|---|---|
| Button | 6 variants (default, destructive, outline, secondary, ghost, link) |
| Card | Composable card with header, title, description, content, footer |
| Badge | 8 color variants (default, success, warning, danger, info, etc.) |
| Switch | Toggle control (used for notification enable/disable) |
| Scroll Area | Custom scrollable container with themed scrollbar |

---

## 10. Security

### 10.1 Authentication & Authorization

- **Password Hashing**: bcrypt with 12 rounds of salting via `passlib`
- **JWT Tokens**: HS256 signed tokens with configurable expiry (30 min access / 7 days refresh)
- **Token Rotation**: Refresh tokens are single-use; each refresh issues a new refresh token
- **Role-Based Access**: Three roles (admin, analyst, viewer) with granular permissions
- **Soft Delete**: Records are flagged as deleted, never permanently removed

### 10.2 API Security

- **CORS**: Configurable origins (default: all origins in dev, locked in production)
- **Rate Limiting**: 100 requests per 60-second window per client
- **Input Validation**: All inputs validated via Pydantic schemas
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy ORM

## 11. Project Structure

```
AI-IDS/
│
├── backend/                          # Python FastAPI backend
│   ├── main.py                       # Application entry point
│   ├── run.py                        # Development server runner
│   ├── requirements.txt              # Python dependencies
│   │
│   ├── alerts/                       # Notification system
│   │   └── alert_engine.py           # 7 notification channels + dispatcher
│   │
│   ├── api/                          # REST API
│   │   ├── router.py                 # Route registration
│   │   ├── health.py                 # Health check endpoints
│   │   └── endpoints/                # Route handlers
│   │       ├── auth.py               # Authentication endpoints
│   │       ├── users.py              # User management
│   │       ├── packets.py            # Packet and flow data
│   │       ├── threats.py            # Threat data
│   │       ├── alerts.py             # Alert management
│   │       ├── dashboard.py          # Dashboard statistics
│   │       ├── ml.py                 # ML training and prediction
│   │       ├── logs.py               # Audit logs
│   │       ├── settings.py           # Application settings
│   │       └── simulation.py         # Traffic simulation
│   │
│   ├── config/                       # Configuration
│   │   └── settings.py               # Environment variable management
│   │
│   ├── core/                         # Core utilities
│   │   └── logging.py                # Structured logging setup
│   │
│   ├── database/                     # Database layer
│   │   ├── base_model.py             # Abstract base ORM model
│   │   ├── session.py                # Async database session
│   │
│   ├── feature_engine/               # ML feature extraction
│   │   └── extractor.py              # 80+ feature computation
│   │
│   ├── middleware/                   # FastAPI middleware
│   │   ├── auth_middleware.py         # JWT verification
│   │   └── error_handler.py          # Exception handling
│   │
│   ├── ml/                           # Machine learning
│   │   └── pipeline.py               # Training, prediction, evaluation
│   │
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── user.py                   # User, Role, Permission
│   │   ├── packet.py                 # Packet, Flow
│   │   ├── threat.py                 # Threat, Prediction, MLModel
│   │   ├── alert.py                  # Alert, NotificationHistory
│   │   └── audit.py                  # AuditLog, Setting
│   │
│   ├── repositories/                 # Data access layer
│   │   ├── base.py                   # Generic CRUD operations
│   │   ├── packet_repository.py      # Packet-specific queries
│   │   ├── threat_repository.py      # Threat-specific queries
│   │   └── user_repository.py        # User-specific queries
│   │
│   ├── schemas/                      # Pydantic schemas
│   │   ├── packet.py                 # Alert response schemas
│   │   └── user.py                   # User request/response schemas
│   │
│   ├── security/                     # Authentication utilities
│   │   └── auth.py                   # JWT creation and password hashing
│   │
│   ├── services/                     # Business logic
│   │   ├── auth_service.py           # Authentication business logic
│   │   └── simulation_service.py     # Traffic generation engine
│   │
│   ├── alembic/                      # Database migrations
│   │   ├── alembic.ini
│   │   └── versions/                 # Migration scripts
│   │
│   └── tests/                        # Unit tests
│       ├── test_auth.py
│       └── test_ml.py
│
├── frontend/                         # React TypeScript frontend
│   ├── vite.config.ts                # Vite configuration
│   ├── tailwind.config.js            # Tailwind CSS configuration
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── package.json                  # npm dependencies
│   │
│   └── src/
│       ├── main.tsx                  # Application entry point
│       ├── App.tsx                   # Route definitions
│       ├── index.css                 # Global styles and CSS variables
│       │
│       ├── components/               # Reusable components
│       │   ├── layout/               # Layout components
│       │   │   ├── Layout.tsx        # App shell (sidebar + header + content)
│       │   │   └── Sidebar.tsx       # Navigation sidebar
│       │   ├── ui/                   # UI primitives
│       │   │   ├── badge.tsx         # Badge component
│       │   │   ├── button.tsx        # Button component
│       │   │   ├── card.tsx          # Card component
│       │   │   ├── switch.tsx        # Switch toggle
│       │   │   └── scroll-area.tsx   # Scrollable container
│       │   ├── AnimatedCounter.tsx    # Animated number display
│       │   ├── NotificationBell.tsx  # Alert count badge
│       │   └── NotificationManager.tsx # Browser notification polling
│       │
│       ├── pages/                    # Page components
│       │   ├── Landing.tsx           # Public landing page
│       │   ├── Login.tsx             # Authentication page
│       │   ├── SignUp.tsx            # Registration page
│       │   ├── CompanySetup.tsx      # Company configuration
│       │   ├── Dashboard.tsx         # Main dashboard
│       │   ├── Packets.tsx           # Packet viewer
│       │   ├── Flows.tsx             # Flow viewer
│       │   ├── Threats.tsx           # Threat list
│       │   ├── Alerts.tsx            # Alert management
│       │   ├── Analytics.tsx         # Analytics charts
│       │   ├── ML.tsx               # ML model management
│       │   ├── Users.tsx             # User administration
│       │   ├── Settings.tsx          # Application settings
│       │   └── Logs.tsx              # Audit log viewer
│       │
│       ├── hooks/                    # Custom React hooks
│       │   └── useNotifications.ts   # Notification permission + polling
│       │
│       ├── store/                    # State management
│       │   └── authStore.ts          # Authentication state
│       │
│       ├── services/                 # API client
│       │   └── api.ts                # Axios instance + API modules
│       │
│       ├── types/                    # TypeScript type definitions
│       │   └── index.ts              # All interfaces and types
│       │
│       └── utils/                    # Utility functions
│           └── cn.ts                 # Tailwind CSS class merging
│
├── scripts/                          # Utility scripts
│   └── seed.py                       # Database seeder
│
├── datasets/                         # ML datasets
│   └── sample_ids_data.csv           # 1000-row sample dataset
│
├── trained_models/                   # Serialized ML models
│   └── model_gradient_boosting.pkl   # Pre-trained model
│
├── build.sh                          # Deployment build script
├── render.yaml                       # Render.com deployment config
├── requirements.txt                  # Python dependencies
└── .env.example                      # Environment variable template
```

## 12. Conclusion

AI-IDS demonstrates how modern web technologies and machine learning can be combined to build an effective intrusion detection system. Key achievements include:

- **Four ML models** trained and evaluated, with automatic best-model selection
- **80+ network flow features** extracted for comprehensive traffic analysis
- **12 attack types** detectable through the detection pipeline
- **7 notification channels** for real-time alerting
- **14-page web application** with real-time data visualization
- **Complete authentication system** with JWT token rotation and RBAC
- **Simulation engine** for generating realistic network traffic

The system is production-ready and deployable to cloud platforms like Render.com with a single configuration file.
