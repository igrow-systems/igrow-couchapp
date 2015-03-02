#!/usr/bin/python

# (c) Copyright Argusat Limited 2015
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
import json

class ParserState:
    reading_header = 1
    reading_supplier_name = 2
    reading_supplier_data = 3

    def __init__(self):
        self.current_state = ParserState.reading_header

    def parsed_header(self):
        if (self.current_state == ParserState.reading_header):
            self.current_state = ParserState.reading_supplier_name
        else:
            illegal_transition()

    def parsed_supplier_name(self):
        if (self.current_state == ParserState.reading_supplier_name):
            self.current_state = ParserState.reading_supplier_data
        else:
            illegal_transition()

    def parsed_supplier_data(self):
        if (self.current_state == ParserState.reading_supplier_data):
            self.current_state = ParserState.reading_supplier_name
        else:
            illegal_transition()

    def get_state(self):
        return self.current_state

    def illegal_transition(self):
        print "Illegal state transition in state: ", self.current_state



preamble_text = 'Vegetable Seed Order'
supplier_column = 0
current_state = ParserState()
seeds = []

with open(sys.argv[1], 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')

    for row in reader:

        if (current_state.get_state() == ParserState.reading_header):

            # skip the preamble
            if (row[0] == preamble_text):
                num_columns = len(row[0])
                continue

            fields = row;
            
            # test if we need to change state
            #if (sum(column == None for column in row) == num_columns):
            current_state.parsed_header()

        elif (current_state.get_state() == ParserState.reading_supplier_name):

            current_supplier = row[0]

            current_state.parsed_supplier_name()

        elif (current_state.get_state() == ParserState.reading_supplier_data):

            tuple_list = []
            for i in range(0,len(fields) - 1):
                if (i != supplier_column):
                    tuple_list.append((fields[i], row[i]))
                else:
                    tuple_list.append((fields[i], current_supplier))

            seed = dict(tuple_list)
            seeds.append(seed)

seedjson = json.dumps(seeds, separators=(',',':'), indent=4)

print seedjson


