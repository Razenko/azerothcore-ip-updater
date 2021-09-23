# Azerothcore ip update script for realmlist 0.3 by Razenko

import sys
import os
from subprocess import check_call
from re import match
from time import sleep

try:
    import mysql.connector
except ImportError:
    print("Missing dependencies.. using pip to install them: \n")
    check_call([sys.executable, "-m", "pip", "install", 'mysql-connector-python'])
    print("\nDependencies installed. Please run this script again.")
    sys.exit()

from mysql.connector import Error

# Database settings
database_host = "127.0.0.1"
database_name = "acore_auth"
database_user = "acore"
database_password = "acore"

# Globals
TITLE = "*** Azerothcore realmlist ip updater script 0.3 ***\n"
TERMINAL_SPACING = "    "


def database_connect(host, name, user, password):
    try:
        print("Connecting to database...", end="")
        db_connection = mysql.connector.connect(host=host,
                                                database=name,
                                                user=user,
                                                password=password)
        if db_connection.is_connected():
            print("success!")
            return db_connection
        else:
            print("\nCould not connect to database!")
    except Error as error:
        print("\nDatabase initialisation failed", error)
        sys.exit()


def validate_ip(ip_address):
    return match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ip_address)


def validate_id(realm_id):
    realms = fetch_realmlist()
    for realm in realms:
        if str(realm_id) == str(realm[0]):
            return True
    return False


def fetch_realmlist():
    try:
        db_connection = database_connect(database_host, database_name, database_user, database_password)
        cursor = db_connection.cursor()
        fetch_query = "SELECT id,name,address FROM realmlist ORDER BY id DESC"
        cursor.execute(fetch_query)
        return cursor.fetchall()
    except Error as error:
        print("Could not fetch realmlists: ", error)
        return None


def update_ip(realm_id, ip_address):
    try:
        db_connection = database_connect(database_host, database_name, database_user, database_password)
        print("Updating realmlist (id %s) ip to: %s" % (realm_id, ip_address))
        cursor = db_connection.cursor()
        update_query = "UPDATE realmlist SET address = %s WHERE id = %s;"
        values = (ip_address, int(realm_id))
        cursor.execute(update_query, values)
        db_connection.commit()
    except Error as error:
        print("Updating realmlist ip failed", error)
        sys.exit()


def clear_screen():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')


def print_realms(realms):
    print(TERMINAL_SPACING + "Available realms on this server:")
    for realm in realms:
        print(TERMINAL_SPACING + str(realm[0]) + "." + str(realm[1]) + "\t(" + str(realm[2]) + ")")


def menu_message(message, waittime):
    print(message)
    print("Returning in:", end=" ", flush=True)
    for i in range(waittime):
        print(waittime - i, end=" ", flush=True)
        sleep(1)
    menu()


def menu():
    realms = fetch_realmlist()
    if realms:
        clear_screen()
        print(TITLE)
        print_realms(realms)
        print(TERMINAL_SPACING + "Q.Exit")
        realm_select = input("\nPlease select a realm to edit (eg. 1 for the first realm or Q to quit): ")
        if realm_select == "Q" or realm_select == "q":
            return
        for realm in realms:
            if str(realm_select) == str(realm[0]):
                verify_edit = input(
                    "Would you like to change the ip address of " + realm[1] + " (current: " + realm[2] + ") [Y/n]? ")
                if verify_edit == "Y":
                    new_ip = input("New ip address: ")
                    if validate_ip(new_ip):
                        update_ip(realm[0], new_ip)
                        menu_message("Operation completed", 3)
                    else:
                        menu_message("Invalid ip address!", 3)
                else:
                    menu_message("Edit aborted", 3)
            else:
                menu_message("Invalid input!", 3)
    else:
        print("No realms available!")


def main():
    print(TITLE)
    if len(sys.argv) == 1:
        menu()
    elif len(sys.argv) == 3:
        id_value = sys.argv[1]
        ip_value = sys.argv[2]
        if validate_ip(ip_value):
            if validate_id(id_value):
                update_ip(id_value, ip_value)
            else:
                print("Invalid id value!\nOperation cancelled.")
        else:
            print(ip_value, "is not a valid ip address!\nOperation cancelled.")
    else:
        print("Please adhere to the proper format when passing arguments: [realm id]  [ip_address]\n"
              "For example: 1 192.168.1.10")
    print("Exiting..")
    sys.exit()


if __name__ == "__main__":
    main()
