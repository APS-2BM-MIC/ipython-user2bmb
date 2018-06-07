from bluesky.suspenders import SuspendBoolHigh
from functools import partial


class PauseInterupt(SuspendBoolHigh):
    def __call__(self, value, **kwargs):
        """Make the class callable so that we can
        pass it off to the ophyd callback stack.

        This expects the massive blob that comes from ophyd
        """
        with self._lock:
            if self._should_suspend(value):
                self._tripped = True
                loop = self.RE._loop
                # this does dirty things with internal state
                if (self.RE is not None):
                    cb = partial(
                        self.RE.request_pause, defer=False)
                    if self.RE.state.is_running:
                        loop.call_soon_threadsafe(cb)
                        # this a hack until we get refactor pushed upstream
                        self._SuspenderBase__make_event()
                # super hack but gets the behavior Pete expects
                self._ev.set(0)
            elif self._should_resume(value):
                self._tripped = False
                # this a hack until we get refactor pushed upstream
                self._SuspenderBase__set_event()


interupter = PauseInterupt(mona.stop_acquisition)
RE.install_suspender(interupter)
