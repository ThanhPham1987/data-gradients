from typing import List

import numpy as np

from src.logger.logger_utils import create_heatmap_plot
from src.preprocess import contours
from src.utils import SegBatchData
from src.feature_extractors.segmentation.segmentation_abstract import SegmentationFeatureExtractorAbstract


class ObjectsCenterOfMass(SegmentationFeatureExtractorAbstract):
    """
    Semantic Segmentation task feature extractor -
    Get all X, Y positions of center of mass of every object in every image for every class.
    Plot those X, Y positions as a heat-map
    """
    def __init__(self, num_classes, ignore_labels):
        super().__init__()
        keys = [int(i) for i in range(0, num_classes + len(ignore_labels)) if i not in ignore_labels]
        self._hist = {k: {'x': list(), 'y': list()} for k in keys}

        self.single_axis = False

    def _execute(self, data: SegBatchData):
        for i, image_contours in enumerate(data.contours):
            for j, cls_contours in enumerate(image_contours):
                unique = np.unique(data.labels[i][j])
                if not len(unique) > 1:
                    continue
                for c in cls_contours:
                    center = contours.get_contour_center_of_mass(c)
                    self._hist[int(np.delete(unique, 0))]['x'].append(center[0])
                    self._hist[int(np.delete(unique, 0))]['y'].append(center[1])

    def process(self, ax, train):
        x, y = [], []
        for val in self._hist.values():
            x.extend(val['x'])
            y.extend(val['y'])
        # TODO: My thumb rules numbers
        bins = int(np.sqrt(len(x)) * 4)
        sigma = 2 * (bins / 150)

        # TODO: Divide each plot for a class. Need to make x, y as a dictionaries (every class..)
        create_heatmap_plot(ax=ax, x=x, y=y,  train=train, bins=bins, sigma=sigma,
                            title=f'Center of mass average locations', x_label='X axis', y_label='Y axis')

        return {"Am I implemented?": False}
