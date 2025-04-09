import asyncio
import logging
import os
import subprocess
from datetime import datetime

import aiohttp

from core import settings
from core.logger_init import init_logger


def generate_dump_name(db_name: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{db_name}_backup_{timestamp}.dump"


async def create_database_dump() -> str:
    db = settings.db
    file_name = generate_dump_name(db.database)
    backups_dir = db.backups_dir
    dump_file = os.path.join(backups_dir, file_name)

    # Создаем директорию для резервных копий, если она не существует
    os.makedirs(backups_dir, exist_ok=True)

    # Устанавливаем права доступа к директории
    os.chmod(backups_dir, 0o777)  # Установка прав доступа на 777

    # Создаем pgpass файл
    if os.name == "nt":  # Windows
        pgpass_path = os.path.join(
            os.getenv("APPDATA", ""), "postgresql", "pgpass.conf"
        )
    else:  # Linux/macOS
        pgpass_path = os.path.expanduser("~/.pgpass")

    try:

        # Записываем пароль в pgpass
        with open(pgpass_path, "w") as f:
            f.write(f"{db.host}:{db.port}:{db.database}:{db.user}:{db.password}\n")

        # Устанавливаем права доступа
        os.chmod(pgpass_path, 0o600)

        # Создаем команду
        cmd = [
            "pg_dump",
            "-U",
            db.user,
            "-h",
            db.host,
            "-p",
            str(db.port),
            "-F",
            "c",
            "-f",
            dump_file,
            db.database,
        ]

        # Запускаем команду асинхронно
        env = os.environ.copy()
        env["PGPASSFILE"] = pgpass_path

        loop = asyncio.get_running_loop()
        process = await loop.run_in_executor(
            None, lambda: subprocess.run(cmd, env=env, capture_output=True, text=True)
        )

        # Проверяем статус
        if process.returncode != 0:
            logging.error(f"Ошибка дампа: {process.stderr}")
            raise subprocess.CalledProcessError(process.returncode, cmd)

    finally:
        # Удаляем pgpass файл
        try:
            os.remove(pgpass_path)
        except FileNotFoundError:
            logging.warning("Файл pgpass не найден для удаления")

    return file_name


class YaDisk:
    API_URL = "https://cloud-api.yandex.net/v1/disk/resources"

    def __init__(self) -> None:
        self.token = settings.yandex_disk.token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "OAuth {}".format(self.token),
        }
        self.folder_name = "db_backup"

    async def _create_folder(self, session: aiohttp.ClientSession) -> None:
        try:
            async with session.put(
                self.API_URL, headers=self.headers, params={"path": self.folder_name}
            ) as response:
                if response.status not in (201, 409):
                    raise Exception(f"Статус: {response.status}")
        except Exception as e:
            logging.error(f"Ошибка при создании папки на Яндекс.Диске: {e}")

    async def get_upload_url(
        self, session: aiohttp.ClientSession, file_name: str
    ) -> str | None:
        upload_url = self.API_URL + "/upload"
        params = {"path": f"{self.folder_name}/{file_name}", "overwrite": "true"}
        try:
            async with session.get(
                upload_url, headers=self.headers, params=params
            ) as response:
                if response.status != 200:
                    raise Exception(f"Статус: {response.status}")
                data = await response.json()
                return str(data.get("href", ""))
        except Exception as e:
            logging.error(f"Ошибка при получении ссылки для загрузки файла: {e}")
            return None

    async def copy_photos_to_disk(self, file_name: str) -> None:
        async with aiohttp.ClientSession() as session:
            await self._create_folder(session)
            upload_url = await self.get_upload_url(session, file_name)
            if not upload_url:
                return None

            file_path = os.path.join(settings.db.backups_dir, file_name)
            try:
                with open(file_path, "rb") as f:
                    async with session.put(upload_url, data=f) as response:
                        if response.status != 201:
                            raise Exception(f"Статус:{response.status}")
                        # await response.read() # необязательно, но можно прочитать ответ
            except Exception as e:
                logging.error(f"Ошибка при загрузке файла: {e}")


async def create_backup() -> str | None:
    init_logger(log_file="backup.log")
    if dump_file := await create_database_dump():
        yadisk = YaDisk()
        await yadisk.copy_photos_to_disk(dump_file)
    return dump_file


if __name__ == "__main__":
    asyncio.run(create_backup())
