from kgec_agent.policy.engine import ConfidencePolicy
from kgec_agent.schemas.models import CalibrationResult, Candidate, PolicyThresholds


THRESHOLDS = PolicyThresholds(
    accept_threshold=0.85,
    verify_threshold=0.5,
    margin_threshold=0.1,
)


def calibration(confidence, margin):
    return CalibrationResult(
        candidates=[
            Candidate(
                entity="a",
                label="A",
                entity_type="Thing",
                raw_score=1.0,
                calibrated_probability=confidence,
            ),
            Candidate(
                entity="b",
                label="B",
                entity_type="Thing",
                raw_score=0.5,
                calibrated_probability=confidence - margin,
            ),
        ],
        confidence=confidence,
        margin=margin,
        reason_codes=[],
    )


def test_confidence_and_margin_boundaries():
    policy = ConfidencePolicy()
    assert policy.apply_confidence_policy(calibration(0.85, 0.1), THRESHOLDS).initial_route == "auto_accept"
    assert policy.apply_confidence_policy(calibration(0.849, 0.1), THRESHOLDS).initial_route == "verify"
    assert policy.apply_confidence_policy(calibration(0.5, 0.2), THRESHOLDS).initial_route == "verify"
    assert policy.apply_confidence_policy(calibration(0.499, 0.2), THRESHOLDS).initial_route == "abstain"
    assert policy.apply_confidence_policy(calibration(0.9, 0.099), THRESHOLDS).initial_route == "verify"
