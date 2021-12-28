import ctypes
import threading

def killThread(thread):
	if not thread:
		return True

	res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), ctypes.py_object(SystemExit))
	if res > 1:
		ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), 0)
		print('Exception raise failure')
		return False

	return True