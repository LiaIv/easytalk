import firebase_admin
from firebase_admin import credentials, firestore
from google.auth.credentials import AnonymousCredentials
import os
from typing import Optional, Dict

_DEFAULT_APP_NAME = "EASYTALK_DEFAULT_APP" # Custom name to avoid conflict
_firestore_clients_cache: Dict[str, firestore.Client] = {} # Cache clients per app name

def _delete_existing_app(name: str = _DEFAULT_APP_NAME) -> None:
    """Deletes an existing Firebase app by name, if it exists."""
    try:
        existing_app = firebase_admin.get_app(name=name)
        firebase_admin.delete_app(existing_app)
        print(f"[firebase_client] Deleted existing Firebase app: {name}")
    except ValueError:
        # App doesn't exist, no need to delete
        pass
    except Exception as e:
        # Catch any other unexpected errors during deletion
        print(f"[firebase_client] Error deleting Firebase app '{name}': {e}")


def initialize_app_for_context(app_name: str = _DEFAULT_APP_NAME) -> firebase_admin.App:
    """
    Initializes a Firebase app for a specific context (emulator or production).
    It ensures an app is initialized only once per name.
    """
    # Determine if running in emulator environment
    firestore_emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST")
    auth_emulator_host = os.getenv("FIREBASE_AUTH_EMULATOR_HOST")
    is_emulator = bool(firestore_emulator_host and auth_emulator_host)

    print(f"\n[firebase_client] ENTERING initialize_app_for_context for app '{app_name}' (is_emulator={is_emulator})")

    # Check if the app is already initialized to avoid re-initialization errors.
    try:
        return firebase_admin.get_app(name=app_name)
    except ValueError:
        # App doesn't exist, so we'll initialize it.
        pass

    # Determine project_id
    project_id = None
    if is_emulator:
        project_id = os.getenv("GCLOUD_PROJECT", "easytalk-emulator")
    else:
        project_id = os.getenv("GCLOUD_PROJECT") or os.getenv("FIREBASE_PROJECT_ID")
        if not project_id:
            raise ValueError("Project ID not configured for Firebase. Set GCLOUD_PROJECT or FIREBASE_PROJECT_ID in your environment.")

    cred_object = None
    options = {"projectId": project_id}

    if is_emulator:
        # For the emulator, we use AnonymousCredentials to prevent any real auth attempts,
        # which is the cause of test hangs and DefaultCredentialsError.
        print(f"[firebase_client] Initializing in EMULATOR mode for project '{project_id}'.")
        cred_object = AnonymousCredentials()
    else:
        # For production, we check for a service account file first,
        # then fall back to Application Default Credentials (ADC).
        print("[firebase_client] Initializing in PRODUCTION mode.")
        service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if service_account_path and os.path.exists(service_account_path):
            print(f"[firebase_client] Using service account from: {service_account_path}")
            cred_object = credentials.Certificate(service_account_path)
        else:
            # If no service account is found, cred_object remains None,
            # and the SDK will use ADC.
            print("[firebase_client] Service account key not found. Using Application Default Credentials (ADC).")

    try:
        # Initialize the app with the determined credentials and options.
        app = firebase_admin.initialize_app(credential=cred_object, options=options, name=app_name)
        print(f"[firebase_client] Firebase app '{app_name}' initialized successfully.")
        return app
    except Exception as e:
        print(f"[firebase_client] CRITICAL: Failed to initialize Firebase app '{app_name}': {e}")
        # Log environment details for easier debugging.
        print(f"[firebase_client] Env Vars: FIRESTORE_EMULATOR_HOST='{os.getenv('FIRESTORE_EMULATOR_HOST')}', GOOGLE_APPLICATION_CREDENTIALS='{os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}'")
        raise


def get_firestore_client(app_name: str = _DEFAULT_APP_NAME) -> firestore.Client:
    """
    Returns a Firestore client for the Firebase app specified by app_name.
    Retrieves from cache if available, otherwise creates and caches a new client.
    Assumes initialize_app_for_context has been called for this app_name.
    """
    global _firestore_clients_cache
    
    if app_name in _firestore_clients_cache:
        return _firestore_clients_cache[app_name]

    try:
        app_instance = firebase_admin.get_app(name=app_name)
    except ValueError:
        print(f"[firebase_client] ERROR: Firebase app '{app_name}' not found. Ensure 'initialize_app_for_context' was called for this app name.")
        raise Exception(f"Firebase app '{app_name}' not initialized. Call initialize_app_for_context for '{app_name}' first.")
    
    client = firestore.client(app=app_instance)
    _firestore_clients_cache[app_name] = client
    print(f"[firebase_client] Firestore client created and cached for app: {app_name}")
    return client

print(f"[firebase_client] firebase_client.py loaded (module level). Default app name: {_DEFAULT_APP_NAME}")
