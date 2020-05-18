class Bar:
    def __init__(self, bopen, bhigh, blow, bclose, volume=None, wap=None, time=None):
        self.open = bopen
        self.high = bhigh
        self.low = blow
        self.close = bclose
        self.volume = volume
        self.wap = wap
        self.time = time

    @staticmethod
    def alphadict_to_bar(input_dict, key_time):
        return Bar(input_dict['1. open']
                   , input_dict['2. high']
                   , input_dict['3. low']
                   , input_dict['4. close']
                   , input_dict['5. volume']
                   , time=key_time)

    def __str__(self):
        return '{' + str(self.time) + '|O:' + str(self.open) + ' H:' + str(self.high) +\
               ' L:' + str(self.low) + ' C:' + str(self.close) + '} (V:' + str(self.volume) + ')'
