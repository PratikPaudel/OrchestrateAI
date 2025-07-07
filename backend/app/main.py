from fastapi import FastAPI
from pathlib import Path
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

# Enhanced debugging for environment variables
def debug_environment():
    print("=" * 60)
    print("ENHANCED ENVIRONMENT DEBUG")
    print("=" * 60)
    
    # Check current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if .env file exists in current directory
    env_file = Path('.env')
    print(f".env file exists in current directory: {env_file.exists()}")
    
    if env_file.exists():
        print(f".env file path: {env_file.absolute()}")
        print(f".env file size: {env_file.stat().st_size} bytes")
        
        # Try to read the .env file content (first 500 chars)
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f".env file content preview (first 300 chars):")
                print(repr(content[:300]))  # Use repr to show hidden characters
                print("...")
                
                # Count lines and check for common issues
                lines = content.splitlines()
                print(f"Total lines in .env: {len(lines)}")
                
                # Check for API key lines
                api_lines = [line for line in lines if any(key in line.upper() for key in ['GROQ', 'OPENAI', 'GEMINI', 'EXA'])]
                print(f"API key lines found: {len(api_lines)}")
                for line in api_lines:
                    # Show structure without revealing keys
                    if '=' in line:
                        key, value = line.split('=', 1)
                        print(f"  {key.strip()}=<{len(value.strip())} chars>")
                    else:
                        print(f"  {line} (no = found)")
                        
        except Exception as e:
            print(f"Error reading .env file: {e}")
    
    # Try loading dotenv with different approaches
    print("\n" + "=" * 40)
    print("DOTENV LOADING TESTS")
    print("=" * 40)
    
    # Method 1: Default load_dotenv()
    load_result = load_dotenv()
    print(f"load_dotenv() returned: {load_result}")
    
    # Method 2: Explicit path
    load_result_explicit = load_dotenv('.env')
    print(f"load_dotenv('.env') returned: {load_result_explicit}")
    
    # Method 3: Override existing
    load_result_override = load_dotenv(override=True)
    print(f"load_dotenv(override=True) returned: {load_result_override}")
    
    # Check environment variables before and after
    print("\n" + "=" * 40)
    print("ENVIRONMENT VARIABLES CHECK")
    print("=" * 40)
    
    api_keys = ['EXA_API_KEY', 'OPENAI_API_KEY', 'GEMINI_API_KEY', 'GROQ_API_KEY']
    
    for key in api_keys:
        value = os.getenv(key)
        if value:
            print(f"✅ {key}: SET (length: {len(value)}, starts with: '{value[:10]}...')")
        else:
            print(f"❌ {key}: NOT SET")
    
    # Check all environment variables that might be API keys
    print("\n" + "=" * 40)
    print("ALL API-RELATED ENVIRONMENT VARIABLES")
    print("=" * 40)
    
    api_vars = []
    for key, value in os.environ.items():
        if 'API' in key.upper() or 'KEY' in key.upper():
            preview = value[:10] + '...' if len(value) > 10 else value
            api_vars.append(f"{key}: {preview}")
    
    if api_vars:
        for var in sorted(api_vars):
            print(f"  {var}")
    else:
        print("  No API-related environment variables found")
    
    print("=" * 60)
    print("END DEBUG - NOW ATTEMPTING TO START APPLICATION")
    print("=" * 60)

# Run debugging first
debug_environment()

# Load environment variables with explicit debugging
print("\nLoading environment variables for application...")
load_dotenv()

# Additional debug output that matches your original code
print(f"EXA_API_KEY loaded: {bool(os.getenv('EXA_API_KEY'))}")
print(f"OPENAI_API_KEY loaded: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"GEMINI_API_KEY loaded: {bool(os.getenv('GEMINI_API_KEY'))}")
print(f"GROQ_API_KEY loaded: {bool(os.getenv('GROQ_API_KEY'))}")

# Now try to import the modules that are failing
print("\nAttempting to import modules...")
try:
    from app.api.routes.jobs import router as api_router
    print("✅ Successfully imported api_router")
except Exception as e:
    print(f"❌ Failed to import api_router: {e}")
    print("This is where the error is occurring!")

try:
    from app.core.graph import research_graph
    print("✅ Successfully imported research_graph")
except Exception as e:
    print(f"❌ Failed to import research_graph: {e}")

app = FastAPI()

# Only add router if it was successfully imported
try:
    app.include_router(api_router, prefix="/api/v1")
    print("✅ Successfully added api_router to app")
except NameError:
    print("❌ api_router not available, skipping router addition")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "OrchestrateAI backend is running. API endpoints coming soon."}

@app.get("/debug/env")
def debug_env():
    return {
        "exa_key_set": bool(os.getenv("EXA_API_KEY")),
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "exa_key_preview": os.getenv("EXA_API_KEY")[:2] + "..." if os.getenv("EXA_API_KEY") else "Not set",
        "openai_key_preview": os.getenv("OPENAI_API_KEY")[:2] + "..." if os.getenv("OPENAI_API_KEY") else "Not set",
        "gemini_key_preview": os.getenv("GEMINI_API_KEY")[:2] + "..." if os.getenv("GEMINI_API_KEY") else "Not set",
        "groq_key_preview": os.getenv("GROQ_API_KEY")[:2] + "..." if os.getenv("GROQ_API_KEY") else "Not set"
    }