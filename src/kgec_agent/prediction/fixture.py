"""Small JSON-backed prediction service for deterministic public replay."""

from kgec_agent.schemas.models import PredictionResult, ScenarioFixture, StructuredQuery


class FixturePredictionService:
    def predict_link(self, query: StructuredQuery, fixture: ScenarioFixture) -> PredictionResult:
        if query != fixture.llm.query:
            raise ValueError("structured query does not match the reviewed scenario fixture")
        return PredictionResult(
            query=query,
            candidates=fixture.candidates,
            reason_codes=["PREDICTION_FROM_REVIEWED_FIXTURE"],
        )
