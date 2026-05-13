class Match:
    def _init_(self, timestamp, match_id):
        self.time_start = timestamp
        self.mid = match_id
        self.specs = {}
        self.player_result = {}


class Tournament:
    def _init_(self, s_name, s_format):
        self.name = s_name
        self.format = s_format

    def 