#!/usr/bin/env python

import sys
import os
import csv


class GxpMakeDB(object):
    """Wrapper module to provide an access to the GXPmake CSV.
    """

    def _get_db_filename(self):
        return self._db_filename

    db_filename = property(_get_db_filename)

    def _get_csvreader(self):
        return self._csvreader

    csvreader = property(_get_csvreader)

    def __init__(self, db_filename):
        """Initialize an instance and create a reader object.
        """
        self._db_filename = db_filename
        self._csvreader = csv.DictReader(open(self._db_filename, "rb"),
                                         delimiter="\t",
                                         quoting=csv.QUOTE_NONE)

    def main(self, ):
        """Main function for testing. Only dumps the contents of the CSV.
        """
        print "Fields"
        print self.csvreader.fieldnames
        print "Contents"
        for row in self.csvreader:
            if row["work_idx"] == "#":  # Skip Comment line
                continue
            sys.stdout.write(" ".join(row.values()))
            sys.stdout.write("\n")
        print "There were %d lines." % (self.csvreader.line_num)


def testfile():
    """Returns a path to the sample database CSV file.
    """
    #data_path = "../sample/data/montage_data2_work_db.csv"
    data_path = "../sample/data/montage_data2_work_txt.csv"
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        data_path)


def main():
    """Sample processing sample CSV file.
    """
    gmdb = GxpMakeDB(testfile())
    gmdb.main()


if __name__ == '__main__':
    main()
