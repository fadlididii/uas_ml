# HeartLink - Dating App Backend API

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

### 4. Setup PostgreSQL Database
1. Install PostgreSQL
2. Buat database baru:
```sql
CREATE DATABASE dating_app;
CREATE DATABASE dating_app_dev;
```

### 5. Konfigurasi Environment
1. Copy file `.env` dan sesuaikan konfigurasi database:
```env
DATABASE_URL=postgresql://username:password@localhost/dating_app
DEV_DATABASE_URL=postgresql://username:password@localhost/dating_app_dev
```

### 6. Inisialisasi Database
```bash
python database_setup.py init
```

### 7. Jalankan Aplikasi
```bash
python app.py
# atau
python run.py
```

Aplikasi akan berjalan di `http://localhost:5000`


## Web Routes (Frontend)

- `/` - Landing page
- `/register` - Registrasi form
- `/login` - Login (redirect ke index)
- `/profile-setup` - Setup profile setelah registrasi
- `/welcome` - Welcome page setelah profile setup
- `/preferences` - Setup preferensi pasangan
- `/match-feed` - Feed pasangan (placeholder)

## Alur Aplikasi

1. **Index Page** → User memilih Register atau Login
2. **Register** → User membuat akun baru
3. **Login** → User login dengan email/password
4. **Profile Setup** → User mengisi data profile
5. **Welcome Page** → Halaman selamat datang
6. **Preferences** → User mengisi preferensi pasangan
7. **Match Feed** → Menampilkan calon pasangan (next step)

## Sample Data

Setelah menjalankan `python database_setup.py init`, tersedia sample data:

- **Admin**: admin@heartlink.com / admin123
- **User 1**: john.doe@example.com / password123
- **User 2**: jane.smith@example.com / password123

## Development

### Database Commands
```bash
# Inisialisasi database dengan sample data
python database_setup.py init

# Hanya buat tables
python database_setup.py tables

# Hanya buat sample data
python database_setup.py sample

# Reset database (HATI-HATI: Menghapus semua data)
python database_setup.py reset
```

### Environment Variables
- `FLASK_CONFIG`: development/production
- `FLASK_ENV`: development/production
- `FLASK_DEBUG`: True/False
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT secret key

## Tech Stack

- **Backend**: Flask 2.3.2
- **Database**: PostgreSQL dengan SQLAlchemy 3.0.3
- **Authentication**: Session-based dengan password hashing
- **Environment**: Python 3.8+

## License

MIT License