"""Tools specifically for the ePodium dataset."""

import numpy as np
import copy
import os


def group_events_12(events):
    """
    Specific to the ePODIUM dataset.
    Reduces the number of distinctive events from 78 to 12 events.
    This is done by combining different pronounciations into the same event.
    """
    events_12 = copy.deepcopy(events)
    for i in range(len(events)):
        for newValue, minOld, maxOld in event_conversion_12:
            condition = np.logical_and(
                minOld <= events_12[i], events_12[i] <= maxOld)
            events_12[i] = np.where(condition, newValue, events_12[i])
    return events_12


event_dictionary = {
    'GiepM_FS': 1,
    'GiepM_S': 2,
    'GiepM_D': 3,
    'GiepS_FS': 4,
    'GiepS_S': 5,
    'GiepS_D': 6,
    'GopM_FS': 7,
    'GopM_S': 8,
    'GopM_D': 9,
    'GopS_FS': 10,
    'GopS_S': 11,
    'GopS_D': 12,
}

event_conversion_12 = [
    [1, 1, 12],
    [2, 13, 24],
    [3, 25, 36],
    [4, 101, 101],
    [5, 102, 102],
    [6, 103, 103],
    [7, 37, 48],
    [8, 49, 60],
    [9, 61, 72],
    [10, 104, 104],
    [11, 105, 105],
    [12, 106, 106]
]

channel_names = ['Fp1', 'AF3', 'F7', 'F3', 'FC1', 'FC5',
               'T7', 'C3', 'CP1', 'CP5', 'P7', 'P3',
               'Pz', 'PO3', 'O1', 'Oz', 'O2', 'PO4',
               'P4', 'P8', 'CP6', 'CP2', 'C4', 'T8',
               'FC6', 'FC2', 'F4', 'F8', 'AF4', 'Fp2',
               'Fz', 'Cz']

channels_mastoid = ['EXG1', 'EXG2']

channels_drop = ['EXG3', 'EXG4', 'EXG5', 'EXG6', 'EXG7', 'EXG8', 'Status']

        