from dotenv import load_dotenv
import os 

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")


PrivateKey = "certs/private.pem"
PublicKey = "certs/public.pem"
algorithm: str = "RS256"
access_token_exp_min: int = 5