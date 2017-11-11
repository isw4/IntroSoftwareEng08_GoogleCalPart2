"""
Module that requests information from Google Calendars. All the main functions require a valid google calendar service.
Get the user credentials, build the service, and then pass the service into the functions along with any other required
parameters.

Main Functions:
list_calendars						: lists all of a user calendars
list_instances_between_datetimes	: lists all event instances from selected calendars that are not transparent,
									  and between a start and end time of EACH date within a date range

Helper Functions:
cal_sort_key
merge_date_time
really_between_times
"""

import arrow

#############################
#
#  Main Functions
#
#############################

def list_calendars(service):
	"""
	Given a google 'service' object, return a list of
	calendars.  Each calendar is represented by a dict.
	The returned list is sorted to have
	the primary calendar first, and selected (that is, displayed in
	Google Calendars web app) calendars before unselected calendars.
	"""
	print("Listing calendars from Google Calendar")  
	calendar_list = service.calendarList().list().execute()["items"]
	result = []
	for cal in calendar_list:
		# Optional binary attributes with False as default
		selected = ("selected" in cal) and cal["selected"]
		primary = ("primary" in cal) and cal["primary"]

		result.append(
		  { "kind": cal["kind"],
			"id": cal["id"],
			"summary": cal["summary"],
			"selected": selected,
			"primary": primary,
			"checked": ""
			})
	
	return sorted(result, key=cal_sort_key)


def list_instances_btwn_times_in_dates(service, selected_cal, begin_date, end_date, begin_time, end_time):
	"""
	Given a google 'service' object and a list of calendar IDs, returns a list of 
	event instances that fall between the given time range on each date within the 
	given date range.
	
	For example, list_instances_btwn_times_in_dates() with the given parameters:
	begin_date: 2013-05-12T00:00:00+00:00
	end_date:   2013-05-15T00:00:00+00:00
	begin_time: 2000-01-01T09:00:00+00:00
	end_time:   2000-01-01T18:00:00+00:00

	Returns all event instances that overlap with the following time periods:
	2013-05-12T09:00:00+00:00 to 2013-05-12T18:00:00+00:00
	2013-05-13T09:00:00+00:00 to 2013-05-13T18:00:00+00:00
	2013-05-14T09:00:00+00:00 to 2013-05-14T18:00:00+00:00
	2013-05-15T09:00:00+00:00 to 2013-05-15T18:00:00+00:00
	"""
	
	begin_datetime = merge_date_time(begin_date, begin_time)	# An isoformatted time string of the earliest date and the start time
	end_datetime   = merge_date_time(end_date,   end_time)		# An isoformatted time string of the latest date and the end time
	print("Getting Google Calendar event instances from {} to {}".format(begin_datetime, end_datetime))

	# There may be events that recur. The first loop identifies all the unique "types" of events
	# and then the second loop finds all instances of the event, nonrecurring and recurring
	pre_events = []
	for cal_id in selected_cal:
		events = service.events().list(calendarId=cal_id).execute()
		print("Events found: {}".format(events))
		for event in events['items']:
			# Ignores transparent events
			if "transparency" in event and event["transparency"] == "transparent":
				continue

			# Identifies if the event recurs
			if "recurrence" in event:
				recurs = True
			else:
				recurs = False

			# Append each event to list
			pre_events.append({
				"event_id": event['id'],
				"cal_id": cal_id,
				"recurs": recurs
				})

	# This is the second loop, getting all instances that Google gives us, and then eliminating those
	# that are not really within the time range on each day
	result = []
	for pre_e in pre_events:
		if pre_e['recurs']:
			# Need to get all event instances for a recurring event, within a certain date-time range
			instances = service.events().instances(calendarId=pre_e['cal_id'], eventId=pre_e['event_id'],
												   timeMin=begin_datetime, timeMax=end_datetime).execute()
			for instance in instances['items']:
				if really_between_times(instance, begin_time, end_time):
					result.append({
						"event_id": instance['id'],
						"summary": instance['summary'],
						"begin_datetime": instance['start']['dateTime'],
						"end_datetime": instance['end']['dateTime']
						})
		else:
			# For non-recurring events, there is only one instance
			instance = service.events().get(calendarId=pre_e['cal_id'], eventId=pre_e['event_id']).execute()
			if really_between_times(instance, begin_time, end_time):
				result.append({
					"event_id": instance['id'],
					"summary": instance['summary'],
					"begin_datetime": instance['start']['dateTime'],
					"end_datetime": instance['end']['dateTime']
					})
		
	print("All instances found: {}".format(result))
	return result


#############################
#
#  Helper Functions
#
#############################


def cal_sort_key( cal ):
	"""
	Sort key for the list of calendars:  primary calendar first,
	then other selected calendars, then unselected calendars.
	(" " sorts before "X", and tuples are compared piecewise)
	"""
	if cal["selected"]:
	   selected_key = " "
	else:
	   selected_key = "X"
	if cal["primary"]:
	   primary_key = " "
	else:
	   primary_key = "X"
	return (primary_key, selected_key, cal["summary"])


def really_between_times(instance, begin_time, end_time):
	"""
	Checks whether the instance is a busy time that falls within the queried time range
	of each date in the date range.
	"""

	# Case where the user searches for busy times throughout the whole day(24h)
	begin = arrow.get(begin_time).format("HH:mm")
	end   = arrow.get(end_time).format("HH:mm")
	if begin == end:
		print("Begin and end time is the same. All instances will be busy times")
		return True

	# Normal case where end_time > begin_time. First lists all available time ranges on
	# the entire date range upon which the instance exists. Then tests whether the 
	# instance overlaps with any of the time ranges.
	avails = list_availabilities_btwn_dates(instance['start']['dateTime'], instance['end']['dateTime'], begin_time, end_time)
	instance_begin = arrow.get(instance['start']['dateTime'])
	instance_end   = arrow.get(instance['end']['dateTime'])
	for avail in avails:
		bt = arrow.get(avail['bt'])
		et = arrow.get(avail['et'])
		if (instance_begin < bt and instance_end < bt) or (instance_begin > et and instance_end > et):
			continue
		else:
			print("{} is a busy time within {} and {} on {}")
			return True
	
	print("Event instance not in available query")
	return False


def merge_date_time(isodate, isotime):
	"""
	Merging the date and timezone from isodate with the time from isotime
	"""
	date_arr = arrow.get(isodate)
	time_arr = arrow.get(isotime)
	#app.logger.debug("Merging date: {} and time: {}".format(date_arr.isoformat(), time_arr.isoformat()))
	date_arr = date_arr.replace(hour=time_arr.hour,
								minute=time_arr.minute)
	#app.logger.debug("Merged datetime is {}".format(date_arr.isoformat()))
	return date_arr.isoformat()


def list_availabilities_btwn_dates(iso_begin_date, iso_end_date, iso_begin_time, iso_end_time):
	"""
	Returns a list of dicts, each containing the begin and end time for a single day. The
	list contains a number of dicts equal to the number of days from the begin to end date,
	inclusive

	Eg)
	iso_begin_date: 2013-05-12T00:00:00+00:00
	iso_end_date:   2013-05-15T00:00:00+00:00
	iso_begin_time: 2000-01-01T09:00:00+00:00
	iso_end_time:   2000-01-01T18:00:00+00:00

	Returns the list: [
		{ 'bt': '2013-05-12T09:00:00+00:00' , 'et': '2013-05-12T18:00:00+00:00' },
		{ 'bt': '2013-05-13T09:00:00+00:00' , 'et': '2013-05-13T18:00:00+00:00' },
		{ 'bt': '2013-05-14T09:00:00+00:00' , 'et': '2013-05-14T18:00:00+00:00' },
		{ 'bt': '2013-05-15T09:00:00+00:00' , 'et': '2013-05-15T18:00:00+00:00' }
	]
	"""

	avails = [{
		'bt': merge_date_time(iso_begin_date, iso_begin_time),
		'et': merge_date_time(iso_begin_date, iso_end_time)
		}]
	curr_arr = arrow.get(iso_begin_date)
	while curr_arr.format("YYYY-MM-DD") != arrow.get(iso_end_date).format("YYYY-MM-DD"):
		curr_arr = curr_arr.shift(days=+1)
		avails.append({
			'bt': merge_date_time(curr_arr.isoformat(), iso_begin_time),
			'et': merge_date_time(curr_arr.isoformat(), iso_end_time)
			})
	return avails