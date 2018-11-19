print(__file__)

"""custom ophyd support for pausing a running plan"""

from bluesky.suspenders import SuspenderBase


class SuspendAndLatchStringMismatched(SuspenderBase):
    """
    Bluesky suspender
    
    Do not resume when the monitored string deviates from the expected.
    """
    # see: http://nsls-ii.github.io/bluesky/_modules/bluesky/suspenders.html#SuspendCeil
    
    def __init__(self, signal, *, 
        match_string=None, 
        sleep=0, pre_plan=None, post_plan=None, tripped_message=''):
        
        self.match_string = match_string or signal.value
        super().__init__(signal, 
            sleep=sleep, 
            pre_plan=pre_plan, 
            post_plan=post_plan, 
            tripped_message=tripped_message,
            **kwargs)

    def _should_suspend(self, value):
        return value != self.match_string

    def _should_resume(self, value):
        # return value == self.match_string
        return False    # latching

    def _get_justification(self):
        if not self.tripped:
            return ''

        just = 'Signal {} is not "{}"'.format(self._sig.name, self.match_string)
        return ': '.join(s for s in (just, self._tripped_message)
                         if s)
