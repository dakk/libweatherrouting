import weatherrouting

class mock_point_validity:
    def __init__(self, track, factor=4):
        self.mean_point = ((track[0][1]+track[1][1])/2, (track[0][0]+track[1][0])/2)
        self.mean_island = weatherrouting.utils.pointDistance(*(track[0]+track[1]))/factor

    def point_validity(self, y, x):
        if weatherrouting.utils.pointDistance(x,y,*(self.mean_point)) < self.mean_island:
            return False
        else:
            return True

    def line_validity(self, y1, x1, y2, x2):
        if weatherrouting.utils.pointDistance(x1,y2,*(self.mean_point)) < self.mean_island:
            return False
        else:
            return True