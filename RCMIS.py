class RCMIS:
    def __init__(self):
        self.users = {"admin": "password"}
        self.players = {}
        self.injuries = {}
        self.rehab_status = {}
        self.medical_reports = {}

    def add_player(self, player_id, name, dob, age, position):
        player = {
            "name": name,
            "dob": dob,
            "age": age,
            "position": position
        }
        self.players[player_id] = player
    def log_injury(self, player_id, injury_type, body_part, severity):
        if player_id not in self.injuries:
            self.injuries[player_id] = []
        self.injuries[player_id].append({
            "injury_type": injury_type,
            "body_part": body_part,
            "severity": severity
        }) 
           
    def generate_medical_report(self, player_id):
        if player_id not in self.players:
            return None

        player = self.players[player_id]
        injuries = self.injuries.get(player_id, [])
        rehabs = self.rehab_status.get(player_id, [])

        return {
            "player": [
                player["name"],
                player["dob"],
                player["age"],
                player["position"]
            ],
            "injuries": injuries,
            "rehabs": rehabs
        }