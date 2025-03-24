import asyncio
import logging
import os
import subprocess
from datetime import datetime

from core import settings


def generate_dump_name(db_name: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{db_name}_backup_{timestamp}.dump"


async def create_database_dump():
    db = settings.db
    dump_file = db.backups_dir + generate_dump_name(db.database)
    if os.name == "nt":  # Windows
        pgpass_path = os.path.join(os.getenv("APPDATA"), "postgresql", "pgpass.conf")
        os.makedirs(os.path.dirname(pgpass_path), exist_ok=True)
    else:  # Linux/macOS
        pgpass_path = os.path.expanduser("~/.pgpass")

    # Записываем пароль в pgpass
    with open(pgpass_path, "w") as f:
        f.write(f"{db.host}:{db.port}:{db.database}:{db.user}:{db.password}\n")

    # Устанавливаем права доступа (только владелец может читать)
    os.chmod(pgpass_path, 0o600)

    try:
        cmd = [
            "pg_dump",
            "-U",
            db.user,
            "-h",
            db.host,
            "-p",
            str(db.port),
            "-F",
            "c",  # custom format
            "-f",
            dump_file,
            db.database,
        ]

        env = os.environ.copy()
        env["PGPASSFILE"] = pgpass_path
        subprocess.run(cmd, check=True, env=env, text=True)

    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка дампа: {e.stderr}")
    finally:
        os.remove(pgpass_path)


if __name__ == "__main__":
    asyncio.run(create_database_dump)
