import os
from dataclasses import dataclass
from datetime import datetime
import shutil

import tomlkit
from tomlkit import TOMLDocument
from tomlkit.items import Table
from rich.traceback import install

from .config_base import ConfigBase
from .official_configs import (
    TelegramBotConfig,
    MaiBotServerConfig,
    ChatConfig,
    DebugConfig,
)

install(extra_lines=3)

TEMPLATE_DIR = "template"


def update_config():
    template_path = f"{TEMPLATE_DIR}/template_config.toml"
    old_config_path = "config.toml"
    new_config_path = "config.toml"

    if not os.path.exists(old_config_path):
        print("[config] 配置文件不存在，从模板创建新配置")
        shutil.copy2(template_path, old_config_path)
        print(f"[config] 已创建新配置文件，请填写后重新运行: {old_config_path}")
        quit()

    with open(old_config_path, "r", encoding="utf-8") as f:
        old_config = tomlkit.load(f)
    with open(template_path, "r", encoding="utf-8") as f:
        new_config = tomlkit.load(f)

    if old_config and "inner" in old_config and "inner" in new_config:
        old_version = old_config["inner"].get("version")
        new_version = new_config["inner"].get("version")
        if old_version and new_version and old_version == new_version:
            print(f"[config] 检测到配置文件版本号相同 (v{old_version})，跳过更新")
            return
        else:
            print(f"[config] 检测到版本号不同: 旧版本 v{old_version} -> 新版本 v{new_version}")
    else:
        print("[config] 已有配置文件未检测到版本号，可能是旧版本。将进行更新")

    backup_dir = "config_backup"
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    old_backup_path = os.path.join(backup_dir, f"config.toml.bak.{timestamp}")
    shutil.copy2(old_config_path, old_backup_path)
    print(f"[config] 已备份旧配置文件到: {old_backup_path}")

    shutil.copy2(template_path, new_config_path)
    print(f"[config] 已创建新配置文件: {new_config_path}")

    def update_dict(target: TOMLDocument | dict, source: TOMLDocument | dict):
        for key, value in source.items():
            if key == "version":
                continue
            if key in target:
                if isinstance(value, dict) and isinstance(target[key], (dict, Table)):
                    update_dict(target[key], value)
                else:
                    try:
                        target[key] = tomlkit.array(str(value)) if isinstance(value, list) else tomlkit.item(value)
                    except (TypeError, ValueError):
                        target[key] = value

    print("[config] 开始合并新旧配置...")
    update_dict(new_config, old_config)
    with open(new_config_path, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(new_config))
    print("[config] 配置文件更新完成，建议检查新配置文件中的内容")
    quit()


@dataclass
class Config(ConfigBase):
    telegram_bot: TelegramBotConfig
    maibot_server: MaiBotServerConfig
    chat: ChatConfig
    debug: DebugConfig


def load_config(config_path: str) -> Config:
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = tomlkit.load(f)
    return Config.from_dict(config_data)


# 更新配置（首次运行触发生成）
update_config()

print("[config] 正在品鉴配置文件...")
global_config = load_config(config_path="config.toml")
print("[config] 加载配置完成！")
