import os

def get_current_file_path():
    return os.path.abspath(__file__)

def main():
    current_file_path = get_current_file_path()
    #print("Path:", current_file_path)

if __name__ == "__main__":
    main()