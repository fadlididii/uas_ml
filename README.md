# HeartLink - Dating Web App 

Backend untuk aplikasi dating menggunakan Flask, SQLAlchemy, dan PostgreSQL.

## Setup dan Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd flask-uas-ml
```

### 2. Setup Virtual Environment
```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
1. Pada requirements.txt file dlib perlu disesuaikan path nya!!! dan btw ini khusus (py ver 3.12)
2. kalau python versi lain bisa download file di -> https://github.com/z-mahmud22/Dlib_Windows_Python3.x

### 4. Setup PostgreSQL Database
1. Install PostgreSQL
2. Buat database baru:
```sql
CREATE DATABASE dating_app;
CREATE DATABASE dating_app_dev;
```

### 5. Konfigurasi Environment
1. Buat file `.env` dan sesuaikan konfigurasi database:
```env

# Flask Configuration
FLASK_CONFIG=development
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/dating_app
DEV_DATABASE_URL=postgresql://username:password@localhost/dating_app_dev

# Security Keys
SECRET_KEY= bebas isi apa aja
JWT_SECRET_KEY= bebas isi apa aja

# Application Settings
APP_NAME=HeartLink Dating App
APP_VERSION=1.0.0

```

### 6. Inisialisasi Database
```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

### 7. Jalankan Aplikasi
```bash
python app.py
# atau
python run.py
```

### 9. Generate Dummy User (kalau mau)
```bash
python generate_user.py
```

Aplikasi akan berjalan di `http://localhost:5000`


## Web Routes (Frontend)

- `/` - Landing page
- `/register` - Registrasi form
- `/login` - Login (redirect ke index)
- `/profile-setup` - Setup profile setelah registrasi

- `/preferences` - Setup preferensi pasangan
- `/match-feed` - Feed pasangan (placeholder)

## Alur Aplikasi

1. **Index Page** → User memilih Register atau Login
2. **Register** → User membuat akun baru
3. **Login** → User login dengan email/password
4. **Profile Setup** → User mengisi data profile
5. **Preferences** → User mengisi preferensi pasangan
6. **Visual Test** → User mengisi preferensi visual
7. **Match Feed** → Menampilkan calon pasangan (next step)
8. **Match Details** → Menampilkan detail pasangan

## Tech Stack

- **Backend**: Flask 2.3.2
- **Database**: PostgreSQL dengan SQLAlchemy 3.0.3
- **Authentication**: Session-based dengan password hashing
- **Environment**: Python 3.8+

## License

MIT License