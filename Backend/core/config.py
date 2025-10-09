from decouple import config
from dotenv import load_dotenv


load_dotenv()


SECRET_KEY = config('SECRET_KEY')
DATABASE_URL = config('DATABASE_URL')
SMTP_SERVER = config('SMTP_SERVER')
SMTP_PORT = config('SMTP_PORT', cast=int)
EMAIL_USER = config('EMAIL_USER')
EMAIL_PASSWORD = config('EMAIL_PASSWORD')
