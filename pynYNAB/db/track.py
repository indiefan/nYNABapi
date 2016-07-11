import functools

from sqlalchemy import event

from pynYNAB.config import echo
from pynYNAB.db.db import session_scope, Catalog


def init_event_tracking(list_property):
    child_class = list_property.mapper.class_

    if not event.contains(list_property, 'append', track_append):
        event.listens_for(list_property, 'append')(track_append)
    if not event.contains(list_property, 'remove', track_remove):
        event.listens_for(list_property, 'remove')(track_remove)
    if not event.contains(list_property, 'dispose_collection', track_dispose):
        event.listens_for(list_property, 'dispose_collection')(track_dispose)


def add_trackers(root_instance):
    root_class = root_instance.__class__
    with session_scope() as session:
        tracker = root_class(tracked=False)
        root_instance.track_id = tracker.id
        root_instance.track = tracker
        session.add(tracker)


def reset(self):
    if echo:
        print("track_reset")


def track_append(root_instance, value, initiator):
    if hasattr(root_instance,'tracked') and root_instance.tracked:
        if echo:
            print("track_append %s,%s,%s" % (root_instance, value, initiator))

        child_class = initiator.parent_token.mapper.class_

        tracker = root_instance.track
        tracker_list = getattr(tracker, initiator.key)
        if id(value) not in [id(e) for e in tracker_list]:
            if not isinstance(value,child_class):
                raise ValueError('tried adding a '+str(value.__class__) + ' to a list of '+str(child_class))

            print('Adding ' + str(id(value)) + ' in')
            print([id(e) for e in tracker_list])

            tracker_list.append(value)
            setattr(tracker, initiator.key, tracker_list)


def track_remove(root_instance, value, initiator):
    if hasattr(root_instance,'tracked') and root_instance.tracked:
        if echo:
            print("track_remove %s,%s,%s" % (root_instance, value, initiator))

        value.is_tombstone = True
        # the rest (adding the value with is_tombstone true to the tracke_list) is handled by track_set


def track_set(target, value, oldvalue, initiator, root_class, root_instance, list_property):
    if hasattr(root_instance,'tracked') and root_instance.tracked:
        if echo:
            print("track_set %s %s => %s" % (initiator.key, oldvalue, value))
        tracker = root_instance.track
        tracker_list = getattr(tracker, list_property.key)
        if id(target) not in [id(e) for e in tracker_list]:
            print('Adding '+str(id(target))+' in')
            print([id(e) for e in tracker_list])

            tracker_list.append(target)


def track_dispose(root_instance, value, initiator):
    if hasattr(root_instance, 'tracked') and root_instance.tracked:
        if echo:
            print("track_dispose %s" % value)
        tracker = root_instance.track


def add_set_tracker(root_instance, root_class, list_property, child_non_list_property):
    event.listens_for(child_non_list_property, 'set')(
        functools.partial(track_set, root_class=root_class, root_instance=root_instance, list_property=list_property))


def track_load(t1, t2):
    if echo:
        print('track_load')


def reset_track(root_object):
    for k in root_object.listfields:
        setattr(root_object.track, k, [])
    pass
