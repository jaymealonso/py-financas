from lib import logging
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

class class_undo_manager:
    def __init__(self, engine):
        """
        Initialize with SQLAlchemy engine
        :param engine: SQLAlchemy engine instance
        """
        self._history = {
            "undo": [],  # Stores tuples of (sql_command, params)
            "redo": []   # Stores tuples for redo operations
        }
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    def register(self, sql_command: str, params: dict = None, description: str = None):
        """
        Register an SQL command that was executed
        :param sql_command: SQL command string
        :param params: Dictionary of parameters for the SQL command
        :param description: Human-readable description of the change
        """
        if params is None:
            params = {}
        
        # Store the inverse command for undo
        inverse_sql = self._get_inverse_command(sql_command, params)
        
        self._history["undo"].append({
            "sql": inverse_sql,
            "params": params,
            "description": description or f"Undo: {sql_command}"
        })
        # Clear redo stack when new action is registered
        self._history["redo"].clear()
        logging.info(f"Registered command: {description or sql_command}")

    def _get_inverse_command(self, sql_command: str, params: dict) -> str:
        """
        Generate inverse SQL command for undo operations
        This is a simple implementation - you may need to expand it
        based on your specific SQL commands
        """
        sql_lower = sql_command.lower()
        
        if "insert into" in sql_lower:
            table = sql_command.split()[2]
            return f"DELETE FROM {table} WHERE id = :id"
        elif "delete from" in sql_lower:
            table = sql_command.split()[2]
            # This would need the original row data - you might need to store it
            return f"INSERT INTO {table} (...) VALUES (...)"  # Simplified
        elif "update" in sql_lower:
            parts = sql_command.split()
            table = parts[1]
            set_idx = parts.index("set")
            where_idx = parts.index("where")
            set_clause = " ".join(parts[set_idx+1:where_idx])
            where_clause = " ".join(parts[where_idx:])
            return f"UPDATE {table} SET {self._inverse_set_clause(set_clause)} {where_clause}"
        return sql_command  # Fallback - not ideal

    def _inverse_set_clause(self, set_clause: str) -> str:
        """
        Helper to inverse SET clauses in UPDATE statements
        """
        # This is very simplistic - you'll need to enhance based on your needs
        assignments = set_clause.split(",")
        inversed = []
        for assign in assignments:
            col, val = assign.split("=")
            inversed.append(f"{col.strip()} = previous_{col.strip()}")
        return ", ".join(inversed)

    def _execute_sql(self, sql: str, params: dict) -> bool:
        """Execute SQL command with error handling"""
        try:
            with self.Session() as session:
                result = session.execute(text(sql), params)
                session.commit()
                return result.rowcount > 0
        except Exception as e:
            logging.error(f"SQL execution failed: {e}")
            return False

    def undo(self) -> bool:
        """Undo the last operation"""
        if not self._history["undo"]:
            logging.error("Nothing to undo")
            return False

        operation = self._history["undo"].pop()
        success = self._execute_sql(operation["sql"], operation["params"])
        
        if success:
            # Move to redo stack
            self._history["redo"].append(operation)
            logging.info(f"Undo successful: {operation['description']}")
        else:
            # Put back in undo stack if failed
            self._history["undo"].append(operation)
            
        return success

    def redo(self) -> bool:
        """Redo the last undone operation"""
        if not self._history["redo"]:
            logging.error("Nothing to redo")
            return False

        operation = self._history["redo"].pop()
        success = self._execute_sql(operation["sql"], operation["params"])
        
        if success:
            # Move back to undo stack
            self._history["undo"].append(operation)
            logging.info(f"Redo successful: {operation['description']}")
        else:
            # Put back in redo stack if failed
            self._history["redo"].append(operation)
            
        return success

    def clear_history(self):
        """Clear all undo/redo history"""
        self._history["undo"].clear()
        self._history["redo"].clear()
        logging.info("Cleared undo/redo history")

# Example initialization:
# from sqlalchemy import create_engine
# engine = create_engine('sqlite:///your_database.db')
# manager = class_undo_manager(engine)