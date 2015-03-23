import win32api, win32process, thread
from time import sleep
class test:
	"""docstring for test"""
	def __init__(self):
		tid=win32api.GetCurrentThreadId()
		print tid
		sleep(3)
		self.tid=win32api.GetCurrentThread()
		print repr(self.tid)
		thread.start_new_thread(self.run,())
		sleep(5)
		
		win32process.SuspendThread(self.tid)
		print 'end'
	def run(self):
		sleep(1)
		win32process.SuspendThread(self.tid)
		print 'sleep 5s.'
		sleep(5)
		win32process.ResumeThread(self.tid)
		print 'resume'
t=test()
