print(__file__)

# Bluesky plans (scans)

def _plan_edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,clShutter=1, pso=None, rotStage=None):
    pso = pso or pso1
    rotStage = rotStage or bm82
    det = pco_edge

    yield from abs_set(shutter, "open", wait=True)
    yield from abs_set(det.cam.frame_type, "Normal")
    yield from mv(samStage, samInPos)
    yield from mv(rotStage.velocity, 50.0)
    yield from mv(rotStage, 0.00)
    
    # back off to the ramp-up point
    yield from abs_set(pso, "taxi", wait=True)

    # run the fly scan
    yield from abs_set(pso, "fly", wait=True)

    if pso.pso_fly.value == 0 & clShutter == 1:               
        yield from abs_set(shutter, "close", wait=True)

    yield from abs_set(rotStage.set_use_switch, "Set", wait=True)
    # ensure `.RVAL` changes (not `.OFF`)
    foff_previous = rotStage.offset_freeze_switch.value
    yield from abs_set(rotStage.offset_freeze_switch, "Fixed", wait=True)
    yield from abs_set(rotStage.user_setpoint, 1.0*(rotStage.position%360.0), wait=True)
    yield from abs_set(rotStage.offset_freeze_switch, foff_previous, wait=True)
    yield from abs_set(rotStage.set_use_switch, "Use", wait=True)

    yield from mv(rotStage.velocity, 50.0)
    yield from sleep(1)
    yield from mv(rotStage, 0.00)
    # shutter.close()
    while (det.hdf1.num_captured.value != numProjPerSweep):    
        yield from sleep(1)        

# FIXME:  Following are just notes from a phone conversation 2018-02-01 with Dan Allan


def bluesky_plan_circa_2015():
    """This syntax was refactored into `abs_set()`"""
    yield Msg("set", pso1, "Taxi")




# The plan yields a message.
# These are all the same.


def example_plan1():
    yield from abs_set(pso1, "Taxi", group="A")
    yield from wait("A")
    yield from abs_set(pso1, "Fly", group="B")
    yield from wait("B")


def example_plan2():
    yield from abs_set(pso1, "Taxi", wait=True)
    yield from abs_set(pso1, "Fly", wait=True)


def example_plan3():
    yield from mv(pso1, "Taxi")  # waits by default
    yield from mv(pso1, "Fly")

"""
The idea with mv is this:
`mv(theta, 0, phi, 1, alpha, 3)`  # in parallel -- wait until all are done

Note:

===========================   ======================================
interactive (blocking)        re-write for BlueSky plan()
===========================   ======================================
some.device.put("config")     yield from mv(some.device, "config")
motor.move(52)                yield from mv(motor, 52)
motor.velocity.put(5)         yield from mv(motor.velocity, 5)
===========================   ======================================

By using `yield from`, BlueSky is able to handle and recover from 
interruptions such as the user pressing `^C`.  Also, the RE can 
differentiate if the plan is being run in simulation and not actually
change the underlying EPICS PV.


# RunEngine iterates through plan, receives Msg("set", pso1, "Taxi")


# RunEngine looks at RunEngine._command_registry and finds that ``set`` is mapped to RunEngine._set. It calls RunEngine._set(Msg("set", pso1, "Taxi")).
# RunEngine._set calls pso1.set(``taxi``) and gets back a status object.
# The RE stashes that status object in a local cache. Perhaps later the plan will ask the RunEngine to wait on the status object via Msg("wait", ...)


Additionally, RunEngine._set is doing other good stuff for us, like keeping track of the fact that this device is in motion.




Note: Remember to search all plans for ``time.sleep(X)`` and replace with ``yield from sleep(X)`` (except in those situations where the call to ``time.sleep()`` is executing in a thread).


All these 'plan stubs' (plans that don't generate runs like count or scan do) are in bluesky.plans pre-0.11.0 and bluesky.plan_stubs in v0.11.0+.
"""
