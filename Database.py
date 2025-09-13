import aiosqlite


class Database:

    # Добавление записи брони в базу данных appointments
    @staticmethod
    async def insert_appointment(user_id: str,
                                 service_id: str,
                                 date: str,
                                 time_start: str,
                                 time_end: str) -> None:

        connect = await aiosqlite.connect("database.db")
        cursor = await connect.cursor()

        await cursor.execute(
            "INSERT INTO appointments (user_id, \
            service_id, \
            date, \
            time_start, \
            time_end) \
            VALUES (?, ?, ?, ?, ?)",
            (
                user_id,
                service_id,
                date,
                time_start,
                time_end
            )
        )

        await connect.commit()
        await cursor.close()
        await connect.close()

    # Получить все косметические процедуры из базы данных services
    @staticmethod
    async def get_services() -> tuple | bool:

        connect = await aiosqlite.connect("database.db")
        cursor = await connect.cursor()

        result = await cursor.execute(
            "SELECT * FROM services"
        )

        services = await result.fetchall()

        if not services:
            return False

        return services
