from xbox6 import calculate_trigger_haptics

def test_trigger_calc():
    # Giả lập tín hiệu âm thanh có tiếng súng nổ mạnh bên phải
    bands = {
        "punch_r": 0.8,
        "highmid_r": 0.9,
        "lowmid_l": 0.1,
        "sub_l": 0.05
    }
    lt, rt = calculate_trigger_haptics(bands, mode="adaptive_gun_brake", gain_l=0.7, gain_r=0.85, threshold=0.04)
    assert rt > 0.5  # RT phải kích hoạt mạnh theo tiếng súng
    assert lt < 0.2  # LT giữ ở mức thấp
    
    # Giả lập tiếng rền phanh gấp bên trái
    bands_brake = {
        "punch_r": 0.05,
        "highmid_r": 0.05,
        "lowmid_l": 0.8,
        "sub_l": 0.7
    }
    lt_b, rt_b = calculate_trigger_haptics(bands_brake, mode="adaptive_gun_brake", gain_l=0.7, gain_r=0.85, threshold=0.04)
    assert lt_b > 0.4
    assert rt_b < 0.1

    # Chế độ directional_stereo
    bands_pan = {
        "punch_r": 0.6,
        "highmid_r": 0.6,
        "lowmid_l": 0.6,
        "sub_l": 0.6,
        "stereo_pan": 0.8
    }
    lt_p, rt_p = calculate_trigger_haptics(bands_pan, mode="directional_stereo", gain_l=0.7, gain_r=0.85, threshold=0.04)
    assert rt_p > lt_p

if __name__ == "__main__":
    test_trigger_calc()
    print("DSP TRIGGER CALC TEST PASSED")
