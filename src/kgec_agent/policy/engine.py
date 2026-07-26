"""Deterministic confidence-and-margin routing policy."""

from kgec_agent.schemas.models import CalibrationResult, PolicyResult, PolicyThresholds


class ConfidencePolicy:
    def apply_confidence_policy(
        self,
        calibration: CalibrationResult,
        thresholds: PolicyThresholds,
    ) -> PolicyResult:
        if (
            calibration.confidence >= thresholds.accept_threshold
            and calibration.margin >= thresholds.margin_threshold
        ):
            route = "auto_accept"
            reasons = ["CONFIDENCE_ACCEPT_THRESHOLD_MET", "MARGIN_THRESHOLD_MET"]
        elif calibration.confidence >= thresholds.verify_threshold:
            route = "verify"
            reasons = ["CONFIDENCE_VERIFY_REGION"]
            if calibration.margin < thresholds.margin_threshold:
                reasons.append("MARGIN_BELOW_ACCEPTANCE_THRESHOLD")
        else:
            route = "abstain"
            reasons = ["CONFIDENCE_BELOW_VERIFY_THRESHOLD"]
        return PolicyResult(
            initial_route=route,
            confidence=calibration.confidence,
            margin=calibration.margin,
            thresholds=thresholds,
            reason_codes=reasons,
        )
