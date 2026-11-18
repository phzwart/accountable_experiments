"""Accountable measurement campaigns: interest and interpolation certificates on one footing."""
from .campaign import CampaignConfig, CampaignResult, Certificate, run_campaign, INTEREST, INTERP
from .criteria import AccuracyCriterion, peak_descriptors, estimate_window_noise
from .dataset import Dataset, Oracle, StoredOracle
from .policies import POLICIES, Guarantee, LevelData, Policy, PolicyDecision, make_policy, register
from .predictors import ScalarRoute, ScalarTarget, SpectrumRoute
from .scores import (DisagreementScore, LogisticInterestScore, LogisticInterpScore,
                     MeasuredSet, PredictedMaxScore, RandomScore, Score)

__version__ = "0.1.0"
