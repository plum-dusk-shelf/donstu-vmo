class Time:
    def __init__(self, hours, minutes, seconds):
        time_in_seconds = hours * 3600 + minutes * 60 + seconds
        self.hours = time_in_seconds // 3600
        self.minutes = time_in_seconds % 3600 // 60
        self.seconds = time_in_seconds % 3600 % 60

    def __add__(self, other):
        new_seconds = self.seconds + other.seconds
        new_minutes = self.minutes + other.minutes
        new_hours = self.hours + other.hours

        return Time(new_hours, new_minutes, new_seconds)

    def __eq__(self, other):
        if self.hours == other.hours or self.minutes == other.minutes and self.seconds == other.seconds:
            return True
        return False

    def __le__(self, other):
        if self.hours < other.hours or self.minutes < other.minutes and self.seconds < other.seconds:
            return True
        return False

    def __gt__(self, other):
        if self.hours > other.hours or self.minutes > other.minutes and self.seconds > other.seconds:
            return True
        return False

    def print(self):
        print(self.hours, self.minutes, self.seconds)


time1 = Time(18, 52, 44)
time2 = Time(13, 12, 00)

time_sum = time1 + time2
time_eq = time1 == time2
time_le = time1 < time2
time_gr = time1 > time2

time_sum.print()
print('равны' * time_eq, 'первое позже' * time_le, 'второе позже' * time_gr, sep='')
