from argparse import ArgumentParser
import json, time, traceback, sys, threading

from prettytable import PrettyTable
from concurrent.futures import ThreadPoolExecutor 
from requests import exceptions

from config import (
    ENABLE_SENDMESSAGE,
    LOOP_CHECK_INTERVAL,
    ENABLE_MULTI_THREAD, 
    MAX_THREADS_NUM, 
    LESS_LOG
)
from check_init import PAGE_CACHE
from check_list import CHECK_LIST
from database import create_dbsession, Saved
from logger import write_log_info, print_and_log

# If True, the data will be forced to be saved to the database and a message will be sent to Telegram.
FORCE_UPDATE = False

# A lock that is used to protect the `check_failed_list` and `is_network_error` variables.
_THREADING_LOCK = threading.Lock()

def database_cleanup():
    """
    Removes projects from the database that are not in the `CHECK_LIST`.

    Returns:
        A list of the names of the removed projects.
    """
    with create_dbsession() as session:
        saved_ids = {x.ID for x in session.query(Saved).all()}
        checklist_ids = {x.__name__ for x in CHECK_LIST}
        drop_ids = saved_ids - checklist_ids
        for id_ in drop_ids:
            session.delete(session.query(Saved).filter(Saved.ID == id_).one())
        session.commit()
        return drop_ids

def _abort(text):
    """
    Print a message to the console and exit the program.

    Args:
        text: The message to print.
    """
    print_and_log(text, level="warning", custom_prefix="[*]")
    sys.exit(1)

def _abort_by_user():
    """
    Abort the program because the user pressed `Ctrl`+`C`.
    """
    return _abort("Abort by user")

def _sleep(sleep_time):
    """
    Sleep for the specified amount of time.

    Args:
        sleep_time: The amount of time to sleep in seconds.
    """
    try:
        time.sleep(sleep_time)
    except KeyboardInterrupt:
        _abort_by_user()

def _get_time_str(time_num=None, offset=0):
    """
    Get a string representation of the current time.

    Args:
        time_num: The Unix timestamp of the current time. If None, the current time will be used.
        offset: The number of seconds to add to the current time.

    Returns:
        A string representation of the current time.
    """
    if time_num is None:
        time_num = time.time()
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_num+offset))

def check_one(cls, disable_pagecache=False):
    """
    Checks a project for updates.

    Args:
        cls: The class that represents the project to check.
        disable_pagecache: If True, the project's page cache will be disabled.

    Returns:
        True if the project has been updated, False otherwise.
    """
    if isinstance(cls, str):
        cls_str = cls
        cls = {cls_.__name__: cls_ for cls_ in CHECK_LIST}.get(cls_str)
        if not cls:
            raise Exception("Can not found '%s' from CHECK_LIST!" % cls_str)
    cls_obj = cls()
    if disable_pagecache:
        cls_obj.enable_pagecache = False
    try:
        cls_obj.do_check()
    except exceptions.ReadTimeout:
        print_and_log("%s check failed! Timeout." % cls_obj.fullname, level="warning")
    except (exceptions.SSLError, exceptions.ProxyError):
        print_and_log("%s check failed! Proxy error." % cls_obj.fullname, level="warning")
    except exceptions.ConnectionError:
        print_and_log("%s check failed! Connection error." % cls_obj.fullname, level="warning")
    except exceptions.HTTPError as error:
        print_and_log("%s check failed! %s." % (cls_obj.fullname, error), level="warning")
    except:
        for line in traceback.format_exc().splitlines():
            print_and_log(line, level="warning", custom_prefix="")
        print_and_log("%s check failed!" % cls_obj.fullname, level="warning")
    else:
        # If the check was successful, update the database and send a message to Telegram.
        if cls_obj.is_updated() or FORCE_UPDATE:
            print_and_log(
                "%s has update: %s" % (cls_obj.fullname, cls_obj.info_dic["LATEST_VERSION"]),
                custom_prefix="[*]",
            )
            try:
                cls_obj.after_check()
            except:
                for line in traceback.format_exc().splitlines():
                    print_and_log(line, level="warning")
                print_and_log(
                    "%s: Something wrong when running after_check!" % cls_obj.fullname,
                    level="warning",
                )
            cls_obj.write_to_database()
            if ENABLE_SENDMESSAGE:
                cls_obj.send_message()
        # If the check was not successful, do nothing.        
        else:
            print("[*] %s has no update" % cls_obj.fullname)
            if not LESS_LOG:
                write_log_info("%s has no update" % cls_obj.fullname)
        return cls, True   

    # If the check was unsuccessful. 
    return cls, False

def single_thread_check(check_list):
    """
    Checks a list of projects for updates in a single thread.

    Args:
        check_list: A list of classes that represent the projects to check.

    Returns:
        A list of projects that have been updated, and a boolean value indicating whether there was a network error.
    """
    req_failed_flag = 0
    check_failed_list = []
    is_network_error = False
    for cls in check_list:
        result = check_one(cls)
        if not result[1]:
            req_failed_flag += 1
            check_failed_list.append(cls)
            if req_failed_flag == 5:
                is_network_error = True
                break
        else:
            req_failed_flag = 0
        _sleep(2)

    return check_failed_list, is_network_error

def multi_thread_check(check_list):
    """
    Checks a list of projects for updates in multiple threads.

    Args:
        check_list: A list of classes that represent the projects to check.

    Returns:
        A list of projects that have been updated, and a boolean value indicating whether there was a network error.
    """
    # Create a thread pool to execute the checks.
    with ThreadPoolExecutor(MAX_THREADS_NUM) as executor:
        results = list(executor.map(check_one, check_list))

    check_failed_list = [result[0] for result in results if not result[1]]

    # Check if there was a network error.
    is_network_error = len(check_failed_list) >= 10

    return check_failed_list, is_network_error

def loop_check():
    """
    Loops continuously and checks the items for updates.
    """
    # Run database cleanup before start.
    write_log_info("Run database cleanup before start")
    drop_ids = database_cleanup()
    write_log_info("Abandoned items: {%s}" % ", ".join(drop_ids))
    
    loop_check_func = multi_thread_check if ENABLE_MULTI_THREAD else single_thread_check
    
    # Get the list of items to check.
    check_list = [cls for cls in CHECK_LIST if not cls._skip]
    while True:
        # Start the check.
        start_time = _get_time_str()
        print("[*]" + start_time)
        print("[*] Started checking at " + start_time)
        write_log_info("=" * 64)
        write_log_info("Start checking at %s" % start_time)

        # Check the projects for updates.
        check_failed_list, is_network_error = loop_check_func(check_list)

         # If there was a network error, sleep for a few seconds.
        if is_network_error:
            print_and_log("Network or proxy error! Sleep...", level="warning")
            _sleep(10)
        else:
            # Check for projects that have failed to check.
            if check_failed_list:
                print_and_log("Check again for failed items")
                single_thread_check(check_failed_list)
                
        # Clear the page cache.         
        PAGE_CACHE.clear()

        print("[*] The next check will start at %s\n" % _get_time_str(offset=LOOP_CHECK_INTERVAL))
        write_log_info("End of check")
        
        # Sleep for the specified amount of time.
        _sleep(LOOP_CHECK_INTERVAL)
                
def get_saved_json():
    """
    Returns a JSON representation of the saved data.
    """
    # Get the saved data from the database.
    with create_dbsession() as session:
        results = session.query(Saved).all()

    # Convert the data to JSON.
    json_data = [result.get_kv() for result in results]

    return json.dumps(json_data, ensure_ascii=False)

def show_saved_data():
    """
    Print the saved data in a table format.
    """
    # Get the saved data from the database.
    with create_dbsession() as session:
        results = session.query(Saved).all()

    if not results:
        print("No saved data available.")
        return

    # Create a table to display the data.
    table = PrettyTable()
    table.field_names = ["ID", "Full Name", "Latest Version"]

    for result in results:
        table.add_row([result.ID, result.FULL_NAME, result.LATEST_VERSION])

    # Print the table.
    print(table)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--force", help="Force save to database & send message to Telegram", action="store_true")
    parser.add_argument("--dontpost", help="Do not send message to Telegram", action="store_true")
    parser.add_argument("-a", "--auto", help="Automatically loop check all items", action="store_true")
    parser.add_argument("-c", "--check", help="Check one item")
    parser.add_argument("-s", "--show", help="Show saved data", action="store_true")
    parser.add_argument("-j", "--json", help="Show saved data as json", action="store_true")

    args = parser.parse_args()

    if args.force:
        FORCE_UPDATE = True
    if args.dontpost:
        ENABLE_SENDMESSAGE = False
    if args.auto:
        loop_check()
    elif args.check:
        check_one(args.check, disable_pagecache=True)
    elif args.show:
        show_saved_data()
    elif args.json:
        print(get_saved_json())
    else:
        parser.print_usage()
