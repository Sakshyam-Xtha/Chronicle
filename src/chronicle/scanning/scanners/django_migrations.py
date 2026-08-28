from pathlib import Path
import ast
from datetime import datetime,timezone
from .base import Scanner
from chronicle.scanning.context import ScanContext
from chronicle.storage.observations import Observation
from .django_model import MigrationOperation

class DjangoMigrationScanner(Scanner):
    def __init__(self, project_root: Path) -> None:
        super().__init__(project_root)
        
    def scan(self, contexts: list[ScanContext]) -> list[Observation]:
        observation = []
        last_migration = None
        last_migration_name = None
        last_app = None
        for context in contexts:
            last_migration = context.get_state("django_migrations",".last_migration")
            if last_migration:
                break
        for migration_file in self._find_migrations():
            migration_name = migration_file.stem
            app_label = migration_file.parent.parent.name
            if last_migration:
                last_app , last_migration_name = last_migration.split(":",1,)
                if app_label == last_app:
                    if self._migration_num(migration_name) <= self._migration_num(last_migration_name):
                        continue
            observation.append(
                self._parse_migration(
                    migration_file
                )
            )
            
        return observation
        
    def _find_migrations(self) -> list[Path]:
        migration_files = []
        for path in self.project_root.rglob(
            "migrations/*.py"
        ):
            if self._is_ignored(path):
                continue
            migration_files.append(path)
        return migration_files
    
    def _is_ignored(self, path:Path) -> bool:
        IGNORED_DIRECTORIES = {
                    ".git",
                    ".venv",
                    "venv",
                    "env",
                    "node_modules",
                    "__pycache__",
                }
        return any(part in IGNORED_DIRECTORIES for part in path.parts)
    
    def _parse_migration(self,migration_file:Path) -> Observation:
        source = migration_file.read_text(encoding="utf-8")
        migration_name = migration_file.stem
        app_label = migration_file.parent.parent.name
        tree = ast.parse(source)
        dependencies = []
        parsed_operations = []
        
        for node in ast.walk(tree):
            if isinstance(node,ast.ClassDef):
                if node.name == "Migration":
                    migration_class = node
                    for statement in migration_class.body:
                        if isinstance(statement,ast.Assign):
                            target = statement.targets[0]
                            if isinstance(target, ast.Name):
                                if target.id == "dependencies":
                                    dependencies = ast.literal_eval(statement.value)
                                elif target.id == "operations":
                                    if not isinstance(
                                        statement.value,
                                        ast.List,
                                    ):
                                        continue

                                    parsed_operations.extend(
                                        self.get_operations(
                                            statement.value
                                        )
                                    )
                                    
        return Observation(
            source="django",
            type="migration",
            external_id=f"{app_label}:{migration_name}",
            timestamp=datetime.now(timezone.utc),
            data={
                "app": app_label,
                "name": migration_name,
                "dependencies": dependencies,
                "operations": parsed_operations,
            },
        )
        
    def get_operations(
        self,
        operations_node: ast.List,
    ) -> list[MigrationOperation]:

        operations = []

        for operation_node in operations_node.elts:

            if not isinstance(
                operation_node,
                ast.Call,
            ):
                continue

            if not isinstance(
                operation_node.func,
                ast.Attribute,
            ):
                continue

            operation_name = operation_node.func.attr

            model_name = None
            field_name = None

            for keyword in operation_node.keywords:

                if keyword.arg == "model_name":

                    model_name = ast.literal_eval(
                        keyword.value
                    )

                elif keyword.arg == "name":

                    field_name = ast.literal_eval(
                        keyword.value
                    )

            operations.append(
                MigrationOperation(
                    operation=operation_name,
                    details={
                        "model": model_name,
                        "field": field_name,
                    },
                ).to_dict()
            )

        return operations
    
    def _migration_num(self,migration_name:str) -> int:
        return int(migration_name.split("_",1)[0])