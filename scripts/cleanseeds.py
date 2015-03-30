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

    doc_id, rev = seedsdb.save(seed)
    print doc_id, ' ', rev

