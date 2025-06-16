from dataclasses import dataclass
import datetime
import json
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session
from lib import logging
from model import Database, ORMUndoRedoOperation


def serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    raise TypeError("Type not serializable")


@dataclass
class UndoRedoOperation:
    undo: bool  # if not undo then redo
    sql: str
    params: Dict[Any, Any]
    description: str


class UndoRedoManager:
    def __init__(self):
        """
        Initialize with external Database class
        """
        self._db = Database()

    def register(self, undo: List[UndoRedoOperation], redo: List[UndoRedoOperation]):
        """
        Register an operation with explicit undo/redo SQL commands

        Args:
            undo_sql: SQL command to undo this operation
            redo_sql: SQL command to redo this operation
            params: Dictionary of parameters for both commands
            description: Human-readable description
        """

        try:
            # Get next sequence number
            with Session(self._db.engine) as session:
                max_seq = (
                    session.query(ORMUndoRedoOperation.sequence)
                    .filter(ORMUndoRedoOperation.operation_type == "undo")
                    .order_by(ORMUndoRedoOperation.sequence.desc())
                    .first()
                )

                next_seq = (max_seq[0] + 1) if max_seq else 1

                # Store undo operation
                op = ORMUndoRedoOperation(
                    operation_type="undo",
                    sql_command=undo.sql,
                    params=json.dumps(undo.params, default=serialize_datetime),
                    description=undo.description or f"Undo operation {next_seq}",
                    timestamp=datetime.datetime.now(),
                    sequence=next_seq,
                )
                session.add(op)

                # Store redo operation
                op = ORMUndoRedoOperation(
                    operation_type="redo",
                    sql_command=redo.sql,
                    params=json.dumps(redo.params, default=serialize_datetime),
                    description=redo.description or f"Redo operation {next_seq}",
                    timestamp=datetime.datetime.now(),
                    sequence=next_seq,
                )
                session.add(op)

                session.commit()
                logging.info(f"Registered operation: {undo.description or f'Operation {next_seq}'}")

        except Exception as e:
            logging.error(f"Failed to register operation: {e}")
            raise

    def _execute_operation(self, operation_type: str) -> bool:
        """
        Execute the next undo or redo operation

        Args:
            operation_type: Either 'undo' or 'redo'
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with Session(self._db.engine) as session:
                # Get the next operation
                op = (
                    session.query(ORMUndoRedoOperation)
                    .filter(ORMUndoRedoOperation.operation_type == operation_type)
                    .order_by(ORMUndoRedoOperation.sequence.desc())
                    .first()
                )

                if not op:
                    logging.error(f"No {operation_type} operations available")
                    return False

                # Execute the SQL
                result = session.execute(text(op.sql_command), op.params)
                session.commit()

                if result.rowcount > 0:
                    logging.info(f"{operation_type.capitalize()} successful: {op.description}")
                    # Remove the executed operation
                    session.delete(op)
                    session.commit()
                    return True
                else:
                    logging.warning(f"{operation_type.capitalize()} affected 0 rows")
                    return False

        except Exception as e:
            logging.error(f"{operation_type.capitalize()} failed: {e}")
            return False

    def undo(self) -> bool:
        """Execute the next undo operation"""
        return self._execute_operation("undo")

    def redo(self) -> bool:
        """Execute the next redo operation"""
        return self._execute_operation("redo")

    def clear_history(self):
        """Clear all undo/redo history"""
        try:
            with Session(self._db.engine) as session:
                session.query(UndoRedoManager).delete()
                session.commit()
                logging.info("Cleared all undo/redo history")
        except Exception as e:
            logging.error(f"Failed to clear history: {e}")
            raise

    def get_history(self, limit: int = 10) -> list:
        """
        Get recent undo/redo history

        Args:
            limit: Maximum number of operations to return
        Returns:
            List of operation dictionaries
        """
        try:
            with Session(self._db.engine) as session:
                ops = (
                    session.query(ORMUndoRedoOperation)
                    .order_by(ORMUndoRedoOperation.timestamp.desc())
                    .limit(limit)
                    .all()
                )

                return [
                    {
                        "id": op.id,
                        "type": op.operation_type,
                        "description": op.description,
                        "timestamp": op.timestamp,
                        "sql": op.sql_command,
                    }
                    for op in ops
                ]
        except Exception as e:
            logging.error(f"Failed to get history: {e}")
            return []


# Create a single instance for the application
undo_manager = UndoRedoManager()
