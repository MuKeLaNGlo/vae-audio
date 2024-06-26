import os
from pathlib import Path
from torch.utils.data import Dataset


class CollectData(Dataset):
    def __init__(self, path_to_dataset, extension=['wav', 'mp3', 'npy', 'pth'], subset=None, transform=None):
        """
        Assume directory structure as:
        - dataset (the level which path_to_dataset indicates)
            - trainingdata
                - class A
                - class B
                ...
            - testdata
                - class A
                - class B
                ...
        :param path_to_dataset: a list of path to dataset directory; thus allows multiple datasets
        :param subset: None|'train'|'test'; if None, both train and test sets are loaded
        :param transform: see https://pytorch.org/docs/stable/torchvision/transforms.html
        """
        assert isinstance(path_to_dataset, list), "The input path_to_dataset should be a list."
        assert subset in [None, 'train', 'test'], "subset should be in [None, 'train', 'test']"

        full_path_to_dataset = []
        for data_dir in path_to_dataset:
            if not subset:  # load both train and test folders
                full_path_to_dataset.append(os.path.join(data_dir, 'trainingdata'))
                full_path_to_dataset.append(os.path.join(data_dir, 'testdata'))
            elif subset == 'train':
                full_path_to_dataset.append(os.path.join(data_dir, 'trainingdata'))
            else:
                full_path_to_dataset.append(os.path.join(data_dir, 'testdata'))

        aggr_data_path = []
        aggr_label = []
        for data_dir in full_path_to_dataset:
            for subclass in os.listdir(data_dir):
                for f in os.listdir(os.path.join(data_dir, subclass)):
                    if any(ext in f for ext in extension):
                        aggr_data_path.append(os.path.join(data_dir, subclass, f))
                        aggr_label.append(subclass)

        self.path_to_dataset = path_to_dataset
        self.extension = extension
        self.subset = subset
        self.transform = transform
        self.path_to_data = aggr_data_path
        self.labels = aggr_label

    def __len__(self):
        return len(self.path_to_data)

    def __getitem__(self, idx):
        if self.transform:
            return idx, self.labels[idx], self.transform(self.path_to_data[idx])

        return idx, self.labels[idx], self.path_to_data[idx]


class NsynthSubset(Dataset):
    """
    This Dataset is used to load *the filtered Nsynth (by nsynth_subset.py)*.
    In the filtered subset, file name follows the format:

        instrumentFamily_source_instrumentID-pitch-velocity

    which is true only when synthesizers are not included (a different format).
    """
    def __init__(self, path_to_dataset, file_ext='.wav', transform=None):
        path_to_data = Path(path_to_dataset)
        file_ext = '*' + file_ext
        y = []
        for f in path_to_data.glob(file_ext):
            f_name = f.stem
            instrument, pitch, vel = f_name.split('-')[0], int(f_name.split('-')[1]), int(f_name.split('-')[2])
            instrument_prop = instrument.split('_')
            assert len(instrument_prop) == 3
            assert instrument_prop[1] == 'acoustic'
            family, inst_id = instrument_prop[0], instrument_prop[2]
            y.append({'family': family, 'instrument': inst_id, 'pitch': pitch, 'velocity': vel})

        self.file_ext = file_ext
        self.path_to_data = list(path_to_data.glob(file_ext))
        self.labels = y
        self.transform = transform

        if len(self.path_to_data) == 0:
            raise Warning("The size of path_to_data is zero with the specified extension %s" % file_ext)

    def __len__(self):
        return len(self.path_to_data)

    def __getitem__(self, idx):
        if self.transform:
            return idx, self.labels[idx], self.transform(str(self.path_to_data[idx]))

        return idx, self.labels[idx], str(self.path_to_data[idx])


if __name__ == '__main__':
    path_to_data = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'myAudioDataset/audio')
    d = CollectData([path_to_data], subset=None, transform=None)
    print("the number of data: %d" % len(d))
    try:
        print("the first five entries:")
        for n in range(5):
            print(d[n])
    except Exception:
        raise IndexError("There is none or fewer than 5 data in the input path")
