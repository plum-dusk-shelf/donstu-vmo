import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class DACSystem:
    def __init__(self):
        #self.users = {}  
        self.users = { "root": hash_password("1488") }
        self.files = {}
        self.current_user = "root"
        self.create_file("readme.md")

    # ---------------- AUTH ----------------
    def create_user(self, username, password):
        if username in self.users:
            print("User already exists")
            return

        self.users[username] = hash_password(password)
        print(f"User {username} created")

    def login(self, username, password):
        if username not in self.users:
            print("User does not exist")
            return

        if self.users[username] != hash_password(password):
            print("Invalid password")
            return

        self.current_user = username
        print(f"Logged in as {username}")
        self.show_accessible_files()

    def logout(self):
        if self.current_user is None:
            print("No user logged in")
            return
        print(f"User {self.current_user} logged out")
        self.current_user = None

    def require_auth(self):
        if self.current_user is None:
            print("You must login first")
            return False
        return True

    # ---------------- FILES ----------------
    def create_file(self, filename):
        if not self.require_auth():
            return

        if filename in self.files:
            print("File already exists")
            return

        self.files[filename] = {
            "owner": self.current_user,
            "acl": {}
        }
        print(f"File {filename} created (owner: {self.current_user})")

    def grant(self, filename, target_user, rights):
        if not self.require_auth():
            return

        if filename not in self.files:
            print("File not found")
            return

        file = self.files[filename]

        if file["owner"] != self.current_user:
            print("Only owner can grant permissions")
            return

        if target_user not in self.users:
            print("Target user does not exist")
            return

        if target_user not in file["acl"]:
            file["acl"][target_user] = set()

        for r in rights:
            if r in "rwx":
                file["acl"][target_user].add(r)

        print(f"Granted {rights} to {target_user} on {filename}")

    # ---------------- ACCESS ----------------
    def check_access(self, filename):
        if not self.require_auth():
            return False

        if filename not in self.files:
            return False

        file = self.files[filename]

        if file["owner"] == self.current_user:
            return 'rwx'

        rights_map = {
            "read": "r",
            "write": "w",
            "execute": "x"
        }

        res = ''
        if not (self.current_user in file["acl"]):
            return "YOU ARE NOT PERMITED"
         
        else:
            return file["acl"][self.current_user]

    def read(self, filename):
        if self.check_access(filename, "read"):
            print("READ SUCCESS")
        else:
            print("ACCESS DENIED")

    def write(self, filename):
        if self.check_access(filename, "write"):
            print("WRITE SUCCESS")
        else:
            print("ACCESS DENIED")

    def show_acl(self, filename):
        if filename not in self.files:
            print("File not found")
            return

        file = self.files[filename]
        print(f"Owner: {file['owner']}")
        for user, rights in file["acl"].items():
            print(f"  {user}: {''.join(sorted(rights))}")

    # ---------------- NEW FEATURE ----------------
    def show_accessible_files(self):
        if not self.require_auth():
            return

        print("\nAccessible files:")

        found = False
        for filename, file in self.files.items():
            if file["owner"] == self.current_user:
                print(f"  {filename} (owner)")
                found = True
            elif self.current_user in file["acl"]:
                rights = "".join(sorted(file["acl"][self.current_user]))
                print(f"  {filename} ({rights})")
                found = True

        if not found:
            print("  (none)")
        print()


# ---------------- CLI ----------------
def main():
    dac = DACSystem()

    print("DAC system with auth + passwords")

    while True:
        try:
            cmd = input(">> ").strip().split()
            if not cmd:
                continue

            if cmd[0] == "exit":
                break

            elif cmd[0] == "help":
                print("""
Auth:
  create_user <name> <password>
  login <name> <password>
  logout

Files:
  create_file <filename>
  grant <filename> <user> <rwx>
  read <filename>
  write <filename>
  check <filename> <read/write/execute>
  show_acl <filename>
""")

            elif cmd[0] == "create_user":
                dac.create_user(cmd[1], cmd[2])

            elif cmd[0] == "login":
                dac.login(cmd[1], cmd[2])

            elif cmd[0] == "logout":
                dac.logout()

            elif cmd[0] == "create_file":
                dac.create_file(cmd[1])

            elif cmd[0] == "grant":
                dac.grant(cmd[1], cmd[2], cmd[3])

            elif cmd[0] == "read":
                dac.read(cmd[1])

            elif cmd[0] == "write":
                dac.write(cmd[1])

            elif cmd[0] == "check":
                result = dac.check_access(cmd[1])
                print("YOUR ACCESS:", result)

            elif cmd[0] == "show_acl":
                dac.show_acl(cmd[1])

            else:
                print("Unknown command")

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
