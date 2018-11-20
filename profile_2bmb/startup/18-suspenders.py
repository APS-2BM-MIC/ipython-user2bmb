print(__file__)

"""custom ophyd support for pausing a running plan"""

from bluesky.suspenders import SuspenderBase


class SuspendAndLatchWhenChanged(SuspenderBase):
    """
    Bluesky suspender
    
    Do not resume when the monitored value deviates from the expected.
    """
    # see: http://nsls-ii.github.io/bluesky/_modules/bluesky/suspenders.html#SuspendCeil
    
    def __init__(self, signal, *, 
                expected_value=None, 
                sleep=0, pre_plan=None, post_plan=None, tripped_message='',
                **kwargs):
        
        self.expected_value = expected_value or signal.value
        super().__init__(signal, 
            sleep=sleep, 
            pre_plan=pre_plan, 
            post_plan=post_plan, 
            tripped_message=tripped_message,
            **kwargs)

    def _should_suspend(self, value):
        return value != self.expected_value

    def _should_resume(self, value):
        # return value == self.expected_value
        return False    # latching

    def _get_justification(self):
        if not self.tripped:
            return ''

        just = 'Signal {}, got "{}", expected "{}"'.format(
            self._sig.name,
            self._sig.get(),
            self.expected_value)
        return ': '.join(s for s in (just, self._tripped_message)
                         if s)
