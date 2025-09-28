class Stats:
    yes=0
    no=0
    total=0
    already_exists = 0
    
    @classmethod
    def display_stats(cls):
        return f"yes: {cls.yes} | no: {cls.no} | total: {cls.total} | already exists: {cls.already_exists} | not scrapable : {cls.total- (cls.yes + cls.no + cls.already_exists)}"

    @classmethod
    def reset_stats(cls):
        cls.yes = 0
        cls.no = 0
        cls.total = 0
        cls.already_exists = 0