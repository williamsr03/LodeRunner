class Event:

	_queue = {}
	_frame = 0

	@staticmethod
	def _enqueue(obj):
		target_frame = Event._frame + obj.frames
		if target_frame in Event._queue:
			Event._queue[target_frame].append(obj)
		else:
			Event._queue[target_frame] = [obj]

	@staticmethod
	def update():
		if Event._frame in Event._queue:
			for event in Event._queue[Event._frame]:
				new_event = event.execute()
				if new_event:
					Event._enqueue(new_event)
			del Event._queue[Event._frame]
		Event._frame += 1

	@staticmethod
	def delete(event):
		for event_list in Event._queue.values():
			if event in event_list:
				event_list.remove(event)

	def __init__(self, func, frames, args=[], recurring=None):
		self.func = func
		self.args = args
		self.frames = frames
		if recurring:
			recurring = self
		self.recurring = recurring
		Event._enqueue(self)

	def execute(self):
		self.func(*self.args)
		return self.recurring