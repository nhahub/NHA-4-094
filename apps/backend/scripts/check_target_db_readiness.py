import sys
import os
import psycopg2
from supabase import create_client, Client
from supabase.lib.client_options import SyncClientOptions
import httpx

POOLER_REGIONS = [
    "eu-central-1",  # Frankfurt
    "eu-west-1",     # Ireland
    "eu-west-2",     # London
    "eu-west-3",     # Paris
    "us-east-1",     # N. Virginia
    "us-east-2",     # Ohio
    "us-west-1",     # N. California
    "us-west-2",     # Oregon
    "ap-southeast-1",# Singapore
    "ap-northeast-1",# Tokyo
    "ap-southeast-2",# Sydney
    "sa-east-1"      # São Paulo
]

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
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                os.environ.setdefault(k, v)

def main():
    print("=" * 60)
    print("         SUPABASE TARGET DATABASE READINESS CHECKER")
    print("=" * 60)

    # Load environments
    load_dotenv()
    
    database_url = os.environ.get("DATABASE_URL")
    db_password = os.environ.get("SUPABASE_DB_PASSWORD")
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_service_role = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    supabase_storage_bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "study-documents")

    project_ref = None
    if supabase_url:
        project_ref = supabase_url.replace("https://", "").replace("http://", "").split(".")[0]

    print("\n--- ENVIRONMENT VALIDATION ---")
    print(f" * SUPABASE_URL: {supabase_url if supabase_url else '[MISSING]'}")
    print(f"   - Project Reference: {project_ref if project_ref else '[UNDETECTED]'}")
    print(f" * SUPABASE_SERVICE_ROLE_KEY: {'[Configured]' if supabase_service_role else '[MISSING]'}")
    print(f" * SUPABASE_STORAGE_BUCKET: {supabase_storage_bucket}")
    print(f" * DATABASE_URL: {'[Configured]' if database_url else '[NOT CONFIGURED]'}")
    print(f" * SUPABASE_DB_PASSWORD: {'[Configured]' if db_password else '[MISSING]'}")

    # Check gitignore status
    gitignore_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.gitignore"))
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gitignore_content = f.read()
        is_ignored = ".env" in gitignore_content
        print(f" * .env Ignored in git: {'Yes (Correct/Safe)' if is_ignored else 'NO (WARNING: Commit Risk!)'}")
    else:
        print(" * .env Ignored in git: [No .gitignore found]")

    # Check for old project refs in config
    print("\n--- OLD REFS IN CONFIG ---")
    old_project_ref = "iobvuyfhqzwjuciaskhd"
    
    if supabase_url and old_project_ref in supabase_url:
        print(f" * WARNING: Active SUPABASE_URL still points to the old project: {old_project_ref}")
    else:
        print(f" * Active SUPABASE_URL: Verified (does not point to old project {old_project_ref})")

    # Step 1: PostgreSQL Connection Probing
    print("\n[1/5] Connecting to target PostgreSQL...")
    conn = None
    cursor = None
    success_conn = False

    if database_url:
        try:
            print(" -> Trying connection via DATABASE_URL...")
            conn = psycopg2.connect(dsn=database_url, connect_timeout=5)
            cursor = conn.cursor()
            success_conn = True
            print(" -> SUCCESS: PostgreSQL database connection established via DATABASE_URL.")
        except Exception as e:
            print(f" -> FAILURE: Connection via DATABASE_URL failed: {str(e)}")
    
    # If DATABASE_URL didn't work or is missing, try direct and pooler options
    if not success_conn and project_ref and db_password:
        direct_host = f"db.{project_ref}.supabase.co"
        try:
            print(f" -> Trying direct host connection ({direct_host}:5432)...")
            conn = psycopg2.connect(
                host=direct_host,
                port=5432,
                user="postgres",
                password=db_password,
                database="postgres",
                connect_timeout=3
            )
            cursor = conn.cursor()
            success_conn = True
            print(" -> SUCCESS: PostgreSQL database connection established via direct host.")
        except Exception as e:
            print(f" -> INFO: Direct host connection failed (Standard for IPv4-only networks). Error: {str(e)}")

        if not success_conn:
            print(" -> Probing pooled regional database hosts on port 6543...")
            for region in POOLER_REGIONS:
                pooler_host = f"aws-0-{region}.pooler.supabase.com"
                username = f"postgres.{project_ref}"
                try:
                    conn = psycopg2.connect(
                        host=pooler_host,
                        port=6543,
                        user=username,
                        password=db_password,
                        database="postgres",
                        connect_timeout=3
                    )
                    cursor = conn.cursor()
                    success_conn = True
                    print(f" -> SUCCESS: Connected to pooled database in region: {region}!")
                    break
                except Exception as e:
                    err_msg = str(e).strip()
                    if "password authentication failed" in err_msg or "FATAL" in err_msg and "password" in err_msg:
                        print(f"      * Found host {pooler_host} but password authentication failed.")
                        break
                    continue

    # Step 2: Database Schema Metadata Check (only if connected)
    print("\n[2/5] Inspecting database tables and schemas...")
    if success_conn and conn:
        try:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = [r[0] for r in cursor.fetchall()]
            
            cursor.execute("SELECT extname FROM pg_extension")
            extensions = [r[0] for r in cursor.fetchall()]

            cursor.execute("""
                SELECT routine_name 
                FROM information_schema.routines 
                WHERE routine_schema='public'
            """)
            functions = [r[0] for r in cursor.fetchall()]

            cursor.execute("SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname='public'")
            rls_status = {r[0]: r[1] for r in cursor.fetchall()}

            cursor.execute("""
                SELECT policyname, tablename, cmd, qual, with_check 
                FROM pg_policies 
                WHERE schemaname='public'
            """)
            policies = cursor.fetchall()

            print(" --- DATABASE METADATA REPORT ---")
            print(f" * Installed Extensions: {extensions}")
            if tables:
                print(f" * Existing Tables in 'public' schema ({len(tables)} found):")
                for t in tables:
                    rls_enabled = rls_status.get(t, False)
                    print(f"   - {t} (RLS Enabled: {rls_enabled})")
            else:
                print(" * Existing Tables: None (Database is COMPLETELY EMPTY!)")

            if functions:
                print(f" * Existing Stored Procedures/RPCs ({len(functions)} found):")
                for f in functions:
                    print(f"   - {f}")
            else:
                print(" * Existing Stored Procedures: None")

            if policies:
                print(f" * Configured RLS Policies ({len(policies)} found):")
                for p in policies:
                    print(f"   - Policy: {p[0]} on Table: {p[1]} (Command: {p[2]})")
                    print(f"     USING: {p[3]}")
                    print(f"     WITH CHECK: {p[4]}")
            else:
                print(" * Configured RLS Policies: None")
            conn.close()
        except Exception as e:
             print(f" -> FAILURE during metadata query: {str(e)}")
    else:
        print(" -> SKIP: Database metadata lookup skipped (No active database connection).")

    # Step 3: Supabase client connection check
    print("\n[3/5] Inspecting Supabase client connectivity and storage...")
    success_supabase_client = False
    if not supabase_url or not supabase_service_role:
        print(" -> FAILURE: Supabase client initialization skipped (Missing URL or Service Role key).")
    else:
        try:
            custom_httpx = httpx.Client(http2=False, timeout=10.0)
            options = SyncClientOptions(httpx_client=custom_httpx)
            supabase: Client = create_client(supabase_url, supabase_service_role, options=options)
            print(" -> SUCCESS: Supabase Python Client successfully initialized.")
            success_supabase_client = True
        except Exception as e:
            print(f" -> FAILURE: Supabase client initialization failed: {str(e)}")

    # Step 4: Storage Bucket check
    print(f"\n[4/5] Checking storage bucket '{supabase_storage_bucket}'...")
    if success_supabase_client:
        try:
            bucket = supabase.storage.get_bucket(supabase_storage_bucket)
            # Safe attribute check on SyncBucket object
            is_public = False
            if hasattr(bucket, "public"):
                is_public = bucket.public
            elif isinstance(bucket, dict):
                is_public = bucket.get("public", False)
                
            print(f" -> SUCCESS: Storage bucket '{supabase_storage_bucket}' exists.")
            print(f"    Bucket Privacy: {'PUBLIC (WARNING)' if is_public else 'PRIVATE (Correct/Safe)'}")
        except Exception as e:
            err_msg = str(e).lower()
            if "not found" in err_msg or "404" in err_msg:
                print(f" -> WARNING: Storage bucket '{supabase_storage_bucket}' does not exist on the target project.")
                print(f"    Action item: Must be created as a PRIVATE bucket named '{supabase_storage_bucket}' in Storage.")
            else:
                print(f" -> FAILURE: Bucket check returned error: {str(e)}")
    else:
        print(" -> SKIP: Storage bucket check skipped (No active Supabase Client).")

    # Step 5: Safety Checks
    print("\n[5/5] Performing local migration safety verification...")
    migration_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app/db/migrations"))
    m001_path = os.path.join(migration_dir, "001_init_documents.sql")
    m002_path = os.path.join(migration_dir, "002_memory_personalization.sql")
    m004_path = os.path.join(migration_dir, "004_memory_enhancements.sql")

    print(" * Local Migration Files Status:")
    for path, name in [(m001_path, "001"), (m002_path, "002"), (m004_path, "004")]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            has_pgcrypto = "pgcrypto" in content
            has_uuid_ossp = "uuid-ossp" in content
            has_rls = "ENABLE ROW LEVEL SECURITY" in content
            print(f"   - Migration {name}: Exists. (pgcrypto: {has_pgcrypto}, uuid-ossp: {has_uuid_ossp}, RLS: {has_rls})")
        else:
            print(f"   - Migration {name}: [MISSING!]")

    print("\n" + "=" * 60)
    print("                READINESS CHECK COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
