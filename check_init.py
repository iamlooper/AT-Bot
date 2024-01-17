import json, time, re
from collections import OrderedDict
from urllib.parse import unquote, urlencode

import requests
from bs4 import BeautifulSoup
import lxml
from requests.packages import urllib3
from sqlalchemy.orm import exc as sqlalchemy_exc

from config import (
    ENABLE_MULTI_THREAD, 
    TIMEOUT, 
    GH_USERNAME, 
    GH_TOKEN
)
from database import create_dbsession, Saved
from page_cache import PageCache
from tgbot import send_message as _send_message
from logger import print_and_log

del lxml

# Disable insecure request warning.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"
)

_KEY_TO_PRINT = {
    "BUILD_TYPE": "Build type",
    "BUILD_VERSION": "Build version",
    "BUILD_DATE": "Build date",
    "BUILD_CHANGELOG": "Changelog",
    "FILE_MD5": "MD5",
    "FILE_SHA1": "SHA1",
    "FILE_SHA256": "SHA256",
    "DOWNLOAD_LINK": "Download",
    "FILE_SIZE": "Size",
}

PAGE_CACHE = PageCache()

class CheckUpdate:
    # Base class for checking updates.

    fullname = None
    enable_pagecache = False
    _skip = False

    def __init__(self):
        self._abort_if_missing_property("fullname")
        self.__info_dic = OrderedDict([
            ("LATEST_VERSION", None),
            ("BUILD_TYPE", None),
            ("BUILD_VERSION", None),
            ("BUILD_DATE", None),
            ("BUILD_CHANGELOG", None),
            ("FILE_MD5", None),
            ("FILE_SHA1", None),
            ("FILE_SHA256", None),
            ("DESCRIPTION", None),            
            ("DOWNLOAD_TEXT", None),            
            ("DOWNLOAD_LINK", None),
            ("ALT_DOWNLOAD_LINK", None),  
            ("FILE_SIZE", None),
        ])
        self._private_dic = {}
        self.__is_checked = False
        try:
            self.__prev_saved_info = Saved.get_saved_info(self.name)
        except sqlalchemy_exc.NoResultFound:
            self.__prev_saved_info = None

        # Decorate these methods when initializing an instance
        # Set self.__is_checked to True automatically after executing self.do_check method
        # and prevent certain methods from being executed when self.__is_checked is not True
        self.do_check = self.__hook_do_check(self.do_check)
        self.after_check = self.__hook_is_checked(self.after_check)
        self.write_to_database = self.__hook_is_checked(self.write_to_database)
        self.is_updated = self.__hook_is_checked(self.is_updated)
        self.get_print_text = self.__hook_is_checked(self.get_print_text)
        self.send_message = self.__hook_is_checked(self.send_message)

    def __hook_do_check(self, method):
        def hook(*args, **kwargs):
            method(*args, **kwargs)
            # If an exception is raised in the previous line, the following line will not be executed
            self.__is_checked = True
            # Must return None
        return hook

    def __hook_is_checked(self, method):
        def hook(*args, **kwargs):
            assert self.__is_checked, "Please execute the 'do_check' method first."
            return method(*args, **kwargs)
        return hook

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def info_dic(self):
        return self.__info_dic.copy()

    @property
    def prev_saved_info(self):
        return self.__prev_saved_info

    def _abort_if_missing_property(self, *props):
        if None in (getattr(self, key, None) for key in props):
            raise Exception(
                "Subclasses inherited from the %s class must specify the '%s' property when defining!"
                % (self.name, "' & '".join(props))
            )

    def update_info(self, key, value):
        # Update the info_dic dictionary, check and convert key and value before updating.
        if key not in self.__info_dic.keys():
            raise KeyError("Invalid key: %s" % key)
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        if value is not None:
            if not isinstance(value, str):
                print_and_log(
                    "%s.update_info: Attempt to convert %s to strings when updating %s key." % (
                        self.name, type(value), key
                    ),
                    level="warning",
                )
                value = str(value)
        self.__info_dic[key] = value

    @classmethod
    def request_url(cls, url, method="get", encoding="utf-8", **kwargs):        
        """
        Wrapped requests with some simplifications.
        Timeout has a default value, or you can customize the parameter as needed.
        :param url: The URL to request.
        :param method: The request method, optional: "get" (default) or "post".
        :param encoding: Text encoding, default is utf-8.
        :param kwargs: Other parameters to pass to requests.
        :return: The source code of the URL page.
        """

        def _request_url(url_, method_, encoding_, **kwargs_):
            if method_ == "get":
                requests_func = requests.get
            elif method_ == "post":
                requests_func = requests.post
            else:
                raise Exception("Unknown request method: %s" % method_)
            params = kwargs_.get("params")
            if cls.enable_pagecache and method_ == "get":
                saved_page_cache = PAGE_CACHE.read(url_, params)
                if saved_page_cache is not None:
                    return saved_page_cache
            timeout = kwargs_.pop("timeout", TIMEOUT)
            if GH_USERNAME is None:
                req = requests_func(
                    url_, timeout=timeout, proxies=None, **kwargs_
                )
            else:
                req = requests_func(
                    url_, auth=(GH_USERNAME,GH_TOKEN), timeout=timeout, proxies=None, **kwargs_
                )           
            req.raise_for_status()
            req.encoding = encoding_
            req_text = req.text
            if cls.enable_pagecache:
                PAGE_CACHE.save(url_, params, req_text)
            return req_text

        # In multi-threading mode, only one CheckUpdate object with enable_pagecache set to True is allowed to make a request at a time.
        # Other CheckUpdate objects on different threads with enable_pagecache set to True must wait.
        # This ensures avoidance of duplicate requests and prevents conflicts in PAGE_CACHE read/write operations.
        if cls.enable_pagecache and ENABLE_MULTI_THREAD:
            with PAGE_CACHE.threading_lock:
                return _request_url(url, method, encoding, **kwargs)
        return _request_url(url, method, encoding, **kwargs)

    @classmethod
    def get_hash_from_file(cls, url, **kwargs):
        """
        Request the URL of the hash verification file and return the hash value from the file.
        :param url: The URL of the hash verification file.
        :param kwargs: Parameters to be passed to the self.request_url method.
        :return: The hash value string.
        """
        return cls.request_url(url, **kwargs).strip().split()[0]

    @staticmethod
    def get_bs(url_text, **kwargs):
        """
        Simple wrapper for the BeautifulSoup function.
        :param url_text: URL source code
        :return: BeautifulSoup object
        """
        features = kwargs.pop("features", "lxml")
        return BeautifulSoup(url_text, features=features, **kwargs)

    @staticmethod
    def getprop(text, key, delimiter=":", default=None, ignore_case=False):
        # Similar to Linux's getprop command, the default separator is ':'. Although it should return a string according to common sense, the default value returned when no result is found is None.
        for line in text.strip().splitlines():
            if delimiter not in line:
                continue
            k, v = (x.strip() for x in line.split(delimiter, 1))
            if ignore_case:
                if k.upper() == key.upper():
                    return v
            else:
                if k == key:
                    return v
        return default

    def do_check(self):
        """
        Start the update check, including page requests, data cleaning, and updating of info_dic, all of which should be done in this method.
        :return: None
        """
        # Note: Please do not directly modify the self.__info_dic dictionary; instead, use the self.update_info method.
        # For consistency, this method does not allow any parameters to be passed and does not allow any return values.
        # If you really need to reference parameters, you can add new class attributes when inheriting.
        raise NotImplementedError

    def after_check(self):
        """
        This method will only be executed after it is determined that the check object has been updated.
        For example, if you have code to download the hash file and retrieve the hash value, you can place it here to save some time (doing these actions when there is no update is pointless).
        :return: None
        """
        # For consistency, this method does not allow any parameters to be passed and does not allow any return values.
        # If you really need to use some variables from self.do_check method, you can pass them through self._private_dic.
        pass

    def write_to_database(self):
        # Write the info_dic data of a CheckUpdate instance into a database.
        with create_dbsession() as session:
            try:
                saved_data = session.query(Saved).filter(Saved.ID == self.name).one()
            except sqlalchemy_exc.NoResultFound:
                new_data = Saved(
                    ID=self.name,
                    FULL_NAME=self.fullname,
                    **self.__info_dic
                )
                session.add(new_data)
            else:
                saved_data.FULL_NAME = self.fullname
                for key, value in self.__info_dic.items():
                    setattr(saved_data, key, value)
            session.commit()

    def is_updated(self):
        """
        Compare with the data stored in the database. If there are any updates, return True; otherwise, return False.
        In general, only compare the LATEST_VERSION field. Subclasses can extend this method as needed when inheriting.
        """
        if self.__info_dic["LATEST_VERSION"] is None:
            return False
        if self.__prev_saved_info is None:
            return True
        return self.__info_dic["LATEST_VERSION"] != self.__prev_saved_info.LATEST_VERSION

    def get_print_text(self):
        # Retrieve updated message text.
        print_str_list = [
            "*%s | New Update!*" % self.fullname,
            time.strftime("%Y-%m-%d", time.localtime(time.time())),
        ]
        for key, value in self.__info_dic.items():
            if value is None:
                continue
            if key == "LATEST_VERSION":
                continue
            if key in "FILE_MD5 FILE_SHA1 FILE_SHA256 BUILD_DATE BUILD_TYPE BUILD_VERSION":
                value = "`%s`" % value
            if key == "BUILD_CHANGELOG":
                if value.startswith("http"):
                    value = "[%s](%s)" % (value, value)
                else:
                    value = "`%s`" % value
            if key == "DOWNLOAD_LINK" and value.startswith("http"):
                value = "[%s](%s)" % (self.__info_dic.get("LATEST_VERSION", ""), value)
            print_str_list.append("\n%s:\n%s" % (_KEY_TO_PRINT[key], value))
        return "\n".join(print_str_list)

    def send_message(self):
        _send_message(self.get_print_text())

    def __repr__(self):
        return "%s(fullname='%s', info_dic={%s})" % (
            self.name,
            self.fullname,
            ", ".join([
                "%s='%s'" % (key, str(value).replace("\n", "\\n"))
                for key, value in self.__info_dic.items() if value is not None
            ])
        )

class CheckUpdateWithBuildDate(CheckUpdate):
    """
    During the execution of the is_updated method, an additional check is performed on the BUILD_DATE field.
    If the BUILD_DATE is earlier than the stored BUILD_DATE in the database, it is considered not updated.
    If inheriting from this class, the date_transform method must be implemented.
    """

    @classmethod
    def date_transform(cls, date_str: str):
        """
        Parse a time string for comparison
        :param date_str: The time string to be parsed
        :return: An object that can be compared
        """
        raise NotImplementedError

    def is_updated(self):
        result = super().is_updated()
        if not result:
            return False
        if self.info_dic["BUILD_DATE"] is None:
            return False
        if self.prev_saved_info is None:
            return True
        latest_date = self.date_transform(str(self.info_dic["BUILD_DATE"]))
        try:
            saved_date = self.date_transform(self.prev_saved_info.BUILD_DATE)
        except:
            return True
        return latest_date > saved_date

class SfCheck(CheckUpdateWithBuildDate):
    project_name = None
    developer = None
    description = None
    sub_path = ""

    _MONTH_TO_NUMBER = {
        "Jan": "01", "Feb": "02", "Mar": "03",
        "Apr": "04", "May": "05", "Jun": "06",
        "Jul": "07", "Aug": "08", "Sep": "09",
        "Oct": "10", "Nov": "11", "Dec": "12",
    }

    def __init__(self):
        self._abort_if_missing_property("project_name")
        self._abort_if_missing_property("developer")
        super().__init__()

    @classmethod
    def date_transform(cls, date_str):
        # Date: "Wed, 12 Feb 2020 12:34:56 UT"
        date_str_ = date_str.rsplit(" ", 1)[0].split(", ")[1]
        date_str_month = date_str_.split()[1]
        date_str_ = date_str_.replace(date_str_month, cls._MONTH_TO_NUMBER[date_str_month])
        return time.strptime(date_str_, "%d %m %Y %H:%M:%S")

    @classmethod
    def filter_rule(cls, string):
        # File filtering rules
        return string.endswith(".zip")

    def do_check(self):
        url = "https://sourceforge.net/projects/%s/rss" % self.project_name
        bs_obj = self.get_bs(
            self.request_url(url, params={"path": "/"+self.sub_path}),
            features="xml",
        )
        builds = list(bs_obj.select("item"))
        if not builds:
            return
        builds.sort(key=lambda x: self.date_transform(x.pubDate.get_text()), reverse=True)
        for build in builds:
            file_size_mb = int(build.find("media:content")["filesize"]) / 1000 / 1000
            # Filter files smaller than 500MB.
            if file_size_mb < 500:
                continue
            file_version = build.guid.get_text().split("/")[-2]
            if self.filter_rule(file_version):
                self.update_info("LATEST_VERSION", file_version)
                self.update_info("DOWNLOAD_LINK", build.guid.get_text())
                self.update_info("BUILD_DATE", build.pubDate.get_text())
                self.update_info("FILE_MD5", build.find("media:hash", {"algo": "md5"}).get_text())
                self.update_info("FILE_SIZE", "%0.1f MB" % file_size_mb)
                break

        if self.description:
            self.update_info(
                "DESCRIPTION",
                "\n".join([
                    "",
                    "*Description:* _%s_" % self.description,
                    "*More information:* [Click here](https://sourceforge.net/projects/%s)" % self.project_name,
                ])
            )  
        else:
            self.update_info(
                "DESCRIPTION",
                "\n".join([
                    "*Description:* [Click here](https://sourceforge.net/projects/%s)" % self.project_name,
                ])
            )                        

    def get_print_text(self):
        return "\n".join([
            "*%s | New Update!*" % self.fullname,
            "",
            "*Developer:* [%s](https://sourceforge.net/u/%s/profile)" % (self.developer, self.developer),
            "*Release filename:* %s" % self.info_dic["LATEST_VERSION"],
            "*Release date:* %s" % self.info_dic["BUILD_DATE"],
            self.info_dic["DESCRIPTION"],
            "",
            "*MD5:* %s" % self.info_dic["FILE_MD5"],
            "*Size:* %s" % self.info_dic["FILE_SIZE"],
            "*Download:* [%s](%s)" % (self.info_dic["LATEST_VERSION"], self.info_dic["DOWNLOAD_LINK"]),
            "",
            "*Join:* @AndroFire | @AndroFireChat",
        ])        

class PlingCheck(CheckUpdate):
    p_id = None
    developer = None
    description = None

    def __init__(self):
        self._abort_if_missing_property("p_id")
        self._abort_if_missing_property("developer") 
        super().__init__()

    @staticmethod
    def filter_rule(build_dic):
        # File filtering rules
        return int(build_dic["active"])

    def do_check(self):
        url = "https://www.pling.com/p/%s/loadFiles" % self.p_id
        json_dic_files = json.loads(self.request_url(url)).get("files")
        if not json_dic_files:
            return
        json_dic_filtered_files = [f for f in json_dic_files if self.filter_rule(f)]
        if not json_dic_filtered_files:
            return
        latest_build = json_dic_filtered_files[-1]
        self._private_dic["latest_build"] = latest_build
        self.update_info("LATEST_VERSION", latest_build["name"])
        self.update_info("BUILD_DATE", latest_build["updated_timestamp"])
        if self.description:
            self.update_info(
                "DESCRIPTION",
                "\n".join([
                    "",
                    "*Description:* _%s_" % self.description,
                    "*More information:* [Click here](https://pling.com/p/%s)" % self.p_id,
                ])
            )  
        else:
            self.update_info(
                "DESCRIPTION",
                "\n".join([
                    "*Description:* [Click here](https://pling.com/p/%s)" % self.p_id,
                ])
            )                               
        self.update_info("FILE_MD5", latest_build["md5sum"])
        self.update_info(
            "DOWNLOAD_LINK", "https://www.pling.com/p/%s/#files-panel" % self.p_id
        )

    def after_check(self):
        latest_build = self._private_dic["latest_build"]
        if latest_build["tags"] is None:
            real_download_link = "https://www.pling.com/p/%s/startdownload?%s" % (
                self.p_id,
                urlencode({
                    "file_id": latest_build["id"],
                    "file_name": latest_build["name"],
                    "file_type": latest_build["type"],
                    "file_size": latest_build["size"],
                })
            )
        else:
            real_download_link = unquote(latest_build["tags"]).replace("link##", "")
        file_size = latest_build["size"]
        if file_size:
            self.update_info(
                "FILE_SIZE",
                "%0.2f MB" % (int(file_size) / 1048576,)
            )
        self.update_info(
            "DOWNLOAD_LINK",
            "[Pling](%s) | [Direct](%s)" % (
                "https://www.pling.com/p/%s/#files-panel" % self.p_id,
                real_download_link,
            )
        )
        
    def get_print_text(self):
        return "\n".join([
            "*%s | New Update!*" % self.fullname,
            "",
            "*Developer:* [%s](https://pling.com/u/%s)" % (self.developer, self.developer),
            "*Release filename:* %s" % self.info_dic["LATEST_VERSION"],
            "*Release date:* %s" % self.info_dic["BUILD_DATE"],
            self.info_dic["DESCRIPTION"],
            "",
            "*MD5:* %s" % self.info_dic["FILE_MD5"],
            "*Size:* %s" % self.info_dic["FILE_SIZE"],
            "*Download:* %s" % self.info_dic["DOWNLOAD_LINK"],
            "",
            "*Join:* @AndroFire | @AndroFireChat",
        ])                

class GithubReleases(CheckUpdateWithBuildDate):
    repository_url = None
    developer = None
    description = None
    ignore_prerelease = True

    def __init__(self):
        self._abort_if_missing_property("repository_url")
        self._abort_if_missing_property("developer") 
        super().__init__()

    @classmethod
    def date_transform(cls, date_str):
        # example: "2022-02-02T08:21:26Z"
        return time.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")

    def do_check(self):
        url = "https://api.github.com/repos/%s/releases/latest" % self.repository_url
        latest_json = json.loads(self.request_url(url))
        if not latest_json:
            return
        if latest_json["draft"]:
            return
        if self.ignore_prerelease and latest_json["prerelease"]:
            return
        self.update_info("BUILD_VERSION", latest_json["name"] or latest_json["tag_name"])
        self.update_info("LATEST_VERSION", latest_json["html_url"])
        self.update_info("BUILD_DATE", latest_json["published_at"])
        if self.description:
            self.update_info(
                "DESCRIPTION",
                "\n".join([
                    "",
                    "*Description:* _%s_" % self.description,
                    "*More information:* [Click here](https://github.com/%s/#readme)" % self.repository_url,
                ])
            )  
        else:
            self.update_info(
                "DESCRIPTION",
                "\n".join([
                    "*Description:* [Click here](https://github.com/%s/#readme)" % self.repository_url,
                ])
            )                       
        self.update_info(
            "DOWNLOAD_LINK",
            "\n".join([
                "[%s (%s)](%s)" % (
                    # File name, File size, Download link
                    asset["name"], "%0.1f MB" % (int(asset["size"]) / 1024 / 1024), asset["browser_download_url"]
                )
                for asset in latest_json["assets"]
            ])
        )
        self.update_info(
            "ALT_DOWNLOAD_LINK",
            "\n".join([
                "[Click here](%s)" % self.info_dic["LATEST_VERSION"],
            ])
        ) 
        # Use the alternative download link if assets are not found.
        self.update_info("DOWNLOAD_LINK", self.info_dic["DOWNLOAD_LINK"] or self.info_dic["ALT_DOWNLOAD_LINK"])
        if not latest_json["assets"]:
            self.update_info(
                "DOWNLOAD_TEXT",
                "\n".join([
                    "Download: "
                ])
            )     
        else: 
            self.update_info(
                "DOWNLOAD_TEXT",
                "\n".join([
                    "Downloads\n"
                ])
            )                    

    def get_print_text(self):
        return "\n".join([
            "*%s | New Update!*" % self.fullname, 
            "",
            "*Developer:* [%s](https://github.com/%s)" % (self.developer, self.developer),
            "*Release title:* [%s](%s)" % (self.info_dic["BUILD_VERSION"], self.info_dic["LATEST_VERSION"]),
            "*Release date:* %s" % self.info_dic["BUILD_DATE"],
            self.info_dic["DESCRIPTION"],
            "",
            "*%s*%s" % (self.info_dic["DOWNLOAD_TEXT"], self.info_dic["DOWNLOAD_LINK"]),
            "",
            "*Join:* @AndroFire | @AndroFireChat",
        ])