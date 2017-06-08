import tarfile
import atexit

from sh import cat, tar
from tqdm import tqdm


def extract_bigtgz(bigtgz, size, out_path):
    with tarfile.open(bigtgz, 'r|gz') as tar:
        with tqdm(total=size, unit='images', ncols=80, unit_scale=True) as pbar:
            def callback(members):
                for tarinfo in members:
                    pbar.update(1)
                    yield tarinfo
            tar.extractall(path=out_path, members=callback(tar))


def extract_chunks(files, num_images, out_path):
    with tqdm(total=num_images,
              unit='images',
              ncols=80,
              unit_scale=True) as pbar:
        process = tar(cat(files, _piped=True), 'xvz', _iter=True, _cwd=out_path)

        def kill():
            try:
                process.kill()
            except:
                pass
        atexit.register(kill)
        for line in process:
            if line.strip().endswith('.jpg'):
                pbar.update(1)
