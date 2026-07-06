import sys
import os
import psycopg2

def load_dotenv():
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()
                # Strip quotes if present
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                os.environ.setdefault(k, v)

def main():
    print("=" * 60)
    print("        SUPABASE SECURE POSTGRESQL MIGRATION RUNNER")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Retrieve connection properties
    database_url = os.environ.get("DATABASE_URL")
    db_password = os.environ.get("SUPABASE_DB_PASSWORD")
    supabase_url = os.environ.get("SUPABASE_URL")
    
    # Deriving properties if DATABASE_URL is not present
    conn_params = {}
    if database_url:
        print("Using connection configuration from: DATABASE_URL")
        conn_params["dsn"] = database_url
    else:
        print("Building connection parameters from environment...")
        
        # Derive Host from SUPABASE_URL
        if not supabase_url:
            print("Error: SUPABASE_URL or DATABASE_URL must be specified in the environment.")
            sys.exit(1)
            
        project_ref = supabase_url.replace("https://", "").replace("http://", "").split(".")[0]
        host = os.environ.get("SUPABASE_DB_HOST", f"db.{project_ref}.supabase.co")
        port = os.environ.get("SUPABASE_DB_PORT", "5432")
        user = os.environ.get("SUPABASE_DB_USER", "postgres")
        dbname = os.environ.get("SUPABASE_DB_NAME", "postgres")
        
        if not db_password:
            print("Error: SUPABASE_DB_PASSWORD is missing in the environment / .env file.")
            print("Please add 'SUPABASE_DB_PASSWORD=your_password' to backend/.env and retry.")
            sys.exit(1)
            
        conn_params.update({
            "host": host,
            "port": port,
            "user": user,
            "password": db_password,
            "database": dbname
        })

    # Find migration script — accepts optional CLI arg, defaults to 003
    migration_filename = sys.argv[1] if len(sys.argv) > 1 else "003_update_embedding_dimension.sql"
    migration_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__), f"../app/db/migrations/{migration_filename}"
    ))

    if not os.path.exists(migration_file):
        print(f"Error: Migration file not found at: {migration_file}")
        sys.exit(1)

    print(f"Reading SQL script: {os.path.basename(migration_file)}")
    with open(migration_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print("Connecting to Supabase PostgreSQL...")
    try:
        conn = psycopg2.connect(**conn_params)
        # Ensure we run in a transaction block
        conn.autocommit = False
        print("Connection established successfully!")
    except Exception as e:
        print("Connection failed: [Redacted Connection Error]")
        # Write technical log message to standard error without printing secrets
        sys.stderr.write(f"Detailed error: {type(e).__name__}\n")
        sys.exit(1)

    print("Executing database migration inside a secure transaction...")
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_content)
        # Commit the transaction on success
        conn.commit()
        print("SUCCESS: Migration applied and committed successfully!")
    except Exception as e:
        # Rollback the transaction on failure
        conn.rollback()
        print("FAILURE: Migration failed. Rollback executed.")
        sys.stderr.write(f"Execution Error: {str(e)}\n")
        conn.close()
        sys.exit(1)

    conn.close()
    print("=" * 60)

if __name__ == "__main__":
    main()
