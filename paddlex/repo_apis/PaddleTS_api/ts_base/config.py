# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2024 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Author: PaddlePaddle Authors
"""
import os
from urllib.parse import urlparse

import ruamel.yaml
from paddlets.utils.config import parse_from_yaml, merge_config_dicts

from ...base import BaseConfig
from ....utils.misc import abspath


class BaseTSConfig(BaseConfig):
    """ Base TS Config """

    def update(self, dict_like_obj: list):
        """update self

        Args:
            dict_like_obj (dict): dict of pairs(key0.key1.idx.key2=value).
        """
        dict_ = merge_config_dicts(dict_like_obj, self.dict)
        self.reset_from_dict(dict_)

    def load(self, config_file_path: str):
        """load config from yaml file

        Args:
            config_file_path (str): the path of yaml file.

        Raises:
            TypeError: the content of yaml file `config_file_path` error.
        """
        dict_ = parse_from_yaml(config_file_path)
        if not isinstance(dict_, dict):
            raise TypeError
        self.reset_from_dict(dict_)

    def dump(self, config_file_path: str):
        """dump self to yaml file

        Args:
            config_file_path (str): the path to save self as yaml file.
        """
        yaml = ruamel.yaml.YAML()
        with open(config_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.dict, f)

    def update_epochs(self, epochs: int):
        """update epochs setting

        Args:
            epochs (int): the epochs number value to set
        """
        self.update({'epoch': epochs})

    def update_weights(self, weight_path: str):
        """update weight path

        Args:
            weight_path (str): the local path of weight file to set.
        """
        self['weights'] = abspath(weight_path)

    def update_learning_rate(self, learning_rate: float):
        """update learning rate

        Args:
            learning_rate (float): the learning rate value to set.
        
        Raises:
            RuntimeError: Not able to update learning rate, because no LR scheduler config was found.
        """
        if 'learning_rate' not in self.model['model_cfg']['optimizer_params']:
            raise RuntimeError(
                "Not able to update learning rate, because no LR scheduler config was found."
            )
        self.model['model_cfg']['optimizer_params']['learning_rate'] = float(
            learning_rate)

    def update_batch_size(self, batch_size: int, mode: str='train'):
        """update batch size setting

        Args:
            batch_size (int): the batch size number to set.
            mode (str, optional): the mode that to be set batch size, must be one of 'train', 'eval', 'test'.
                Defaults to 'train'.

        Raises:
            ValueError: `mode` error. `train` is supported only.
        """
        if mode == 'train':
            self.set_val('batch_size', batch_size)
        else:
            raise ValueError(
                f"Setting `batch_size` in {repr(mode)} mode is not supported.")

    def update_pretrained_weights(self, weight_path: str):
        """update pretrained weight path

        Args:
            weight_path (str): the local path or url of pretrained weight file to set.

        Raises:
            RuntimeError: "Not able to update pretrained weight path, because no model config was found.
            TypeError: `weight_path` error. `str` and `None` are supported only.
        """
        if 'model' not in self:
            raise RuntimeError(
                "Not able to update pretrained weight path, because no model config was found."
            )
        if isinstance(weight_path, str):
            if urlparse(weight_path).scheme == '':
                # If `weight_path` is a string but not URL (with scheme present),
                # it will be recognized as a local file path.
                weight_path = abspath(weight_path)
        else:
            if weight_path is not None:
                raise TypeError("`weight_path` must be string or None.")

        self.model['pretrain'] = weight_path

    def update_dataset(self, dataset_dir: str, dataset_type: str=None):
        """update dataset settings
        """
        raise NotImplementedError

    def update_save_dir(self, save_dir: str):
        """update save directory

        Args:
            save_dir (str): the path to save outputs.
        """
        self['output_dir'] = abspath(save_dir)

    def get_epochs_iters(self) -> int:
        """get epochs

        Returns:
            int: the epochs value, i.e., `Global.epochs` in config.
        """
        if 'epoch' in self:
            return self.epoch
        else:
            # Default iters
            return 1000

    def get_learning_rate(self) -> float:
        """get learning rate

        Returns:
            float: the learning rate value, i.e., `Optimizer.lr.learning_rate` in config.
        """
        if 'learning_rate' not in self.model['model_cfg']['optimizer_params']:
            # Default lr
            return 0.0001
        else:
            return self.model['model_cfg']['optimizer_params']['learning_rate']

    def get_batch_size(self, mode='train') -> int:
        """get batch size

        Args:
            mode (str, optional): the mode that to be get batch size value, must be one of 'train', 'eval', 'test'.
                Defaults to 'train'.

        Raises:
            ValueError: `mode` error. `train` is supported only.

        Returns:
            int: the batch size value of `mode`, i.e., `DataLoader.{mode}.sampler.batch_size` in config.
        """
        if mode == 'train':
            if 'batch_size' in self:
                return self.batch_size
            else:
                # Default batch size
                return 16
        else:
            raise ValueError(
                f"Getting `batch_size` in {repr(mode)} mode is not supported.")