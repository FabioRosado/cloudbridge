import logging

from cloudbridge.cloud.base.resources import ClientPagedResultList
from cloudbridge.cloud.base.services import BaseObjectStoreService, BaseSecurityGroupService, BaseSecurityService

from .resources import AzureBucket, AzureSecurityGroup

log = logging.getLogger(__name__)


class AzureSecurityService(BaseSecurityService):
    def __init__(self, provider):
        super(AzureSecurityService, self).__init__(provider)

        # Initialize provider services
        # self._key_pairs = AzureKeyPairService(provider)
        self._security_groups = AzureSecurityGroupService(provider)

    @property
    def key_pairs(self):
        """
        Provides access to key pairs for this provider.

        :rtype: ``object`` of :class:`.KeyPairService`
        :return: a KeyPairService object
        """
        return None

    @property
    def security_groups(self):
        """
        Provides access to security groups for this provider.

        :rtype: ``object`` of :class:`.SecurityGroupService`
        :return: a SecurityGroupService object
        """
        return self._security_groups


class AzureSecurityGroupService(BaseSecurityGroupService):
    def __init__(self, provider):
        super(AzureSecurityGroupService, self).__init__(provider)

    def get(self, sg_id):
        for item in self.provider.azure_client.list_security_group():
            if item.id == sg_id:
                return AzureSecurityGroup(self.provider, item)
        return None

    def list(self, limit=None, marker=None):
        nsg_list = self.provider.azure_client.list_security_group()
        network_security_group = [AzureSecurityGroup(self.provider, sg)
                                  for sg in nsg_list]
        return ClientPagedResultList(self.provider, network_security_group, limit, marker)

        # network_id is similar to resource group in azure
    def create(self, name, description, network_id):
        parameters = {"location": self.provider.region_name}
        result = self.provider.azure_client.create_security_group(name, parameters)
        return AzureSecurityGroup(self.provider, result)

    def find(self, name, limit=None, marker=None):
        raise NotImplementedError(
            "AzureSecurityGroupService does not implement this method")

    def delete(self, group_id):
        for item in self.provider.azure_client.list_security_group():
            if item.id == group_id:
                sg_name = item.name
                self.provider.azure_client.delete_security_group(sg_name)
                return True
        return False


class AzureObjectStoreService(BaseObjectStoreService):
    def __init__(self, provider):
        super(AzureObjectStoreService, self).__init__(provider)

    def get(self, bucket_id):
        log.info("Azure Object Store Service get API with bucket id - " + str(bucket_id))
        object_store = self.provider.azure_client.get_container(bucket_id)
        if object_store:
            return AzureBucket(self.provider, object_store)
        return None

    def find(self, name, limit=None, marker=None):
        object_store = self.provider.azure_client.get_container(name)
        object_stores = []
        if object_store:
            object_stores.append(AzureBucket(self.provider, object_store))

        return ClientPagedResultList(self.provider, object_stores,
                                     limit=limit, marker=marker)

    def list(self, limit=None, marker=None):
        object_stores = [AzureBucket(self.provider, object_store)
                   for object_store in
                   self.provider.azure_client.list_containers()]
        return ClientPagedResultList(self.provider, object_stores,
                                     limit=limit, marker=marker)

    def create(self, name, location=None):
        object_store = self.provider.azure_client.create_container(name)
        return AzureBucket(self.provider, object_store)