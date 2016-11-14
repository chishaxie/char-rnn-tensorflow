#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function
import numpy as np
import tensorflow as tf

import argparse
import time
import os
import re
from six.moves import cPickle

from utils import TextLoader
from model import Model

from six import text_type

import ppzz

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_dir', type=str, default='save',
                       help='model directory to store checkpointed models')
    parser.add_argument('-n', type=int, default=10*33,
                       help='number of characters to sample')
    parser.add_argument('--prime', type=text_type, default=u'\n',
                       help='prime text')
    parser.add_argument('--sample', type=int, default=1,
                       help='0 to use max at each timestep, 1 to sample at each timestep, 2 to sample on spaces')
    parser.add_argument('--verbose', action='store_true',
                       help='Show more information')
    parser.add_argument('--best', action='store_true',
                       help='Show only best')
    args = parser.parse_args()
    assert not (args.verbose and args.best)
    sample(args)

def sample(args):
    with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
        saved_args = cPickle.load(f)
    with open(os.path.join(args.save_dir, 'chars_vocab.pkl'), 'rb') as f:
        chars, vocab = cPickle.load(f)
    model = Model(saved_args, True)
    with tf.Session() as sess:
        tf.initialize_all_variables().run()
        saver = tf.train.Saver(tf.all_variables())
        ckpt = tf.train.get_checkpoint_state(args.save_dir)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)
            had_best = False
            for _ in range(100):
                out = (model.sample(sess, chars, vocab, args.n, args.prime, args.sample))
                if args.verbose:
                    print(out)
                    print('--------------------------------')
                fmt = re.compile(ur'([^，。\s]{7}，[^，。\s]{7}。[^，。\s]{7}，[^，。\s]{7}。)\n')
                ss = fmt.findall(out)
                for s in ss:
                    pz = ppzz.pz_for_7j(s)
                    if args.best:
                        if pz == (0, 0):
                            print(s)
                            had_best = True
                    else:
                        print(s, pz)
                if not args.best or had_best:
                    break

if __name__ == '__main__':
    main()
