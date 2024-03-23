#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


class StepTooSmallException(Exception):
    """
    if the step is too small, the last_value will not update
    """
