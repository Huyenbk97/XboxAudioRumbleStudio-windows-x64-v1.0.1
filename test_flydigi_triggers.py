from xbox6 import FlydigiApexController, FlydigiController

def test_flydigi_triggers():
    assert FlydigiController is FlydigiApexController
    fly = FlydigiController()
    assert hasattr(fly, "set_triggers")
    
    # Thử nghiệm gửi lệnh rung cò: không được crash, trả về boolean
    res = fly.set_triggers(0.5, 0.8)
    assert isinstance(res, bool)
    
    res_zero = fly.set_triggers(0.0, 0.0)
    assert isinstance(res_zero, bool)
    
    fly.close()

if __name__ == "__main__":
    test_flydigi_triggers()
    print("FLYDIGI TRIGGER TEST PASSED")
