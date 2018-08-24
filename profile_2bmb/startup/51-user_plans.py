
# RE(my_series(-7.7, -5, 1.4, acquire_time=0.1), ant="Pr03_006", common_name="foaming ant", status="previously used at 32-ID")

# pixel = 0.00164 mm        ( 4x lens)
# vertical frame = 1200 pixels
# recommend shift vertically by 3/4 frame
# 1.476 = 0.00164 * 1200 * 3/4

def my_series(start, stop, step, acquire_time=0.02):
    positions = np.arange(start, stop, step)
    # for example, 
    #    In [28]: a = np.arange(-7.5, 0, 1.5)
    #    Out[28]: array([-7.5, -6. , -4.5, -3. , -1.5,  0. ])
    
    for pos_y in positions:
        print("moving sample to y =", pos_y)
        yield from bps.mv(tomo_stage.y, pos_y)
        yield from user_tomo_scan(acquire_time=acquire_time, samOutDist=-5)
