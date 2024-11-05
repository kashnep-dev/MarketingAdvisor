import os
import time
from logging.handlers import TimedRotatingFileHandler
from common.logging.logger import LOGGER


class SafeRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backup_count=0, encoding=None, delay=False, utc=False):
        super().__init__(filename, when, interval, backup_count, encoding, delay, utc)

        """
        멀티 프로세스로 실행될 때 doRollover 시점을 분산함으로써 로그 파일을 rolling할 때 파일 경합 가능성을 줄임
        """
        current_time = int(time.time())
        print("pid : " + str(os.getpid()) + "/ current_time : " + str(current_time)+">= self.rolloverAt : " + str(self.rolloverAt) + " : " + str(current_time >= self.rolloverAt))
        if current_time >= self.rolloverAt:
            self.doRollover()

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        current_time = int(time.time())
        dst_now = time.localtime(current_time)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            time_tuple = time.gmtime(t)
        else:
            time_tuple = time.localtime(t)
            dst_then = time_tuple[-1]
            if dst_now != dst_then:
                if dst_now:
                    addend = 3600
                else:
                    addend = -3600
                time_tuple = time.localtime(t + addend)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, time_tuple)

        # Issue 18948: A file may not have been created if delay is True.
        if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.mode = "a"
            self.stream = self._open()
        new_rollover_at = self.computeRollover(current_time)
        while new_rollover_at <= current_time:
            new_rollover_at = new_rollover_at + self.interval

        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == "MIDNIGHT" or self.when.startswith("W")) and not self.utc:
            dst_at_rollover = time.localtime(new_rollover_at)[-1]
            if dst_now != dst_at_rollover:
                if not dst_now:
                    # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:
                    # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                new_rollover_at += addend
        self.rolloverAt = new_rollover_at
