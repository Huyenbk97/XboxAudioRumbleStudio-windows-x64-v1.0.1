from xbox6 import Unified4ChannelDispatcher

def test_dispatcher():
    disp = Unified4ChannelDispatcher()
    assert hasattr(disp, "set_vibration_4ch")
    assert hasattr(disp, "stop_all")
    
    # Thử nghiệm gửi lệnh rung 4 kênh: không được crash, trả về boolean
    res = disp.set_vibration_4ch(0, 0.0, 0.0, 0.0, 0.0)
    assert isinstance(res, bool)
    
    # Thử nghiệm các giá trị biên (0.0 đến 1.0)
    res_high = disp.set_vibration_4ch(0, 1.0, 0.5, 0.7, 0.8)
    assert isinstance(res_high, bool)
    
    disp.stop_all()

if __name__ == "__main__":
    test_dispatcher()
    print("DISPATCHER TEST PASSED")
