"""Deterministic cross-demonstration reconciliation."""

from collections import Counter, defaultdict

from app.models.learning import ReconciliationRequest, ReconciliationResult
from app.models.procedure import Procedure, ProcedureStep


class ReconcilerAgent:
    """Surface contradictions, agreement, and uncertainty across sources."""

    def reconcile(self, request: ReconciliationRequest) -> ReconciliationResult:
        agreements: list[str] = []
        conflicts: list[str] = []
        uncertainties: list[str] = []
        consensus_steps: list[ProcedureStep] = []
        source_count = len(request.sources)
        maximum_steps = max(len(item.procedure.steps) for item in request.sources)

        for index in range(maximum_steps):
            observed = [
                (source.source_id, source.procedure.steps[index])
                for source in request.sources
                if index < len(source.procedure.steps)
            ]
            groups: dict[str, list[tuple[str, ProcedureStep]]] = defaultdict(list)
            for source_id, step in observed:
                groups[self._normalize(step.action)].append((source_id, step))
            winner = max(groups.values(), key=lambda items: len(items))
            representative = winner[0][1]
            support = len(winner)
            if len(groups) == 1 and len(observed) == source_count:
                agreements.append(f"Step {index + 1} is supported by every source.")
            elif len(groups) > 1:
                variants = sorted({item.action for _, item in observed})
                conflicts.append(
                    f"Step {index + 1} has competing actions: {' | '.join(variants)}"
                )
            if len(observed) < source_count:
                uncertainties.append(
                    f"Step {index + 1} appears in {len(observed)} of {source_count} sources."
                )
            consensus_steps.append(
                representative.model_copy(
                    update={
                        "step": index + 1,
                        "evidence": (
                            f"Supported by {support}/{source_count} approved sources: "
                            + ", ".join(source_id for source_id, _ in winner)
                        ),
                    }
                )
            )

        rules, rule_uncertainties = self._consensus_rules(request, source_count)
        uncertainties.extend(rule_uncertainties)
        confidence = round(
            sum(1 for agreement in agreements if agreement.startswith("Step"))
            / max(maximum_steps, 1),
            4,
        )
        first = request.sources[0].procedure
        procedure = Procedure(
            task=request.task,
            objective=first.objective,
            inputs=first.inputs,
            outputs=first.outputs,
            steps=consensus_steps,
            rules=rules,
            conditions=first.conditions,
            exceptions=first.exceptions,
            examples=[source.source_id for source in request.sources],
        )
        return ReconciliationResult(
            procedure=procedure,
            source_count=source_count,
            agreements=agreements,
            conflicts=conflicts,
            uncertainties=uncertainties,
            confidence=confidence,
            ready_for_practice=not conflicts and confidence == 1.0,
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.casefold().split()).rstrip(".")

    def _consensus_rules(
        self,
        request: ReconciliationRequest,
        source_count: int,
    ) -> tuple[list[str], list[str]]:
        variants: dict[str, str] = {}
        counts: Counter[str] = Counter()
        for source in request.sources:
            for rule in {self._normalize(item) for item in source.procedure.rules}:
                counts[rule] += 1
            for rule in source.procedure.rules:
                variants.setdefault(self._normalize(rule), rule)
        consensus = [variants[key] for key, count in counts.items() if count == source_count]
        uncertain = [
            f"Rule needs review ({count}/{source_count} sources): {variants[key]}"
            for key, count in counts.items()
            if count < source_count
        ]
        return consensus, uncertain
