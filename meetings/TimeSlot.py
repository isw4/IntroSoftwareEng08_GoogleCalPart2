import arrow

class TimeSlot:

	 def __init__(self, summary, begin_datetime, end_datetime):
	 	self.summary        = summary
	 	self.begin_datetime = begin_datetime
	 	self.end_datetime   = end_datetime

	 def blockout(self, busytimeslot):
		"""
		Args:
			busytimeslot:	TimeSlot object, representing a busy time

		Returns:
			A list of either 0, 1, or 2 TimeSlot objects, representing
			free times
		"""

		if busytimeslot.completely_overlaps(self):
			return []
		if busytimeslot.does_not_overlap(self):
			return [ self ]
		if busytimeslot.partially_overlaps(self):
			return shrink()
		if busytimeslot.completely_within(self):
			return split()
		
		print("This case shouldn't happen")
		assert False


	#################################################################
	#
	# Functions comparing free to busy times
	#
	#################################################################

	def completely_overlaps(self, other):
		"""
		Tests to see if the self TimeSlot completely overlaps with
		the other TimeSlot.

		Args:
			self:	TimeSlot object
			other:	TimeSlot object

		Returns:
			True if self completely overlaps other. ie:
						self	other
				06:00	[]
				07:00	[]		[]
				08:00	[]		[]
				09:00	[]		[]
				10:00	[]
			False otherwise
		"""
		return ( arrow.get(self.begin_datetime) <= arrow.get(other.begin_datetime)
		         and arrow.get(self.end_datetime) >= arrow.get(other.end_datetime) )


	def does_not_overlap(self, other):
		"""
		Tests to see if the self TimeSlot does not overlap
		the other TimeSlot.

		Args:
			self:	TimeSlot object
			other:	TimeSlot object

		Returns:
			True if self does not overlap other. ie:
						self	other
				06:00	[]		
				07:00			
				08:00			[]
				09:00			[]
				10:00			[]
			False otherwise
		"""
		if ( arrow.get(self.begin_datetime) < arrow.get(other.begin_datetime)
		     and arrow.get(self.end_datetime) < arrow.get(other.begin_datetime) ):
			overlaps = False
		
		elif ( arrow.get(self.begin_datetime) > arrow.get(other.end_datetime)
		       and arrow.get(self.end_datetime) > arrow.get(other.end_datetime) ):
			overlaps = False

		else:
			overlaps = True

		return overlaps


	def partially_overlaps(self, other):
		"""
		Tests to see if the self TimeSlot partially overlaps
		the other TimeSlot.

		Args:
			self:	TimeSlot object
			other:	TimeSlot object

		Returns:
			True if self partially overlaps other. ie:
						self	other
				06:00	[]		
				07:00	[]		
				08:00	[]		[]
				09:00			[]
				10:00			[]
			Also true:
						self	other
				06:00			[]
				07:00			[]
				08:00	[]		[]
				09:00	[]		[]
				10:00	[]		[]
			False otherwise
		"""
		if ( arrow.get(self.begin_datetime) <= arrow.get(other.begin_datetime)
		     and arrow.get(self.end_datetime) < arrow.get(other.end_datetime) ):
			overlaps = True
		
		elif ( arrow.get(self.begin_datetime) > arrow.get(other.begin_datetime)
		       and arrow.get(self.end_datetime) >= arrow.get(other.end_datetime) ):
			overlaps = True

		else:
			overlaps = False

		return overlaps


	def completely_within(self, other):
		"""
		Tests to see if the self TimeSlot is completely within
		the other TimeSlot.

		Args:
			self:	TimeSlot object
			other:	TimeSlot object

		Returns:
			True if self completely overlaps other. ie:
						self	other
				06:00			[]
				07:00	[]		[]
				08:00	[]		[]
				09:00	[]		[]
				10:00			[]
			False otherwise. ie:
						self	other
				06:00	[]		[]
				07:00	[]		[]
				08:00	[]		[]
				09:00	[]		[]
				10:00			[]
		"""
		return ( arrow.get(self.begin_datetime) > arrow.get(other.begin_datetime)
		         and arrow.get(self.end_datetime) < arrow.get(other.end_datetime) )

	