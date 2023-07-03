# Copyright 2020 The `Kumar Nityan Suman` (https://github.com/nityansuman/).
# All Rights Reserved.
#
#
#                     GNU GENERAL PUBLIC LICENSE
#                        Version 3, 29 June 2007
#  Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
#  Everyone is permitted to copy and distribute verbatim copies
#  of this license document, but changing it is not allowed.
# ==============================================================================

import csv
import logging
import os

import numpy as np
import pandas as pd
import sqlite3


def backup(session: list) -> bool:
	"""Method to backup details for the current session.

	Args:
		session (list): Session metadata container.

	Returns:
		bool: Status flag indicatig successful backup of session metadata.
	"""
	# Process session information
	username = "_".join([x.upper() for x in session["username"].split()])
	subject_name = session["subject_name"].strip().upper()
	subject_id = session["subject_id"].strip()
	test_type = ["Objective" if session["test_id"] == "0" else "Subjective"][0]
	test_id = session["test_id"]
	timestamp = session["date"]
	status = False

	# Construct login data
	row = [
		timestamp,
		username,
		subject_name,
		subject_id,
		test_type,
		test_id,
		session["score"],
		session["result"]
	]

	# Push session metadata to a central repo
	filepath = session["database_path"]
	if os.path.isfile(filepath):
		try:
			with open(filepath, mode="a") as fp:
				fp_writer = csv.writer(fp)
				fp_writer.writerow(row)
				status = True
		except Exception as e:
			logging.exception("Exception raised at `backup`.", exc_info=True)
	else:
		print("Database placeholder nott found!")
	return status


def relative_ranking(session: list) -> tuple:
	"""Method to compute relative ranking for a particular user response.

	Args:
		session (list): Session metadata container.

	Returns:
		tuple: Tuple with max, min and mean score.
	"""
	min_scope, max_score = 0.0, 100.0
	mean_score = None

	def rounder(value, decimals=2):
		return np.round(value, decimals=decimals)

	# Load session meta to central repository
	directory = os.path.join(str(os.getcwd()), "database")
	session["database_path"] = os.path.join(str(os.getcwd()), "database", "database.db")
	conn = sqlite3.connect(session["database_path"])
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	cur.execute("select MAX(score) from students where subject_id={} and test_id={}".format(int(session["subject_id"]), int(session["test_id"])))
	max_score = float(cur.fetchone()[0])

	cur.execute("select MIN(score) from students where subject_id={} and test_id={}".format(int(session["subject_id"]), int(session["test_id"])))
	min_score = float(cur.fetchone()[0])

	cur.execute("select AVG(score) from students where subject_id={} and test_id={}".format(int(session["subject_id"]), int(session["test_id"])))
	mean_score = float(cur.fetchone()[0])

	max_score = rounder(max_score, decimals=2)
	min_score = rounder(min_score, decimals=2)
	mean_score = rounder(mean_score, decimals=2)
	return (max_score, min_score, mean_score)
