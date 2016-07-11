from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import class_mapper, RelationshipProperty, ColumnProperty
from pynYNAB.db.Entity import Entity
from six import iteritems


def knowledge_change(changed_entities):
    return sum(map(lambda v: len(v), [changed_entitity for dictkey, changed_entitity in changed_entities.items()]))


class ListOfEntities(RelationshipProperty):
    def __init__(self,*args,**kwargs):
        super(ListOfEntities,self).__init__(*args,cascade='all, delete-orphan',lazy='subquery',**kwargs)

    def update_from_changed_entities(self, instance, changed):
        from pynYNAB.db.db import session_scope
        currentlist=getattr(instance,self.key)
        otherclass = self.mapper.class_

        for elobj in changed:
            try:
                currentelement = next(obj for obj in currentlist if obj.id == elobj.id)
                if elobj.is_tombstone:
                    currentlist.remove(currentelement)
                else:
                    pass
            except StopIteration:
                elobj.parent = instance
                currentlist.append(elobj)



class Root(Entity):
    OPNAME = ''
    Fields = {}

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __init__(self, tracked=True, *args, **kwargs):
        self.knowledge = 0
        self.current_knowledge = 0
        self.device_knowledge_of_server = 0
        self.server_knowledge_of_device = 0

        from pynYNAB.db.track import init_event_tracking

        root_class = self.__class__
        self.tracked = tracked
        if self.tracked:
            from pynYNAB.db.track import add_trackers, add_set_tracker
            for key, list_property in self.listfields.items():
                child_class = list_property.mapper.class_

                init_event_tracking(list_property)
                add_trackers(self)
                for child_property in class_mapper(child_class).iterate_properties:
                    if isinstance(child_property, ColumnProperty):
                        add_set_tracker(self,root_class, list_property, child_property)

                originalsetattr = self.__setattr__

                def setattrnew(name,value):
                    print(('setattr',name,value))
                    originalsetattr(name,value)

                self.__setattr__ = setattrnew


        super(Root, self).__init__()


    @property
    def listfields(self):
        return {property.key: property for property in class_mapper(self.__class__).iterate_properties if
                isinstance(property, ListOfEntities)}

    def update_from_syncdata(self, sync_data):
        changed_entities = sync_data['changed_entities']
        for key in changed_entities:
            pass
        self.update_from_changed_entities(changed_entities)

        self.server_knowledge_of_device = sync_data['server_knowledge_of_device']
        # To handle cases where the local knwoledge got out of sync
        if self.server_knowledge_of_device > self.knowledge:
            self.knowledge = self.server_knowledge_of_device
        self.device_knowledge_of_server = sync_data['current_server_knowledge']

    def sync(self, connection):
        change, request_data = self.get_request_data()
        self.knowledge += change
        sync_data = connection.dorequest(request_data, self.OPNAME)
        self.update_from_syncdata(sync_data)


    def update_from_changed_entities(self, changed_entities):
        for key, prop in self.listfields.items():
            if key in changed_entities and changed_entities[key]:
                prop.update_from_changed_entities(self, changed_entities[key])


    def get_changed_entities(self):
        tracker = self.track
        returndict = {k:getattr(tracker,k) for k in self.listfields}
        return {k:v for k,v in iteritems(returndict) if v != []}


    def get_request_data(self):
        changed_entities = self.get_changed_entities()
        change = knowledge_change(changed_entities)
        return (change, {"starting_device_knowledge": self.knowledge,
                         "ending_device_knowledge": self.knowledge + change,
                         "device_knowledge_of_server": self.device_knowledge_of_server,
                         "changed_entities": changed_entities})
