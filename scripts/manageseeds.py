#!/usr/local/Cellar/python/2.7.9/Frameworks/Python.framework/Versions/2.7/bin/python

# (c) Copyright 2015 Argusat Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import csv
import couchdb
import argparse
import time
import getpass

class ParserState:
    reading_header = 1
    reading_supplier_name = 2
    reading_supplier_data = 3

    def __init__(self):
        self.current_state = ParserState.reading_header

    def parsed_header(self):
        if (self.current_state == ParserState.reading_header):
            print "Transition ", self.current_state, " -> ", ParserState.reading_supplier_name
            self.current_state = ParserState.reading_supplier_name
        else:
            illegal_transition()

    def parsed_supplier_name(self):
        if (self.current_state == ParserState.reading_supplier_name):
            print "Transition ", self.current_state, " -> ", ParserState.reading_supplier_data
            self.current_state = ParserState.reading_supplier_data
        else:
            illegal_transition()

    def parsed_supplier_data(self):
        if (self.current_state == ParserState.reading_supplier_data):
            print "Transition ", self.current_state, " -> ", ParserState.reading_supplier_name
            self.current_state = ParserState.reading_supplier_name
        else:
            illegal_transition()

    def get_state(self):
        return self.current_state

    def illegal_transition(self):
        print "Illegal state transition in state: ", self.current_state


couchdb_port = 5984
db_name = 'igrow'

preamble_text = 'Vegetable Seed Order'
supplier_column = 0
total_column = 8
total_text = 'Total:'

current_state = ParserState()
seeds = []
preamble_read = False
num_columns = -1

parser = argparse.ArgumentParser(description='Manage the iGrow seeds database')
parser.add_argument('--deletedb', dest='deletedb', action='store_true',
                   help='deletes the existing seed database before any other action')
parser.add_argument('--dryrun', dest='dryrun', action='store_true',
                   help='do not modify database')
parser.add_argument('--input', dest='ifile', type=str, nargs=1,
                   help='CSV input file')
parser.add_argument('--user', dest='user', type=str, default='admin', 
                    nargs='?', help='admin user')
parser.add_argument('--host', dest='couchdb_hostname', type=str, default='localhost',
                    nargs='?', help='CouchDB hostname')

args = parser.parse_args()

if (not args.dryrun):
    password = getpass.getpass()
    couch = couchdb.Server('http://{0}:{1}@{2}:{3}/'.format(args.user, password, args.couchdb_hostname, couchdb_port))

    if (args.deletedb):
        try:
            couch.delete(db_name)
            seedsdb = couch.create(db_name)
        except couchdb.http.ResourceNotFound:
            pass
    else:
        try:
            seedsdb = couch[db_name]
        except couchdb.http.ResourceNotFound:
            seedsdb = couch.create(db_name)


with open(args.ifile[0], 'rb') as ifile:
    reader = csv.reader(ifile, delimiter=',')

    for row in reader:
        # skip the preamble
        if (not preamble_read):
            if (row[0] == preamble_text):
                preamble_read = True
                continue

        # set the number of columns to the
        # length of the column label row
        if (num_columns == -1):
            num_columns = len(row)
            print num_columns, ' columns.'

        # catch all blank rows
        num_blank_cols = sum(column == '' for column in row)
        if (num_blank_cols >= num_columns):
            continue

        print num_blank_cols, ', '.join(row)

        if (current_state.get_state() == ParserState.reading_header):

            fields = row;

            fields = [field.lower() for field in fields]
            fields = [str(field).replace(' ', '_') for field in fields]

            current_state.parsed_header()

        elif (current_state.get_state() == ParserState.reading_supplier_name):

            current_supplier = row[0]
            current_state.parsed_supplier_name()

        elif (current_state.get_state() == ParserState.reading_supplier_data):

            if (row[total_column] == total_text):
                current_state.parsed_supplier_data()
                continue

            tuple_list = []
            for i in range(0,len(fields) - 1):
                if (i != supplier_column):
                    tuple_list.append((fields[i], row[i]))
                else:
                    tuple_list.append((fields[i], current_supplier))

            localtime   = time.localtime()
            timeString  = time.strftime("%Y/%m/%d %H:%M:%S ", localtime)

            # is DST in effect?
            timezone    = -(time.altzone if localtime.tm_isdst else time.timezone)
#            timeString += "Z" if timezone == 0 else "+" if timezone > 0 else "-"
            timeString += "+" if timezone >= 0 else "-"
            timeString += time.strftime("%H%M'", time.gmtime(abs(timezone)))
            # add a document type of 'seed' for sanity later
            tuple_list.append(('type', 'seed'))
            tuple_list.append(('created', timeString))
            tuple_list.append(('modified', timeString))
            tuple_list.append(('user', 'system'))
            tuple_list.append(('variety_url','http://vegetalis.co.uk/images/made/images/uploads/Tomato_Rambling_Red_Stripe_10046117_360_360_c1_c_c_0_0.jpg'))
            seed = dict(tuple_list)
            seeds.append(seed)
            print seed
            if (not args.dryrun):
                doc_id, rev = seedsdb.save(seed)
                print doc_id, ' ', rev

