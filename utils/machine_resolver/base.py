import abc

__all__ = ['MachineResolverException', 'Machine', 'MachineResolver']


class MachineResolverException(Exception):
    pass


class Machine(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_userdata(self):
        pass

    @abc.abstractmethod
    def get_instance_id(self):
        pass

    @abc.abstractmethod
    def get_public_ipv4(self):
        pass

    @abc.abstractmethod
    def get_local_ipv4(self):
        pass

    @abc.abstractmethod
    def get_keys(self):
        pass


class MachineResolver(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_machine(self, ip):
        pass
