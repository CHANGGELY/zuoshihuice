from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 数据与缓存目录（可用环境变量覆盖）
    DATA_DIR: Path = Path("K线data").resolve()
    CACHE_DIR: Path = Path("cache").resolve()

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

settings = Settings()
# 确保目录存在
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
