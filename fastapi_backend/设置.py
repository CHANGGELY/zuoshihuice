from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class 配置类(BaseSettings):
    数据目录: Path = Path("K线data").resolve()
    缓存目录: Path = Path("cache").resolve()
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

配置 = 配置类()
配置.数据目录.mkdir(parents=True, exist_ok=True)
配置.缓存目录.mkdir(parents=True, exist_ok=True)
