"""
This test module tests the functions necessary to return the instances that
fall within a certain time range for each date in a certain date range.
"""

import arrow
from from_gcal import really_between_times

#
# Constants:
# Defines the begin and end time of the queried time range per day
# 	BEGIN_TIME:	9.30 am
#	END_TIME:   6.30 pm
#
BEGIN_TIME = '2000-01-01T09:30:00+00:00'
END_TIME   = '2000-01-01T18:30:00+00:00'

def test_samed_before():
	print("Instance on same day, before time range")
	instance = {
		"start" : { "dateTime" : '2013-05-12T03:30:00+00:00' },
		"end"   : { "dateTime" : '2013-05-12T04:30:00+00:00' }
	}
	assert really_between_times(instance, BEGIN_TIME, END_TIME) == False


def test_samed_begin_overlap():
	print("Instance on same day, partial front overlap of time range")
	instance = {
		"start" : { "dateTime" : '2013-05-12T09:00:00+00:00' },
		"end"   : { "dateTime" : '2013-05-12T10:30:00+00:00' }
	}
	assert really_between_times(instance, BEGIN_TIME, END_TIME) == True


def test_samed_completely_within():
	print("Instance on same day, completely within time range")
	instance = {
		"start" : { "dateTime" : '2013-05-12T10:30:00+00:00' },
		"end"   : { "dateTime" : '2013-05-12T11:30:00+00:00' }
	}
	assert really_between_times(instance, BEGIN_TIME, END_TIME) == True


def test_samed_complete_overlap():
	print("Instance on same day, completely overlapping time range")
	instance = {
		"start" : { "dateTime" : '2013-05-12T08:30:00+00:00' },
		"end"   : { "dateTime" : '2013-05-12T20:30:00+00:00' }
	}
	assert really_between_times(instance, BEGIN_TIME, END_TIME) == True


def test_samed_end_overlap():
	print("Instance on same day, partial back overlap of time range")
	instance = {
		"start" : { "dateTime" : '2013-05-12T17:30:00+00:00' },
		"end"   : { "dateTime" : '2013-05-12T19:30:00+00:00' }
	}
	assert really_between_times(instance, BEGIN_TIME, END_TIME) == True

def test_samed_after():
	print("Instance on same day, after time range")
	instance = {
		"start" : { "dateTime" : '2013-05-12T22:30:00+00:00' },
		"end"   : { "dateTime" : '2013-05-12T23:30:00+00:00' }
	}
	assert really_between_times(instance, BEGIN_TIME, END_TIME) == True


def test_diffd_no_overlap():
	print("Instance on different days, not overlapping time range")
	instance = {
		"start" : { "dateTime" : '2013-05-12T22:30:00+00:00' },
		"end"   : { "dateTime" : '2013-05-13T04:30:00+00:00' }
	}
	assert really_between_times(instance, BEGIN_TIME, END_TIME) == False


def test_diffd_begin_overlap():
	print("Instance on different days, partially overlapping time range")
	instance = {
		"start" : { "dateTime" : '2013-05-12T22:30:00+00:00' },
		"end"   : { "dateTime" : '2013-05-13T11:30:00+00:00' }
	}
	assert really_between_times(instance, BEGIN_TIME, END_TIME) == True


def test_diffd_complete_overlap():
	print("Instance on different days, completely overlapping time range")
	instance = {
		"start" : { "dateTime" : '2013-05-12T03:30:00+00:00' },
		"end"   : { "dateTime" : '2013-05-15T04:30:00+00:00' }
	}
	assert really_between_times(instance, BEGIN_TIME, END_TIME) == True