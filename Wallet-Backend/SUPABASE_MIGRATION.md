# Migrating to Supabase

This guide will help you migrate your Wallet app from local PostgreSQL to Supabase, enabling seamless access across devices.

## Prerequisites

- Your current local PostgreSQL database should be running
- Python environment with all dependencies installed
- A Supabase account (free tier is sufficient)

## Step 1: Export Your Current Data

First, let's safely export your existing data:

```bash
cd Wallet-Backend
python migrate_to_supabase.py
```

Choose option 1 or 3 to export your data. This will create a JSON backup in the `data_export/` folder.

## Step 2: Set Up Supabase

### 2.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/log in
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `wallet-app` (or your preferred name)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to your location
5. Click "Create new project"
6. Wait for the project to be created (takes ~2 minutes)

### 2.2 Get Connection Details

1. In your Supabase dashboard, go to **Settings > Database**
2. Copy the **Connection string** (URI format)
3. Go to **Settings > API**  
4. Copy the **Project URL** and **anon public** key

### 2.3 Create Environment File

Create a `.env` file in the `Wallet-Backend/` directory:

```env
# Database Configuration (Supabase)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Supabase Configuration (optional, for future features)
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_KEY=[YOUR-ANON-KEY]

# JWT Authentication
SECRET_KEY=your-secret-key-here-make-it-long-and-random-at-least-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
LOG_LEVEL=INFO
```

**Replace the placeholders:**
- `[YOUR-PASSWORD]`: The database password you created
- `[PROJECT-REF]`: Your project reference from the connection string
- `[YOUR-ANON-KEY]`: The anon public key from API settings
- `SECRET_KEY`: Generate a long, random string (you can use the same one as before)

## Step 3: Install Dependencies

Update your Python dependencies to include Supabase support:

```bash
pip install -r requirements.txt
```

## Step 4: Run Database Migrations

Create the database schema in Supabase:

```bash
alembic upgrade head
```

This will create all the necessary tables in your Supabase database.

## Step 5: Import Your Data (Optional)

If you want to keep your existing data:

```bash
python import_from_json.py data_export/wallet_data_export_[TIMESTAMP].json
```

Replace `[TIMESTAMP]` with the actual timestamp from your export file.

## Step 6: Test the Application

1. Start your backend:
   ```bash
   uvicorn main:app --reload
   ```

2. Start your frontend:
   ```bash
   cd ../Wallet-Frontend
   npm run dev
   ```

3. Test login and basic functionality to ensure everything works

## Step 7: Deploy Your Application

Now that you're using Supabase, you can deploy your application to any cloud platform:

### Backend Deployment Options:
- **Railway**: Easy deployment with Git integration
- **Heroku**: Popular platform with free tier
- **Vercel**: Great for API deployments
- **DigitalOcean App Platform**: Simple and affordable

### Frontend Deployment Options:
- **Vercel**: Excellent for React apps
- **Netlify**: Great for static sites with API integration
- **GitHub Pages**: Free for public repositories

### Environment Variables for Deployment

Make sure to set these environment variables in your deployment platform:

```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_KEY=[YOUR-ANON-KEY]
SECRET_KEY=[YOUR-SECRET-KEY]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOG_LEVEL=INFO
```

## Benefits of Using Supabase

✅ **Cloud-hosted**: Access from anywhere  
✅ **Automatic backups**: Your data is safe  
✅ **Real-time capabilities**: Future features like live updates  
✅ **Authentication**: Built-in auth system (future enhancement)  
✅ **API**: Auto-generated REST and GraphQL APIs  
✅ **Dashboard**: Visual database management  
✅ **Free tier**: Generous limits for personal use  

## Troubleshooting

### Connection Issues
- Double-check your DATABASE_URL format
- Ensure your Supabase project is active
- Verify the password and project reference

### Migration Errors
- Make sure your local database is running when exporting
- Check that all dependencies are installed
- Verify the JSON export file exists before importing

### Import Issues
- Ensure migrations have been run (`alembic upgrade head`)
- Check for duplicate data if re-importing
- Verify foreign key constraints are satisfied

## Security Notes

- Never commit your `.env` file to version control
- Use strong, unique passwords for your database
- Rotate your SECRET_KEY if compromised
- Consider enabling Row Level Security (RLS) in Supabase for production

## Next Steps

Once migration is complete:

1. **Mobile Access**: Your app can now be accessed from mobile browsers
2. **PWA**: Consider making it a Progressive Web App for mobile installation
3. **Real-time Features**: Explore Supabase real-time subscriptions
4. **Enhanced Auth**: Use Supabase Auth for social logins
5. **File Storage**: Use Supabase Storage for receipts/attachments

---

**Need Help?** 
- Check the [Supabase Documentation](https://supabase.com/docs)
- Review the migration scripts for detailed error messages
- Ensure your local environment is properly configured 