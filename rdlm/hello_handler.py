#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of restful-distributed-lock-manager released under the MIT license.
# See the LICENSE file for more information.

from rdlm.request_handler import RequestHandler, admin_authenticated
from rdlm.lock import LOCK_MANAGER_INSTANCE
from resource_file_operations import FILE_OPERATIONS
from conf_reader import CONF_READER
import logging
from rdlm.lock import Lock


class GetResources(object):

    @staticmethod
    def get_resources_list():
        '''
        @summary: returns resources list
        '''
        if CONF_READER.VALIDATE_RESOURCE is True:
            in_file_resources = FILE_OPERATIONS.get_resources()
            return in_file_resources
        else:
            in_file_resources = FILE_OPERATIONS.get_resources()
            mem_resources = LOCK_MANAGER_INSTANCE.get_resources_names()
            return in_file_resources + list(set(mem_resources) - set(in_file_resources))


class HelloHandler(RequestHandler):
    """Class which handles the / URL"""

    def get(self):
        '''
        @summary: deals with GET request on /
        '''
        # self.write('<title>Hello</title> - This is me !')
        self.render("index.html")


class AddResourceHandler(RequestHandler):
    """Class which handles the / URL"""

    def get(self):
        '''
        @summary: deals with GET request on /add
        '''
        self.render("addresource.html")

    def post(self):
        '''
        @summary: deals with POST for adding a resource
        '''
        resource = self.get_argument('resource')
        FILE_OPERATIONS.add_resource(resource)
        self.render("success.html", name=resource, operation="added")
        logging.info("Resource - %s - Added " % resource)


class ShowAllResourcesHandler(RequestHandler):
    """Class which handles the / URL"""

    def get(self):
        '''
        @summary: deals with GET request on /showallresource
        '''
        resources = {}
        total_resources = GetResources.get_resources_list()
        for resource_name in total_resources:
            tmp = LOCK_MANAGER_INSTANCE.get_resource_as_dict(resource_name)
            if tmp is not None:
                if len(tmp.get('locks')) > 0:
                    resources.update({resource_name: "Locked"})
                else:
                    resources.update({resource_name: ""})
            else:
                resources.update({resource_name: ""})
        logging.debug("Current Resources - %s" % resources)
        self.render("showallresources.html", resources=resources)


class ShowResourceHandler(RequestHandler):
    """Class which handles the / URL"""

    def get(self, name):
        '''
        @summary: deals with GET request on /showresource
        '''
        tmp = LOCK_MANAGER_INSTANCE.get_resource_as_dict(name)
        if tmp is not None:
            locks = tmp["locks"]
            self.render("showresource.html", name=name, locks=locks)
        else:
            self.render("showresource.html", name=name, locks={})


class RemoveResourceHandler(RequestHandler):
    """Class which handles the / URL"""

    def get(self):
        '''
        @summary: deals with GET request on /removeresource
        '''
        resources = GetResources.get_resources_list()
        self.render("removeresource.html", resources=resources)

    def post(self):
        '''
        @summary: deals with POST for removing a resource
        '''
        resource = self.get_argument('resource')
        FILE_OPERATIONS.remove_resource(resource)
        self.render("success.html", name=resource, operation="removed")
        logging.info("Resource - %s - Removed" % resource)


class RequestLockHandler(RequestHandler):
    """Class which handles the / URL"""

    def get(self):
        '''
        @summary: deals with GET request on /add
        '''
        resources = GetResources.get_resources_list()
        self.render("requestlock.html", resources=resources)

    def post(self):
        '''
        @summary: deals with POST for adding a resource
        '''
        resource = self.get_argument('resource')
        title = self.get_argument('title')
        lifetime = int(self.get_argument('lifetime'))
        wait = int(self.get_argument('wait'))
        logging.info("Resource - %s - Lock Requested with (%s, %s, %s)" % (resource, title, lifetime, wait))
        lock = Lock(resource, title, wait, lifetime)
        LOCK_MANAGER_INSTANCE.add_lock(resource, lock)
        logging.debug(lock.uid)
        self.render("requestlockresponse.html", name=resource, uid=lock.uid)


class ReleaseLockHandler(RequestHandler):
    """Class which handles the / URL"""

    def get(self):
        '''
        @summary: deals with GET request on /add
        '''
        resources = GetResources.get_resources_list()
        self.render("releaselock.html", resources=resources)

    def post(self):
        '''
        @summary: deals with POST for adding a resource
        '''
        name = self.get_argument('name')
        uid = self.get_argument('uid')
        logging.info("Release Requested - %s - %s" % (name, uid))
        res = LOCK_MANAGER_INSTANCE.delete_lock(name, uid)
        name = name + " - " + uid
        self.render("success.html", name=name, operation="released")
