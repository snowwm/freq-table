class RecordStore:
    def __init__(self):
        self.by_id = {}

    def count(self):
        return len(self.by_id)

    def add(self, record):
        self.by_id[record['url']] = record

    def get_sorted_by_freq(self):
        return sorted(self.by_id.values(), key=lambda r: float(r['frequency']))
