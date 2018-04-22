#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of restful-distributed-lock-manager released under the MIT license.
# See the LICENSE file for more information.

from ConfigParser import SafeConfigParser
import logging


class ConfReader(object):
    DIR_PATH = ""
    FILE_PATH = ""
    VALIDATE_RESOURCE = True

    def __init__(self):
        self.parser = SafeConfigParser()
        self.__read_conf_file()
        self.__set_dir_path()
        self.__set_validate_resource()
        self.__set_file_path()

    def __read_conf_file(self):
        try:
            self.parser.read('/etc/rdlm/rdlm.conf')
        except Exception as e:
            logging.error(e)

    def __set_dir_path(self):
        ConfReader.DIR_PATH = self.parser.get('rdlm', 'directory_path')
        return ConfReader.DIR_PATH

    def __set_validate_resource(self):
        ConfReader.VALIDATE_RESOURCE = self.parser.getboolean('rdlm', 'validate_resource')
        return ConfReader.VALIDATE_RESOURCE

    def __set_file_path(self):
        ConfReader.FILE_PATH = ConfReader.DIR_PATH + "resrouce"


CONF_READER = ConfReader()
