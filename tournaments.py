class Player:
    def __init__(self, s_hash, s_name):
        self.hash = s_hash
        self.name = s_name
        self.played_matches = [] #storing mids here I think

    def calc_stats(self, matches: list): # 
        results = {
            
        }

class Team:
    def __init__(self, s_id, s_name):
        self.id = s_id
        self.name = s_name
        self.players = [] # here'll be dict w/ players with their specs like id, name etc.
        

class Match:
    def _init_(self, match_id, s_player_results: list, s_specs: dict):
        self.id = match_id
        self.specs = {}
        for key in s_specs.keys():
            self.specs[key] = s_specs[key]
        self.player_results = s_player_results

            
    def get_results(self, s_params: str):
        match s_params:
            case "teams":
                teams = {}
                for player in self.player_results:
                    teamNum = player["teamNum"] - 2
                    if teamNum not in teams.keys():
                        teams[teamNum] = {
                            "kills": 0,
                            "damage": 0,
                            "placement": player["teamPlacement"],
                            "players": []
                        }
                    teams[teamNum]["players"].append(player["nidHash"])
                    teams["kills"] += player["kills"]
                    teams["damage"] += player["damageDealt"]
                return teams
            case "players":
                players = {}
                for player in self.player_results:
                    playerHash = player["nidHash"]
                    players[playerHash] = {
                        "kills": player["kills"],
                        "damage" : player["damageDealt"],
                        "knockdowns": player["knockdowns"],
                        "character": player["characterName"],
                        "teamNum": player["teamNum"],
                        "playerName": player["playerName"],
                        "hardware": player["hardware"],
                        "shots": player["shots"],
                        "hits": player["hits"],
                        "revives": player["revivesGiven"],
                        "respawns": player["respawnsGiven"],
                        "headshots": player["headshots"],
                        "assists": player["assists"],
                        "survivalTime": player["survivalTime"]
                    }
                return players
            case "overall":
                match = {
                    "kills": 0, #
                    "shots": 0, #
                    "damage": 0, #
                    "respawns": 0, #
                    "duration": 0, #
                    "revives": 0, #
                    "winner": 0, # teamNum i think
                    "killLeader": "", # nidHash
                    "maxKills": 0, #
                    "hits": 0, #
                    "assists": 0, #
                    "characters": {}, # characterName and its pickrate
                    "headshots": 0 #
                }
                for player in self.player_results:
                    if match["maxKills"] < player["kills"]:
                        match["maxKills"] = player["kills"]
                        match["killLeader"] = player["nidHash"] 
                    match["kills"] += player["kills"]
                    match["shots"] += player["shots"]
                    match["damage"] += player["damageDealt"]
                    match["respawns"] += player["respawnsGiven"]
                    match["revives"] += player["revivesGiven"]
                    match["headshots"] += player["headshots"]
                    match["hits"] += player["hits"]
                    match["assists"] += player["assists"]
                    match["headshots"] += player["headshots"]
                    if player["characterName"] not in match["characters"].keys():
                        match["characters"][player["characterName"]] = 0
                    match["characters"][player["characterName"]] += 1
                    if match["duration"] < player["survivalTime"]:
                        match["duration"] = player["survivalTime"]
                    if player["teamPlacement"] == 0:
                        return {}
                    elif player["teamPlacement"] == 1:
                        match["winner"] = player["teamNum"]
                return match
            case _:
                print("Unknown command")
                    
                        

class Group:
    def __init__(self, s_id, s_name, s_settings):
        self.id = s_id
        self.name = s_name
        self.format = s_settings # it'll store amount of matches, maps, ban_specs, lobby format etc
        self.dropspots = {"isWork": 0}
        if (self.format["format"] == "ALGS"):
            self.dropspots["isWork"] = 0
        self.dropspots = {"isWork": 0}
        self.banned_characters = []
        self.matches = []
        self.scoreboard = {} # maybe slot is a key & the value is a list w/ every match data for the team???
        self.teams = [] # each team means lobby slot
        self.status = "Pending"
        self.points = { # describes amount of points awarded to a team for placement in a single match
        "ALGS": {
            1: 12,
            2: 9,
            3: 7,
            4: 5,
            5: 4,
            6: 3,
            7: 3,
            8: 2,
            9: 2,
            10: 2,
            11: 1,
            12: 1,
            13: 1,
            14: 1,
            15: 1,
            16: 0,
            17: 0,
            18: 0,
            19: 0,
            20: 0,
            "kill": 1
        }
    }

    def sort_teams(scoreboard: dict):
        # teams sorted by points. if points are equal - teams sorted by single match best score. if placements are equal - teams sorted by kills for 1 match
        teams = [scoreboard.keys()]
        for team_ind in range(len(scoreboard.keys())):
            for team_jnd in range(len(scoreboard.keys())):
                if([scoreboard[teams[team_ind]]["currentpts"] < scoreboard[teams[team_jnd]]]["currentpts"]):
                    temp = teams[team_ind]
                    teams[team_jnd] = teams[team_ind]
                    teams[team_ind] = temp
                elif(scoreboard[teams[team_ind]]["currentpts"] == scoreboard[teams[team_jnd]]["currentpts"]):
                    if(scoreboard[teams[team_ind]]["best_score"] < scoreboard[teams[team_jnd]]["best_score"]):
                        temp = teams[team_ind]
                        teams[team_jnd] = teams[team_ind]
                        teams[team_ind] = temp
                    elif(scoreboard[teams[team_ind]]["best_score"] == scoreboard[teams[team_jnd]]["best_score"]):
                        if(scoreboard[teams[team_ind]]["best_kills"] < scoreboard[teams[team_jnd]]["best_kills"]):
                            temp = teams[team_ind]
                            teams[team_jnd] = teams[team_ind]
                            teams[team_ind] = temp
        for i in range(len(teams)):
            scoreboard[teams[i]]["placement"] = i+1
        return scoreboard

    def add_match(self, s_match: Match):
        self.matches.append(s_match)
        results_per_team = s_match.get_results("team")
        for team_ind in range(len(self.teams)):
            if(team_ind not in self.scoreboard.keys()):
                self.scoreboard[team_ind] = {
                    "results": [],
                    "currentpts": 0,
                    "placement": 0,
                    "best_score": 0,
                    "best_kills": 0
                }
            self.scoreboard[team_ind]["results"].append(results_per_team[team_ind])
            match_score = self.points["ALGS"][results_per_team[team_ind]["placement"]] + (self.points["ALGS"]["kills"] * results_per_team[team_ind]['kills'])
            self.scoreboard[team_ind]["currentpts"] += match_score
            if (self.scoreboard[team_ind]["best_score"] < match_score):
                self.scoreboard[team_ind]["best_score"] = match_score
            if (self.scoreboard[team_ind]["best_kills"] < results_per_team[team_ind]['kills']):
                self.scoreboard[team_ind]["best_kills"] = results_per_team[team_ind]['kills']
        self.scoreboard = self.sort_teams(self.scoreboard)

    def remove_match(self, s_match: int):
        if(s_match > len(self.matches)):
            return False
        match = self.matches[s_match]
        results_per_team = s_match.get_results("team")
        for team_ind in range(len(self.teams)):
            if(team_ind not in self.scoreboard.keys()):
                self.scoreboard[team_ind] = {
                    "results": [],
                    "currentpts": 0,
                    "placement": 0,
                    "best_score": 0,
                    "best_kills": 0
                }
            self.scoreboard[team_ind]["results"].append(results_per_team[team_ind])
            match_score = self.points["ALGS"][results_per_team[team_ind]["placement"]] + (self.points["ALGS"]["kills"] * results_per_team[team_ind]['kills'])
            self.scoreboard[team_ind]["currentpts"] -= match_score
            if (self.scoreboard[team_ind]["best_score"] == match_score):
                self.scoreboard[team_ind]["best_score"] = match_score
            if (self.scoreboard[team_ind]["best_kills"] < results_per_team[team_ind]['kills']):
                self.scoreboard[team_ind]["best_kills"] = results_per_team[team_ind]['kills']
        
    def getTable(self):
        table = {
            "teams": self.teams,
            "scoreboard": self.scoreboard,
            "status": self.status
        }
        return table




class Stage:
    def __init__(self, s_name, s_format):
        self.name = s_name
        self.format = s_format
        self.groups = []


class Tournament:
    def _init_(self, s_name, s_format):
        self.name = s_name
        self.format = s_format
        self.stages = []

    def add_match(self, match: Match):
