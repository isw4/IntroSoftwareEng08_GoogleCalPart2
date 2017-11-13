import TimeSlot


free = TimeSlot('2013-05-12T09:00:00+00:00', '2013-05-12T17:00:00+00:00')
busy = TimeSlot('2013-05-12T08:00:00+00:00', '2013-05-12T08:59:00+00:00')
print("Busy before free: {} {} {} {}".format(not busy.completely_overlaps(free), busy.does_not_overlap(free), not busy.partially_overlaps(free), not busy.completely_within(free)))


free = TimeSlot('2013-05-12T09:00:00+00:00', '2013-05-12T17:00:00+00:00')
busy = TimeSlot('2013-05-12T08:00:00+00:00', '2013-05-12T09:00:00+00:00')
#print("Busy just overlapping free: {}".format(busy.does_not_overlap(free)))


free = TimeSlot('2013-05-12T09:00:00+00:00', '2013-05-12T17:00:00+00:00')
busy = TimeSlot('2013-05-12T08:00:00+00:00', '2013-05-12T08:59:00+00:00')
#print("Busy before free: {}".format(busy.does_not_overlap(free)))