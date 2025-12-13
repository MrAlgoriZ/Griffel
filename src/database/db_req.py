import asyncpg
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from src.utils.env import Env


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.user = Env.DATABASE.user
        self.password = Env.DATABASE.password
        self.database = Env.DATABASE.database
        self.host = Env.DATABASE.host

    async def create_conn(self):
        return await asyncpg.connect(
            user=self.user,
            password=self.password,
            database=self.database,
            host=self.host,
        )


class BaseTable(ABC):
    @abstractmethod
    async def insert(self, data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def update(self, conditions: Dict[str, Any], data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    async def delete(self, conditions: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    async def select(
        self, conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def select_one(self, conditions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass


class Table(BaseTable):
    def __init__(self, name: str):
        self.name = name
        self.db = Database()

    async def _execute_query(self, query: str, *args) -> Any:
        conn = await self.db.create_conn()
        try:
            result = await conn.fetch(query, *args)
            return result
        finally:
            await conn.close()

    async def _execute_update(self, query: str, *args) -> str:
        conn = await self.db.create_conn()
        try:
            result = await conn.execute(query, *args)
            return result
        finally:
            await conn.close()

    def _build_where_clause(
        self, conditions: Dict[str, Any], start_index: int = 1
    ) -> Tuple[str, List[Any]]:
        if not conditions:
            return "", []

        clauses = []
        values = []
        for i, (key, value) in enumerate(conditions.items(), start_index):
            clauses.append(f"{key} = ${i}")
            values.append(value)

        return " WHERE " + " AND ".join(clauses), values

    def _build_set_clause(
        self, data: Dict[str, Any], start_index: int = 1
    ) -> Tuple[str, List[Any]]:
        clauses = []
        values = []
        for key, value in data.items():
            clauses.append(f"{key} = ${start_index + len(clauses)}")
            values.append(value)

        return ", ".join(clauses), values

    async def insert(self, data: Dict[str, Any]) -> Any:
        if not data:
            raise ValueError("Cannot insert empty data")

        columns = ", ".join(data.keys())
        placeholders = ", ".join(f"${i}" for i in range(1, len(data) + 1))
        query = (
            f"INSERT INTO {self.name} ({columns}) VALUES ({placeholders}) RETURNING *"
        )

        result = await self._execute_query(query, *data.values())
        return result[0] if result else None

    async def update(self, conditions: Dict[str, Any], data: Dict[str, Any]) -> int:
        if not conditions:
            raise ValueError("Update requires at least one condition")
        if not data:
            raise ValueError("Cannot update with empty data")

        data_to_update = dict(data)

        if "bot_mode" in data_to_update and "prompt" not in data_to_update:
            try:
                mode_name = str(data_to_update.get("bot_mode") or "").upper()
                if mode_name and mode_name != "CUSTOM":
                    from src.bot.ai.service.default_models import DefaultModels

                    model_obj = getattr(DefaultModels, mode_name, None)
                    if model_obj and hasattr(model_obj, "system_prompt"):
                        data_to_update["prompt"] = model_obj.system_prompt
            except Exception:
                pass

        set_clause, set_values = self._build_set_clause(data_to_update)
        where_clause, where_values = self._build_where_clause(
            conditions, start_index=len(set_values) + 1
        )

        all_values = set_values + where_values
        query = f"UPDATE {self.name} SET {set_clause}{where_clause}"

        result = await self._execute_update(query, *all_values)
        return int(result.split()[-1]) if result else 0

    async def delete(self, conditions: Dict[str, Any]) -> int:
        if not conditions:
            raise ValueError("Delete requires at least one condition")

        where_clause, values = self._build_where_clause(conditions)
        query = f"DELETE FROM {self.name}{where_clause}"

        result = await self._execute_update(query, *values)
        return int(result.split()[-1]) if result else 0

    async def select(
        self, conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        where_clause, values = (
            self._build_where_clause(conditions) if conditions else ("", [])
        )
        query = f"SELECT * FROM {self.name}{where_clause}"

        result = await self._execute_query(query, *values)
        return [dict(row) for row in result] if result else []

    async def select_one(self, conditions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not conditions:
            raise ValueError("select_one requires at least one condition")

        result = await self.select(conditions)
        return result[0] if result else None

    async def select_by_id(
        self, id_column: str, id_value: Any
    ) -> Optional[Dict[str, Any]]:
        return await self.select_one({id_column: id_value})

    async def exists(self, conditions: Dict[str, Any]) -> bool:
        result = await self.select(conditions)
        return len(result) > 0

    async def count(self, conditions: Optional[Dict[str, Any]] = None) -> int:
        where_clause, values = (
            self._build_where_clause(conditions) if conditions else ("", [])
        )
        query = f"SELECT COUNT(*) as count FROM {self.name}{where_clause}"

        result = await self._execute_query(query, *values)
        return result[0]["count"] if result else 0

    async def bulk_insert(self, data_list: List[Dict[str, Any]]) -> List[Any]:
        if not data_list:
            return []

        results = []
        for data in data_list:
            result = await self.insert(data)
            results.append(result)

        return results

    async def bulk_delete(self, conditions_list: List[Dict[str, Any]]) -> int:
        total_deleted = 0
        for conditions in conditions_list:
            total_deleted += await self.delete(conditions)

        return total_deleted

    async def raw_query(self, query: str, *args) -> List[Dict[str, Any]]:
        result = await self._execute_query(query, *args)
        return [dict(row) for row in result] if result else []
