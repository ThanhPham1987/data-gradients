import concurrent
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Iterator

import hydra
from matplotlib import pyplot as plt

from feature_extractors import FeatureExtractorAbstract
from preprocess.preprocessor_abstract import PreprocessorAbstract
from logger.tensorboard_logger import TensorBoardLogger
from utils.data_classes import BatchData


debug_mode = True


class AnalysisManager:
    def __init__(self, cfg, train_data_iterator: Iterator, val_data_iterator: Optional[Iterator] = None):
        self._train_extractors: List[FeatureExtractorAbstract] = []
        self._val_extractors:   List[FeatureExtractorAbstract] = []
        self._threads = ThreadPoolExecutor()

        self.cfg = cfg

        # Users Data Iterators
        self._train_only: bool = val_data_iterator is None
        self._train_iter: Iterator = train_data_iterator
        self._val_iter: Iterator = val_data_iterator

        # Logger
        self._logger = TensorBoardLogger()

        # Task Data Preprocessor
        self._preprocessor: PreprocessorAbstract = PreprocessorAbstract.get_preprocessor(cfg.task)
        self._preprocessor.number_of_classes = cfg.number_of_classes
        self._preprocessor.ignore_labels = cfg.ignore_labels

    def build(self):
        cfg = hydra.utils.instantiate(self.cfg)
        self._train_extractors = cfg.common + cfg[cfg.task]
        cfg = hydra.utils.instantiate(self.cfg)
        self._val_extractors = cfg.common + cfg[cfg.task]

    def _get_batch(self, data_iterator) -> BatchData:
        images, labels = next(data_iterator)
        images, labels = self._preprocessor.validate(images, labels)
        bd = self._preprocessor.preprocess(images, labels)
        return bd

    def execute(self):
        train_batch = 0
        while True:
            print(f'Processing train batch {train_batch}...', flush=True)
            if train_batch > 3 and debug_mode:
                break
            try:
                batch_data = self._get_batch(self._train_iter)
            except StopIteration:
                break

            for extractor in self._train_extractors:
                if not debug_mode:
                    futures = [self._threads.submit(extractor.execute, batch_data) for extractor in
                               self._train_extractors]
                else:
                    extractor.execute(batch_data)

            if not self._train_only:
                try:
                    batch_data = self._get_batch(self._val_iter)
                except StopIteration:
                    self._train_only = True
                else:
                    for extractor in self._val_extractors:
                        if not debug_mode:
                            futures += [self._threads.submit(extractor.execute, batch_data) for extractor in
                                        self._val_extractors]
                        else:
                            extractor.execute(batch_data)

            if not debug_mode:
                # Wait for all threads to finish
                concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
            train_batch += 1

    def post_process(self):
        for val_extractor, train_extractor in zip(self._val_extractors, self._train_extractors):
            fig, ax = plt.subplots()

            # First val - because graph params will be overwritten by latest (train) and we want it's params
            if not self._train_only:
                val_extractor.process(ax, train=False)

            train_extractor.process(ax, train=True)

            fig.tight_layout()

            self._logger.log_graph(val_extractor.__class__.__name__ + "/fig", fig)

    def close(self):
        self._logger.close()

    def run(self):
        self.build()
        self.execute()
        self.post_process()
        self.close()
