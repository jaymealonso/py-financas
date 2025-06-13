from lib import logging
from sqlalchemy import text, Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from model import Database

# SQLAlchemy base model
Base = declarative_base()

class class_undo_manager:
    def __init__(self):
        """
        Initialize with external Database class
        """
        self._db = Database()
        
    def _initialize_database(self):
        """Create the undo_redo_stack table if it doesn't exist"""
        try:
            UndoRedoOperation.__table__.create(bind=self._db.engine, checkfirst=True)
        except Exception as e:
            logging.error(f"Failed to initialize undo_redo table: {e}")
            raise

    def register(self, undo_sql: str, redo_sql: str, params: dict = None, description: str = None):
        """
        Register an operation with explicit undo/redo SQL commands
        
        Args:
            undo_sql: SQL command to undo this operation
            redo_sql: SQL command to redo this operation
            params: Dictionary of parameters for both commands
            description: Human-readable description
        """
        if params is None:
            params = {}
            
        try:
            # Get next sequence number
            with self._db.Session() as session:
                max_seq = session.query(UndoRedoOperation.sequence).filter(
                    UndoRedoOperation.operation_type == 'undo'
                ).order_by(
                    UndoRedoOperation.sequence.desc()
                ).first()
                
                next_seq = (max_seq[0] + 1) if max_seq else 1
                
                # Store undo operation
                op = UndoRedoOperation(
                    operation_type='undo',
                    sql_command=undo_sql,
                    params=params,
                    description=description or f"Undo operation {next_seq}",
                    sequence=next_seq
                )
                session.add(op)
                
                # Store redo operation
                op = UndoRedoOperation(
                    operation_type='redo',
                    sql_command=redo_sql,
                    params=params,
                    description=description or f"Redo operation {next_seq}",
                    sequence=next_seq
                )
                session.add(op)
                
                session.commit()
                logging.info(f"Registered operation: {description or f'Operation {next_seq}'}")
                
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
            with self._db.Session() as session:
                # Get the next operation
                op = session.query(UndoRedoOperation).filter(
                    UndoRedoOperation.operation_type == operation_type
                ).order_by(
                    UndoRedoOperation.sequence.desc()
                ).first()
                
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
        return self._execute_operation('undo')

    def redo(self) -> bool:
        """Execute the next redo operation"""
        return self._execute_operation('redo')

    def clear_history(self):
        """Clear all undo/redo history"""
        try:
            with self._db.Session() as session:
                session.query(UndoRedoOperation).delete()
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
            with self._db.Session() as session:
                ops = session.query(UndoRedoOperation).order_by(
                    UndoRedoOperation.timestamp.desc()
                ).limit(limit).all()
                
                return [{
                    'id': op.id,
                    'type': op.operation_type,
                    'description': op.description,
                    'timestamp': op.timestamp,
                    'sql': op.sql_command
                } for op in ops]
        except Exception as e:
            logging.error(f"Failed to get history: {e}")
            return []

# Create a single instance for the application
manager = class_undo_manager()