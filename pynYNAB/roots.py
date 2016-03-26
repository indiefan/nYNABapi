from sqlalchemy.orm import class_mapper, RelationshipProperty, ColumnProperty

from pynYNAB.Entity import obj_from_dict
from pynYNAB.db.Entity import Entity
from pynYNAB.db.track import Tracker


def knowledge_change(changed_entities):
    return sum(map(lambda v: len(v), [changed_entitity for dictkey, changed_entitity in changed_entities.items()]))


class ListOfEntities(RelationshipProperty):
    pass


class Root(Entity):
    OPNAME = ''
    Fields = {}

    def __init__(self, *args, **kwargs):
        self.knowledge = 0
        self.current_knowledge = 0
        self.device_knowledge_of_server = 0
        self.server_knowledge_of_device = 0

        cls = self.__class__
        for key, prop in self.listfields.items():
            otherclass = prop.mapper.class_
            track = Tracker(cls, otherclass, prop)
            setattr(getattr(self, prop.key), 'track', track)

            for prop2 in class_mapper(otherclass).iterate_properties:
                if isinstance(prop2, ColumnProperty):
                    track.add_set_tracker(otherclass, prop2)
            track.add_init_tracker(otherclass)

        super(Root, self).__init__()

    @property
    def listfields(self):
        return {prop.key: prop for prop in class_mapper(self.__class__).iterate_properties if
                isinstance(prop, ListOfEntities)}

    def sync(self, connection):
        change, request_data = self.get_request_data()
        syncData = connection.dorequest(request_data, self.OPNAME)

        self.knowledge += change
        changed_entities = {}
        for name, value in syncData['changed_entities'].items():
            if isinstance(value, list):
                for entityDict in value:
                    if not entityDict.get('is_tombstone'):
                        newdict = self.listfields[name].mapper.class_.convert_out(entityDict)
                        obj = obj_from_dict(self.listfields[name].mapper.class_, newdict)
                        try:
                            changed_entities[name].append(obj)
                        except KeyError:
                            changed_entities[name] = [obj]
            else:
                changed_entities[name] = value
        self.update_from_changed_entities(changed_entities)
        for key, prop in self.listfields.items():
            getattr(self, prop.key).track.reset()

        self.server_knowledge_of_device = syncData['server_knowledge_of_device']
        # To handle cases where the local knwoledge got out of sync
        if self.server_knowledge_of_device > self.knowledge:
            self.knowledge = self.server_knowledge_of_device
        self.device_knowledge_of_server = syncData['current_server_knowledge']

    def update_from_changed_entities(self, changed_entities):
        for key, prop in self.listfields.items():
            try:
                current = {e.id: e for e in getattr(self, prop.key)}

                changed = changed_entities[prop.key] if changed_entities[prop.key] else []
                for el in changed:
                    if el.id in current.keys():
                        if el.is_tombstone:
                            del current[el.id]
                        else:
                            current[el.id] = el
                    else:
                        if not el.is_tombstone:
                            current[el.id] = el
                setattr(self, prop.key, list(current.values()))
            except KeyError:
                pass

    def get_changed_entities(self):
        changed = {}
        for prop in class_mapper(self.__class__).iterate_properties:
            if isinstance(prop, ListOfEntities):
                propchanged = getattr(self, prop.key).track.changed
                if propchanged:
                    changed[prop.key] = propchanged

        return changed

    def get_request_data(self):
        changed_entities = self.get_changed_entities()
        change = knowledge_change(changed_entities)
        return (change, {"starting_device_knowledge": self.knowledge,
                         "ending_device_knowledge": self.knowledge + change,
                         "device_knowledge_of_server": self.device_knowledge_of_server,
                         "changed_entities": changed_entities})
