from factor_engine import FactorEngine
from factor_engine.engine import FactorEngine as EngineFactorEngine
from factor_engine.runtime import BatchFactorRuntime, RealtimeFactorRuntime, RuntimeConfig
from factor_engine.runtime.adapters import MarketTick


def test_factor_engine_root_import_matches_engine_import() -> None:
    assert FactorEngine is EngineFactorEngine


def test_runtime_public_imports_are_available() -> None:
    assert BatchFactorRuntime is not None
    assert RealtimeFactorRuntime is not None
    assert RuntimeConfig is not None


def test_market_tick_adapter_import_is_available() -> None:
    assert MarketTick is not None
