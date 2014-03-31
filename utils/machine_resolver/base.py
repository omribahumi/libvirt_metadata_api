import abc

__all__ = ['MachineResolverException', 'Machine', 'MachineResolver']


class MachineResolverException(Exception):
    """
    Base exception for Machine/MachineResolver objects to throw
    """

    pass


class Machine(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_userdata(self):
        """
        :return: the machine's user-data
        :rtype: str
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get_instance_id(self):
        """
        :return: the machine's instance-id
        :rtype: str
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get_public_ipv4(self):
        """
        :return: the machine's public IPv4
        :rtype: str
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get_local_ipv4(self):
        """
        :return: the machine's private IPv4
        :rtype: str
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get_keys(self):
        """
        :return: the machine's public keys
        :rtype: collections.OrderedDict {'key_name': {'key_format': 'value', ...}, ...}
        """

        raise NotImplementedError


class MachineResolver(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_machine(self, ip):
        """
        :param ip: IP address to look up
        :type ip: str
        :return: Machine interface
        :rtype: Machine
        """

        raise NotImplementedError
