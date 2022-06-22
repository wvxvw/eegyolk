# testing eegyolk

from posixpath import splitext
from itertools import islice
import unittest
import os
import glob
import sys
from tempfile import TemporaryDirectory
import mne

sys.path.insert(0, os.getcwd())

from eegyolk.display_helper import make_ordinal
from eegyolk.helper_functions import band_pass_filter
from eegyolk.helper_functions import hash_it_up_right_all
from eegyolk.helper_functions import filter_eeg_raw
from eegyolk.helper_functions import load_metadata # (filename, path_metadata, path_output, make_excel_files=True, make_csv_files=True)

from eegyolk.initialization_functions import load_dataset
# from eegyolk.initialization_functions import load_metadata
from eegyolk.initialization_functions import load_events
from eegyolk.initialization_functions import save_events
# from eegyolk.initialization_functions import print_event_info
from eegyolk.initialization_functions import caller_save_events
from eegyolk.initialization_functions import generator_load_dataset

# sample_eeg_cnt = 'tests/sample/640-464-17m-jc-mmn36.cnt' # one file in the tests folder to have a .cnt fileed for now
# sample_eeg_cnt_read = mne.io.read_raw_cnt(sample_eeg_cnt, preload=True)
sample_eeg_bdf = os.path.join('../epod_data_not_pushed','not_zip','121to130','121to130','121','121a','121a'+'.bdf')
path_eeg = os.path.join('../epod_data_not_pushed','not_zip')
sample_eeg_bdf_read = mne.io.read_raw_bdf(sample_eeg_bdf, preload=True)
sample_metadata = os.path.join('../epod_data_not_pushed','metadata','cdi.txt')
# path_metadata = os.path.join('../epod_data_not_pushed','metadata')
event_marker_folder = os.path.join('../epod_data_not_pushed','not_zip', 'event_markers') # check with nadine on this folder
sample_eeg_list = ['101a']

class TestDisplayHelperMethods(unittest.TestCase):

    def test_make_ordinal(self):
        self.assertEqual(make_ordinal(5), '5th')


class TestFilteringMethods(unittest.TestCase):

    def test_band_pass_filter(self):
        sample_eeg_filtered = band_pass_filter(sample_eeg_bdf_read, 0, 10)
        self.assertEqual(
            (sample_eeg_filtered.info['lowpass']),
            10,
        )
    def test_filter_raw(self):
        sample_eeg_raw_filtered = filter_eeg_raw(sample_eeg_bdf_read, 0, 10,50,  ['EXG1', 'EXG2'])
        self.assertEqual(
            (sample_eeg_raw_filtered.info['lowpass']),
            10,
        )



class TestHashMethods(unittest.TestCase):

    def test_hash_it_up_right_all(self):
        tempfile1 = 'tempfile1.cnt'
        tempfile2 = 'tempfile2.cnt'
        with TemporaryDirectory() as td:
            with open(os.path.join(td, tempfile1), 'w') as tf:
                tf.write('string')
            with open(os.path.join(td, tempfile2), 'w') as tf:
                tf.write('string')
            self.assertTrue(hash_it_up_right_all(td, '.cnt').equals(hash_it_up_right_all(td, '.cnt')))

class TestLoadMethods(unittest.TestCase):

   
    def test_load_metadata(self):
        filename = os.path.splitext(sample_metadata)[0]
        loaded_metadata = load_metadata(
            filename,
            sys.path[0],
            sys.path[0],
            make_excel_files=False,
            make_csv_files=False,
        )
        self.assertEqual(len(loaded_metadata), 143)

    def test_load_events(self):
        loaded_event_markers = load_events(event_marker_folder, sample_eeg_list)
        self.assertEqual(len(loaded_event_markers), 1)
    
    def test_call_event_markers(self):
        # temporary directory
        expected = 10
        with TemporaryDirectory() as td:
            caller_save_events(td, islice(generator_load_dataset(path_eeg), 10))
            actual = sum(1 for txt in glob.glob(os.path.join(td,'*.txt')))
        # compare number files generated,to expected which we stop at 10 with 
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()

