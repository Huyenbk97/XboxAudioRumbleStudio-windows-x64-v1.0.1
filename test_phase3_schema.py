from xbox6 import SharedVibrationParams

def test_phase3_schema():
    p = SharedVibrationParams()
    assert hasattr(p, "trigger_haptics_enabled")
    assert hasattr(p, "trigger_left_gain")
    assert hasattr(p, "trigger_right_gain")
    assert hasattr(p, "trigger_mode")
    assert hasattr(p, "trigger_threshold")
    
    assert p.trigger_haptics_enabled is True
    assert p.trigger_left_gain == 0.70
    assert p.trigger_right_gain == 0.85
    assert p.trigger_mode == "adaptive_gun_brake"
    assert p.trigger_threshold == 0.04
    
    snap = p.snapshot()
    assert "trigger_haptics_enabled" in snap
    assert "trigger_left_gain" in snap
    assert "trigger_right_gain" in snap
    assert "trigger_mode" in snap

if __name__ == "__main__":
    test_phase3_schema()
    print("PHASE 3 SCHEMA TEST PASSED")
