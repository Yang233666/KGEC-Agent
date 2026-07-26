"""Fixture calibration service with no numerical-framework dependency."""

from kgec_agent.schemas.models import CalibrationResult, PredictionResult


class CalibrationService:
    def calibrate_prediction(self, prediction: PredictionResult) -> CalibrationResult:
        ordered = sorted(prediction.candidates, key=lambda item: item.calibrated_probability, reverse=True)
        confidence = ordered[0].calibrated_probability
        margin = confidence - ordered[1].calibrated_probability
        return CalibrationResult(
            candidates=ordered,
            confidence=confidence,
            margin=margin,
            reason_codes=["CALIBRATION_FROM_REVIEWED_FIXTURE", "TOP1_MARGIN_COMPUTED"],
        )
