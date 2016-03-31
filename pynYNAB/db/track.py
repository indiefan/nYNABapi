from sqlalchemy import event

from pynYNAB.config import get_logger


class ModificationTracker(object):
    pass


class Tracker(object):
    def __init__(self, cls, otherclass, prop):
        self.trackedtype = cls
        self.changed = []
        self.otherclass = otherclass
        self.logger = get_logger()
        event.listens_for(prop, 'append')(self.track_append)
        event.listens_for(prop, 'dispose_collection')(self.track_dispose)
        event.listens_for(prop, 'remove')(self.track_remove)

    def reset(self):
        self.changed = []

    def track_append(self, target, value, initiator):
        self.logger.debug("track_append %s" % value)
        if not isinstance(value, self.otherclass):
            print('Tried to append a %s, expected a %s ' % (self.otherclass, value.__class__))
            raise ValueError()
        self.changed.append(value)

    def track_remove(self, target, value, initiator):
        self.logger.debug("track_remove %s" % value)
        valuecopy = value.copy()
        valuecopy.is_tombstone = True
        self.track_append(target, valuecopy, initiator)

    def track_set(self, target, value, oldvalue, initiator):
        self.logger.debug("track_set %s %s => %s" % (initiator.key, oldvalue, value))
        if initiator.key != 'is_tombstone' and target.initialized:
            self.changed.append(target)

    def track_dispose(self, target, value, initiator):
        self.logger.debug("track_dispose %s" % value)
        l = getattr(target, initiator.attr.key)
        l.track = self

    def add_set_tracker(self, otherclass, prop2):
        event.listens_for(prop2, 'set')(self.track_set)

    def track_init(self, target, args, kwarg):
        self.logger.debug('track_init %s' % target)

    def track_load(self, target, args, kwarg):
        self.logger.debug('track_load')

    def add_init_tracker(self, otherclass):
        event.listens_for(otherclass, 'init')(self.track_init)
        event.listens_for(otherclass, 'load')(self.track_load)
