#!/usr/bin/env python3

import os
import base64
import random
import libnotary


def main():
    N = 10

    for i in range(N):
        data = os.urandom(random.randrange(10, 1000))
        
        private_key = libnotary.generate()
        public_key = libnotary.get_public(private_key)
                
        signature = libnotary.sign(private_key, data)
    
        if not libnotary.verify(public_key, data, signature):
            print(i, 'FAILED')


if __name__ == '__main__':
    main()
