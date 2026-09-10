"""Dependency-free calibration interface for the Vercel runtime."""
from dataclasses import dataclass
from typing import Any
@dataclass(frozen=True)
class CalibrationResult:
    calibrated_score: float
    model_used: bool=False
    model_version: str='calibration-disabled-v1'
    reason: str='Runtime calibration is disabled in the Vercel lightweight build.'
    @property
    def score(self): return self.calibrated_score
class ScoreCalibrator:
    def __init__(self, model_version='calibration-disabled-v1'):
        self.model_version=model_version; self._model=None
    @property
    def is_trained(self): return False
    def fit(self,*args,**kwargs): return self
    def predict(self, features: Any, score: float):
        return CalibrationResult(float(score),False,self.model_version)
    def save(self,path): raise RuntimeError('Calibration training is not part of the Vercel runtime.')
    @classmethod
    def load(cls,path): return cls()
# Backwards-compatible alias
CalibrationModel=ScoreCalibrator
