"""Shadow-only book-faithful evidence model.

This package is intentionally excluded from production resolver and dashboard paths.
"""

from business_cycle.shadow_model.runner import run_shadow_evidence_model

__all__ = ["run_shadow_evidence_model"]

