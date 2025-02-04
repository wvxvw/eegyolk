import mne
import pandas as pd
import numpy as np
import os
import glob

import PATH

channels_ddp_30 = ['O2', 'O1', 'OZ', 'PZ', 'P4', 'CP4', 'P8', 'C4', 'TP8', 'T8', 'P7', 
               'P3', 'CP3', 'CPZ', 'CZ', 'FC4', 'FT8', 'TP7', 'C3', 'FCZ', 'FZ', 
               'F4', 'F8', 'T7', 'FT7', 'FC3', 'F3', 'FP2', 'F7', 'FP1']

channels_ddp_62 = ['O2', 'O1', 'OZ', 'PZ', 'P4', 'CP4', 'P8', 'C4', 'TP8', 'T8', 'P7', 
               'P3', 'CP3', 'CPZ', 'CZ', 'FC4', 'FT8', 'TP7', 'C3', 'FCZ', 'FZ', 
               'F4', 'F8', 'T7', 'FT7', 'FC3', 'F3', 'FP2', 'F7', 'FP1', 'AFZ', 'PO3', 
               'P1', 'POZ', 'P2', 'PO4', 'CP2', 'P6', 'M1', 'CP6', 'C6', 'PO8', 'PO7', 
               'P5', 'CP5', 'CP1', 'C1', 'C2', 'FC2', 'FC6', 'C5', 'FC1', 'F2', 'F6', 
               'FC5', 'F1', 'AF4', 'AF8', 'F5', 'AF7', 'AF3', 'FPZ']

def create_labels(PATH, filename):

    # 5 months is excluded from analysis, since the data is too messy (see Bjorn's thesis)
    age_groups = [11, 17, 23, 29, 35, 41, 47]

    df_list = []
    # Store cnt file info
    for age_group in age_groups:
        folder = os.path.join(PATH, str(age_group) + "mnd mmn")
        code_list = []
        path_list = []     
        file_list = []

        for file in sorted(os.listdir(folder)):
            if file.endswith(".cnt"):  
                code_list.append(int(file[0:3])) # First 3 numbers of file is participant code
                path_list.append(os.path.join(folder, file))
                file_list.append(file)

        df = pd.DataFrame({"code": code_list, "path": path_list, "file": file_list})
        df['age_group'] = age_group
        df_list.append(df)

    cnt_df = pd.concat(df_list)  

    # Set correct age labels for each file
    PATH_metadata = os.path.join(PATH , 'metadata')
    df_list = []
    for age_group in age_groups:
        age_file = "ages_" + str(age_group) + "mnths.txt"
        df = pd.read_csv(os.path.join(PATH_metadata , 'ages', age_file), sep = "\t")
        df['age_group'] = age_group
        df_list.append(df)

    age_df = pd.concat(df_list)
    age_df = age_df.drop(columns=['age_months', 'age_years']) # age_days is sufficient
    merged_df = pd.merge(cnt_df, age_df, how = 'left', on = ['age_group', 'code'])
    merged_df['age_days'].fillna(merged_df['age_group'] * 30, inplace = True)
    merged_df.to_excel(os.path.join(PATH, filename), index = True)
    
def create_labels_processed(PATH_data, PATH_labels, labels):
    # Storing each column seperately, before concatinating as DataFrame
    code_list = []
    path_list = []
    file_list = []
    age_group_list = []
    age_days_list = []

    files_path = glob.glob(PATH_data + '/*.npy')
    for file_path in files_path:
        filename = os.path.basename(os.path.splitext(file_path)[0])  
        data = labels.loc[labels['file'] == filename]
        code_list.append(data['code'].values[0] )    
        path_list.append(file_path)
        file_list.append(filename)
        age_group_list.append(data['age_group'].values[0])
        age_days_list.append(data['age_days'].values[0])

    labels_processed = pd.DataFrame({"code": code_list, 'path': path_list, "file": file_list, 
                                        'age_group': age_group_list, 'age_days': age_days_list})
    labels_processed.to_excel(PATH_labels, index = True)
    return labels_processed

    
    
    
    
    
    
    
    
    
    # BJORN: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    
    
def read_cnt_file(file,
              label_group,
              event_idx = [2, 3, 4, 5, 12, 13, 14, 15],
              channel_set = "30",
              tmin = -0.2,
              tmax = 0.8,
              lpass = 0.5, 
              hpass = 40, 
              threshold = 5, 
              max_bad_fraction = 0.2,
              max_bad_channels = 2):
    """ Function to read cnt file. Run bandpass filter. 
    Then detect and correct/remove bad channels and bad epochs.
    Store resulting epochs as arrays.
    
    Args:
    --------
    file: str
        Name of file to import.
    label_group: int
        Unique ID of specific group (must be >0).
    channel_set: str
        Select among pre-defined channel sets. Here: "30" or "62"
    """
    
    if channel_set == "30":
        channel_set = channels_ddp_30
    elif channel_set == "62":
        channel_set = channels_ddp_62

    else:
        print("Predefined channel set given by 'channel_set' not known...")
        
    
    # Initialize array
    signal_collection = np.zeros((0,len(channel_set),501))
    label_collection = [] #np.zeros((0))
    channel_names_collection = []
    
    # Import file
    try:
        data_raw = mne.io.read_raw_cnt(file, eog='auto', preload=True, verbose=False)
    except ValueError:
        print("ValueError")
        print("Could not load file:", file)
        return None, None, None
    
    # Band-pass filter (between 0.5 and 40 Hz. was 0.5 to 30Hz in Stober 2016)
    data_raw.filter(0.5, 40, fir_design='firwin')

    # Get events from annotations in the data
    events_from_annot, event_dict = mne.events_from_annotations(data_raw)
    
    # Set baseline:
    baseline = (None, 0)  # means from the first instant to t = 0

    # Select channels to exclude (if any)
    channels_exclude = [x for x in data_raw.ch_names if x not in channel_set]
    channels_exclude = [x for x in channels_exclude if x not in ['HEOG', 'VEOG']]
    
    for event_id in event_idx:
        if str(event_id) in event_dict:
            # Pick EEG channels
            picks = mne.pick_types(data_raw.info, meg=False, eeg=True, stim=False, eog=False,
                               #exclude=data_exclude)#'bads'])
                                   include=channel_set, exclude=channels_exclude)#'bads'])

            epochs = mne.Epochs(data_raw, events=events_from_annot, event_id=event_dict,
                                tmin=tmin, tmax=tmax, proj=True, picks=picks,
                                baseline=baseline, preload=True, event_repeated='merge', verbose=False)

            # Detect potential bad channels and epochs
            bad_channels, bad_epochs = select_bad_epochs(epochs,
                                                                          event_id,
                                                                          threshold = threshold,
                                                                          max_bad_fraction = max_bad_fraction)

            # Interpolate bad channels
            # ------------------------------------------------------------------
            if len(bad_channels) > 0:
                if len(bad_channels) > max_bad_channels:
                    print(20*'--')
                    print("Found too many bad channels (" + str(len(bad_channels)) + ")")
                    return None, None, None
                else:
                    montage = mne.channels.make_standard_montage('standard_1020')
                    montage.ch_names = [ch_name.upper() for ch_name in montage.ch_names]
                    data_raw.set_montage(montage)
                    
                    # MARK: Think about using all channels before removing (62 -> 30), to enable for better interpolation
                    
                    # Mark bad channels:
                    data_raw.info['bads'] = bad_channels
                    # Pick EEG channels:
                    picks = mne.pick_types(data_raw.info, meg=False, eeg=True, stim=False, eog=False,
                                       #exclude=data_exclude)#'bads'])
                                       include=channel_set, exclude=channels_exclude)#'bads'])
                    epochs = mne.Epochs(data_raw, events=events_from_annot, event_id=event_dict,
                                        tmin=tmin, tmax=tmax, proj=True, picks=picks,
                                        baseline=baseline, preload=True, verbose=False)
                    
                    # Interpolate bad channels using functionality of 'mne'
                    epochs.interpolate_bads()
                    

            # Get signals as array and add to total collection
            channel_names_collection.append(epochs.ch_names)
            signals_cleaned = epochs[str(event_id)].drop(bad_epochs).get_data()
            signal_collection = np.concatenate((signal_collection, signals_cleaned), axis=0)
            label_collection += [event_id + label_group] * signals_cleaned.shape[0]

    return signal_collection, label_collection, channel_names_collection
    
    
    
    
    
    
    
# BJORN 2 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@    
    
    
    
    
"""Functions to import and process EEG data from cnt files.
"""
def standardize_EEG(data_array,
                    std_aim = 1,
                    centering = 'per_channel',
                    scaling = 'global'):
    """ Center data around 0 and adjust standard deviation.

    Args:
    --------
    data_array: np.ndarray
        Input data.
    std_aim: float/int
        Target standard deviation for rescaling/normalization.
    centering: str
        Specify if centering should be done "per_channel", or "global".
    scaling: str
        Specify if scaling should be done "per_channel", or "global".
    """
    if centering == 'global':
        data_mean = data_array.mean()

        # Center around 0
        data_array = data_array - data_mean

    elif centering == 'per_channel':
        for i in range(data_array.shape[1]):

            data_mean = data_array[:,i,:].mean()

            # Center around 0
            data_array[:,i,:] = data_array[:,i,:] - data_mean

    else:
        print("Centering method not known.")
        return None

    if scaling == 'global':
        data_std = data_array.std()

        # Adjust std to std_aim
        data_array = data_array * std_aim/data_std

    elif scaling == 'per_channel':
        for i in range(data_array.shape[1]):

            data_std = data_array[:,i,:].std()

            # Adjust std to std_aim
            data_array[:,i,:] = data_array[:,i,:] * std_aim/data_std
    else:
        print("Given method is not known.")
        return None

    return data_array
    
    
    
# BJORN 3 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    


def select_bad_epochs(epochs, stimuli, threshold = 5, max_bad_fraction = 0.2):
    """
    Function to find suspect epochs and channels --> still might need manual inspection!
    
    Args:
    --------
    epochs: epochs object (mne)
    
    stimuli: int/str
        Stimuli to pick epochs for.         
    threshold: float/int
        Relative threshold. Anything channel with variance > threshold*mean OR < threshold*mean
        will be considered suspect. Default = 5.   
    max_bad_fraction: float
        Maximum fraction of bad epochs. If number is higher for one channel, call it a 'bad' channel
    """
    bad_epochs = set()
    bad_channels = []
    
    from collections import Counter
    
    signals = epochs[str(stimuli)].get_data()
    max_bad_epochs = max_bad_fraction*signals.shape[0]
    
    # Find outliers in episode STD and max-min difference:
    signals_std = np.std(signals, axis=2)
    signals_minmax = np.amax(signals, axis=2) - np.amin(signals, axis=2)
    
    outliers_high = np.where((signals_std > threshold*np.mean(signals_std)) | (signals_minmax > threshold*np.mean(signals_minmax)))
    outliers_low = np.where((signals_std < 1/threshold*np.mean(signals_std)) | (signals_minmax < 1/threshold*np.mean(signals_minmax)))
    outliers = (np.concatenate((outliers_high[0], outliers_low[0])), np.concatenate((outliers_high[1], outliers_low[1])) ) 
    
    if len(outliers[0]) > 0:
        print("Found", len(set(outliers[0])), "bad epochs in a total of", len(set(outliers[1])), " channels.")
        occurences = [(Counter(outliers[1])[x], x) for x in list(Counter(outliers[1]))]
        for occur, channel in occurences:
            if occur > max_bad_epochs:
                print("Found bad channel (more than", max_bad_epochs, " bad epochs): Channel no: ", channel )
                bad_channels.append(channel)
            else:
                # only add bad epochs for non-bad channels
                bad_epochs = bad_epochs|set(outliers[0][outliers[1] == channel])
                
        print("Marked", len(bad_epochs), "bad epochs in a total of", signals.shape[0], " epochs.")
        
#        # Remove bad data:
#        signals = np.delete(signals, bad_channels, 1)
#        signals = np.delete(signals, list(bad_epochs), 0)
        
    else:
        print("No outliers found with given threshold.")
    
    return [epochs.ch_names[x] for x in bad_channels], list(bad_epochs)