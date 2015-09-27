import unittest
from cloudbridge.providers import factory
from cloudbridge.providers import interfaces
from cloudbridge.providers.factory import CloudProviderFactory


class ProviderFactoryTestCase(unittest.TestCase):

    def test_create_provider_valid(self):
        """
        Creating a provider with a known name should return
        a valid implementation
        """
        self.assertIsInstance(CloudProviderFactory().create_provider(factory.ProviderList.EC2, {}, version=1),
                              interfaces.CloudProvider,
                              "create_provider did not return a valid instance type")

    def test_create_provider_invalid(self):
        """
        Creating a provider with an invalid name should raise a NotImplementedError
        """
        with self.assertRaises(NotImplementedError):
            CloudProviderFactory().create_provider("ec23", {})
        with self.assertRaises(NotImplementedError):
            CloudProviderFactory().create_provider(factory.ProviderList.EC2, {}, version=100)

    def test_find_provider_impl_valid(self):
        """
        Searching for a provider with a known name or version should return a valid implementation
        """
        self.assertTrue(CloudProviderFactory().find_provider_impl(factory.ProviderList.EC2))
        self.assertEquals(CloudProviderFactory().find_provider_impl(factory.ProviderList.EC2, version=1),
                          "cloudbridge.providers.ec2.EC2CloudProviderV1")

    def test_find_provider_impl_invalid(self):
        """
        Searching for a provider with an invalid name or version should return None
        """
        self.assertIsNone(CloudProviderFactory().find_provider_impl("openstack1"))
        self.assertIsNone(CloudProviderFactory().find_provider_impl(
            factory.ProviderList.EC2, version=100))