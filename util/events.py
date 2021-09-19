from enum import auto, Enum


class Eventos(Enum):
    LANCAMENTO_CREATED = auto()
    LANCAMENTO_WINDOW_CLOSED = auto()


subscribers = dict()


def subscribe(event_type: Eventos, fn1, ref1):
    if event_type not in subscribers:
        subscribers[event_type] = []
    subscribers[event_type].append({"fn": fn1, "ref": ref1})


def post_event(event_type: Eventos, data):
    if event_type not in subscribers:
        return
    for details in subscribers[event_type]:
        details["fn"](data)


def unsubscribe_refs(ref):
    for subs in subscribers:
        for details in subscribers[subs]:
            if details["ref"] == ref:
                subscribers[subs].remove(details)
