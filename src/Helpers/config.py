from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()
class Settings(BaseSettings):
     
     """
     Class to validate data inherits from Pydantic BaseSetting
     """
     APP_NAME : str
     GOOGLE_API_KEY : str
     FILE_ALLOWED_TYPES :list
     FILE_SIZE_LIMIT:int
     FAST_API_URL:str

     class Config:
        """
        Class will load all the data from .env file and use it for the validation
        """
        env_file = ".env"
    
def get_settings():
     """
     Function that will return an Instance of Settings class
     """
     return Settings()
