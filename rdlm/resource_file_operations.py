#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of restful-distributed-lock-manager released under the MIT license.
# See the LICENSE file for more information.

from subprocess import Popen, PIPE, STDOUT
import os
import logging
from conf_reader import CONF_READER


class ResourceFileOperations(object):

    def __init__(self):
        pass

    def add_resource(self, name):
        '''
        @summary: deals with adding a resource into file
        '''
        name = name.strip()
        self.__create_directory()
        self.__create_file()
        self.__add_resource_to_file(name)

    def get_resources(self):
        '''
        @summary: deals with getting resources from the file
        '''
        logging.debug("Getting Resources from file")
        try:
            with open(CONF_READER.FILE_PATH, "a+") as f:
                content = f.readlines()
            content = [x.strip() for x in content]
            return content
        except:
            return []

    def remove_resource(self, name):
        '''
        @summary: deals with removing resource from the file
        '''
        logging.debug("Remove Resource - %s - from file" % name)
        content = self.get_resources()
        try:
            content.remove(name)
            self.__write_content_to_file(content)
        except:
            logging.debug("Matching resource not found in the resource list for removal")
            pass

    def __write_content_to_file(self, content):
        '''
        @summary: writes list to file
        '''
        with open(CONF_READER.FILE_PATH, "w") as f:
            for resource in content:
                f.write(resource + "\n")

    def __add_resource_to_file(self, name):
        '''
        @summary: appends resource to file
        '''
        content = self.get_resources()
        logging.debug("Adding Resource - %s - to file" % name)
        if name not in content:
            with open(CONF_READER.FILE_PATH, "a+") as f:
                f.write(name + "\n")
        else:
            logging.debug("Resource - %s - exists in file" % name)
            pass

    def is_resource_valid(self, name):
        '''
        @summary: validate if the resource is present in the file
        '''
        content = self.get_resources()
        if name not in content:
            logging.debug("Resource - %s - Invalid" % name)
            return False
        else:
            logging.debug("Resource - %s - Valid" % name)
            return True

    def __create_directory(self):
        '''
        @summary: checks and create directory if not present
        '''
        if os.path.exists(CONF_READER.DIR_PATH):
            logging.debug("Directory - %s - Exists" % CONF_READER.DIR_PATH)
            pass
        else:
            logging.debug("Creating directory - %s " % CONF_READER.DIR_PATH)
            cmd = "mkdir -p " + CONF_READER.DIR_PATH
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            output = p.stdout.read()
            logging.debug(output)

    def __create_file(self):
        '''
        @summary: checks and create file if not present
        '''
        if os.path.exists(CONF_READER.FILE_PATH):
            logging.debug("Resource File - %s - Exists" % CONF_READER.FILE_PATH)
            pass
        else:
            logging.debug("Creating File - %s " % CONF_READER.FILE_PATH)
            cmd = "touch " + CONF_READER.FILE_PATH
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            output = p.stdout.read()
            logging.debug(output)


FILE_OPERATIONS = ResourceFileOperations()
