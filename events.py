from typing import Callable, Dict


class Event(object):
    _event_name: str
    _observers: Dict[object, Callable]

    def __init__(self, event_name):
        self._event_name = event_name
        self._observers = dict()

    def add_observer(self, observer: object, callback: Callable):
        if observer in self._observers.keys():
            raise ValueError()
        self._observers[observer] = callback

    def remove_observer(self, observer: object):
        # raises KeyError if observer not in self._observers
        del self._observers[observer]

    def publish(self, **kwargs):
        for callback in self._observers.values():
            callback(**kwargs)


new_tracked_player_event = Event("New Tracked Player")
new_record_event = Event("New Record")
improved_record_event = Event("Improved Record")
update_session_start_event = Event("Update Session Start")
update_session_end_event = Event("Update Session End")
