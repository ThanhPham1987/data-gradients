from typing import List
import numpy as np

import preprocess.contours
from utils.data_classes import BatchData
from feature_extractors.segmentation.segmentation_abstract import SegmentationFeatureExtractorAbstract
from logger.logger_utils import create_bar_plot


class SegmentationCountSmallObjects(SegmentationFeatureExtractorAbstract):
    def __init__(self, percent_of_an_image):
        super().__init__()
        # TODO NUMBERS DOES NOT WORK
        min_pixels: int = int(512 * 512 / (percent_of_an_image * 100))
        self.bins = np.array(range(0, min_pixels, int(min_pixels / 10)))
        self._hist: List[int] = [0] * 11
        self.label = ['<0.01', '0.02', '0.03', '0.04', '0.05', '0.06', '0.07', '0.08', '0.09', '0.1', '>0.1']

    def execute(self, data: BatchData):
        for i, onehot_contours in enumerate(data.batch_onehot_contours):
            for cls_contours in onehot_contours:
                for c in cls_contours:
                    _, _, contour_area = preprocess.contours.get_contour_moment(c)
                    self._hist[np.digitize(contour_area, self.bins) - 1] += 1

    def process(self, ax, train):
        self._hist = list(np.array(self._hist) / sum(self._hist))
        create_bar_plot(ax, self._hist, self.label,
                        x_label="Object Size [%]", y_label="# Objects", ticks_rotation=0,
                        title="Number of small objects", train=train, color=self.colors[int(train)])

        ax.grid(visible=True, axis='y')
