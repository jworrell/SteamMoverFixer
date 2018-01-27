import os

import pywintypes
import win32.win32file as win32file


STEAM_COMMON = "C:\\Program Files (x86)\\Steam\\SteamApps\\common"
STEAM_VAULT = "E:\\SteamVault"


def main(steam_common, steam_vault):
    log_file = open("fixer.log", "w")

    for item in os.listdir(steam_vault):
        full_path = os.path.join(steam_common, item)
        desired_path = os.path.join(STEAM_VAULT, item)

        # First pass, look for files that fail to open (probably bad)
        try:
            handle = win32file.CreateFile(full_path,
                                          win32file.FILE_GENERIC_READ,
                                          win32file.FILE_SHARE_READ,
                                          None,
                                          win32file.OPEN_EXISTING,
                                          win32file.FILE_FLAG_BACKUP_SEMANTICS,
                                          None)

            final_path = win32file.GetFinalPathNameByHandle(handle, 0x0)

            win32file.CloseHandle(handle)

            if final_path[4:] == desired_path:
                print("Link is good: '{}' -> '{}'".format(full_path, final_path))
                continue

        except pywintypes.error as win32_error:
            pass

        # Second pass, look for files that failed for other reasons
        try:
            handle = win32file.CreateFile(full_path,
                                          win32file.FILE_GENERIC_READ,
                                          win32file.FILE_SHARE_READ,
                                          None,
                                          win32file.OPEN_EXISTING,
                                          win32file.FILE_FLAG_BACKUP_SEMANTICS | win32file.FILE_FLAG_OPEN_REPARSE_POINT,
                                          None)

            win32file.CloseHandle(handle)

        except pywintypes.error as win32_error:
            print("Skipping '{}' ({})".format(full_path, win32_error.strerror))
            continue

        log_file.write("{},{}\n".format(full_path, desired_path))

        print("Fixing: '{}' -> '{}'".format(full_path, desired_path))
        win32file.RemoveDirectory(full_path)
        win32file.CreateSymbolicLink(full_path, desired_path, 0x1 | 0x2)


if __name__ == "__main__":
    main(STEAM_COMMON, STEAM_VAULT)
