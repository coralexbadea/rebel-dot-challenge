class DatabaseError(Exception):
    def __init__(self, message=None):
        self.message = "Error connecting to the database."
        if message:
            self.message = message
        super().__init__(self.message)
