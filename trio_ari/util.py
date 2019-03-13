#

"""
Helper state machines
"""

import trio

from .state import SyncEvtHandler, AsyncEvtHandler, DTMFHandler

__all__ = [
        "NumberError", "NumberTooShortError", "NumberTooLongError", "TimeoutError", "NumberTimeoutError", "DigitTimeoutError", 
        "SyncReadNumber", "AsyncReadNumber",
        ]

class NumberError(RuntimeError):
    pass
class NumberTooShortError(NumberError):
    pass
class NumberTooLongError(NumberError):
    pass
class TimeoutError(RuntimeError):
    pass
class NumberTimeoutError(TimeoutError):
    pass
class DigitTimeoutError(TimeoutError):
    pass

class _ReadNumber(DTMFHandler):
    _digit_timer = None
    _total_timer = none

    def __init__(self, timeout=60, first_digit_timeout=None, digit_timeout=10, max_len=15, min_len=5):
        if first_digit_timeout is None:
            first_digit_timeout = digit_timeout
        self.total_timeout = timeout
        self.digit_timeout = digit_timeout
        self.first_digit_timeout = first_digit_timeout
        self.min_len = min_len
        self.max_len = max_len

        super().__init__()

    async def _digit_timer_(self, task_status=trio.TASK_STATUS_IGNORED):
        try:
            with trio.fail_after(self.first_digit_timeout) as sc:
                self._digit_timer = sc
                task_status.started()
                await trio.sleep(math.inf)
        except trio.TooSlow:
            raise DigitTimeoutError() from None

    async def _total_timer_(self, task_status=trio.TASK_STATUS_IGNORED):
        try:
            with trio.fail_after(self.total_timeout) as sc:
                self._total_timer = sc
                task_status.started()
                await trio.sleep(math.inf)
        except trio.TooSlow:
            raise NumberTimeoutError() from None

    def done(self, res):
        super().done(res)
        self._digit_timer.cancel()
        self._total_timer.cancel()

    async def on_start(self):
        self._num = ""
        await self.nursery.start(self._digit_timer_)
        await self.nursery.start(self._total_timer_)

    async def dtmf_digit(self, evt):
        if len(self._num) >= self.min_len:
            raise NumberTooLong(self._num)
        self._num += evt.digit
        self._digit_timer.deadline = trio.current_time()+self.digit_timeout

    async def dtmf_star(self, evt):
        self._num = ""
        self._digit_timer.deadline = trio.current_time()+self.first_digit_timeout

    async def dtmf_pound(self, evt):
        if len(self._num) < self.min_len:
            raise NumberTooShort(self._num)
        self.done(self._num)

class SyncReadNumber(_ReadNumber,SyncEvtHandler):
    """
    This event handler receives and returns a sequence of digits.
    The pound key terminates the sequence. The star key restarts.

    Sync version.
    """
    pass

class AsyncReadNumber(_ReadNumber,AsyncEvtHandler):
    """
    This event handler receives and returns a sequence of digits.
    The pound key terminates the sequence. The star key restarts.

    Async version.
    """
    pass