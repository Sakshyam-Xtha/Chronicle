from chronicle.analysis.analyzers.base import BaseAnalyzer
from chronicle.storage.models import Findings
from chronicle.storage.observations import Observation
from chronicle.analysis.context import AnalysisContext

class DjangoMigrationAnalyzer(BaseAnalyzer):

    def analyze(
        self,
        context: AnalysisContext
    ) -> list[Findings]:

        findings = []

        for observation in context.observations:

            if observation.source != "django":
                continue

            if observation.type != "migration":
                continue

            operations = observation.data.get(
                "operations",
                []
            )

            for operation in operations:

                operation_name = operation.get(
                    "operation"
                )

                if operation_name == "RemoveField":

                    findings.append(
                        Findings(
                            analyzer="django-migrations",
                            severity="warning",
                            title="Field removed",
                            message=(
                                "A database field is being "
                                "removed by this migration."
                            ),
                            observation_id= observation.id, #type: ignore
                            data=operation,
                        )
                    )

        return findings