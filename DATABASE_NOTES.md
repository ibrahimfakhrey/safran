# Database Location Notes

## Important: Database Files

The application uses **TWO** database files:

1. **Main Database**: `apartment_platform.db` (root directory)
   - Configured in `config.py`
   - Used by seed scripts and direct SQLite queries

2. **Instance Database**: `instance/app.db`
   - **This is what the running Flask app actually uses!**
   - Flask automatically uses the instance folder for database files
   - Must be kept in sync with the main database

## Solution

When the app is running, it uses `instance/app.db`. To ensure changes take effect:

```bash
# After seeding or modifying apartment_platform.db, copy it:
cp apartment_platform.db instance/app.db

# Or run seed scripts which will use the correct database through the app context
python3 seed_cars.py
```

## Why Two Databases?

Flask's instance folder pattern separates instance-specific data from the application code. This is useful for deployment but can cause confusion in development.

## Recommendation

Always use the seed scripts or Flask app context to modify the database, as they will use the correct database file automatically.
