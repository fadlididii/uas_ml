# HeartLink - Dating App Backend API

Backend RESTful API untuk aplikasi dating menggunakan Flask, SQLAlchemy, dan PostgreSQL.

## Fitur

- ✅ Registrasi dan Login User
- ✅ Manajemen Profile User
- ✅ Pengaturan Preferensi Pasangan
- ✅ RESTful API Endpoints
- ✅ Database PostgreSQL dengan SQLAlchemy
- ✅ Session Management
- ✅ Password Hashing
- ✅ Data Validation

## Database Schema

### Users Table
- `id` (UUID, Primary Key)
- `email` (String, Unique, Not Null)
- `password_hash` (Text, Not Null)
- `is_active` (Boolean, Default: True)
- `is_superuser` (Boolean, Default: False)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

### User Profiles Table
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key)
- `first_name`, `last_name` (String)
- `date_of_birth` (Date)
- `gender` (String)
- `bio` (Text)
- `photo_url` (Text)
- `weight`, `height` (Integer)
- `education`, `location`, `religion` (String)
- `social_care` (Integer)
- `smoking`, `drinking`, `have_pets` (Boolean)
- `cluster_id` (Integer)

### User Preferences Table
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key)
- `age_min`, `age_max` (Integer)
- `same_location` (Boolean)
- `relationship_goal` (String)
- `is_smoking`, `is_drinking` (Boolean)
- `same_religion` (Boolean)
- `partner_social_care` (Integer)
- `partner_education` (String)
- `comfortable_pets` (Boolean)

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

## API Endpoints

### Authentication
- `POST /api/register` - Registrasi user baru
- `POST /api/login` - Login user
- `POST /api/logout` - Logout user

### User Profile
- `GET /api/profile` - Get user profile
- `POST /api/profile` - Create user profile
- `PUT /api/profile` - Update user profile

### User Preferences
- `GET /api/preferences` - Get user preferences
- `POST /api/preferences` - Create user preferences
- `PUT /api/preferences` - Update user preferences

### Utility
- `GET /api/user/status` - Get user completion status
- `GET /api/users` - Get all users (for matching)

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
- **API**: RESTful JSON API
- **Environment**: Python 3.8+

## Next Steps

1. Implementasi algoritma matching berdasarkan preferensi
2. Upload dan manajemen foto profile
3. Real-time messaging
4. Push notifications
5. Machine learning untuk rekomendasi pasangan
6. Mobile app integration

## Troubleshooting

### Database Connection Error
1. Pastikan PostgreSQL service berjalan
2. Cek konfigurasi database di `.env`
3. Pastikan database sudah dibuat

### Import Error
1. Pastikan virtual environment aktif
2. Install ulang dependencies: `pip install -r requirements.txt`

### Session Error
1. Pastikan SECRET_KEY sudah diset
2. Clear browser cookies/session

## Contributing

1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Buat Pull Request

## License

MIT License