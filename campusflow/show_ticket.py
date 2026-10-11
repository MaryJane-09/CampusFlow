
class CampusFlow:
    def __init__(self):
        self.tickets = []

    @property
    def ticket(self):
        return self.tickets

    @ticket.setter
    def ticket(self, value):
        self.tickets = value


campus = CampusFlow()
