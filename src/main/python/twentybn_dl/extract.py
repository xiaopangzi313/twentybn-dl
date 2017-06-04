import tarfile

from tqdm import tqdm


def extract_bigtgz(self, bigtgz, size, out_path):
    with tarfile.open(bigtgz, 'r|gz') as tar:
        with tqdm(total=self.count, unit='records') as pbar:
            def callback(members):
                for tarinfo in members:
                    pbar.update(1)
                    yield tarinfo
            tar.extractall(path=out_path, members=callback(tar))
