#/usr/bin/env python3

from distutils.core import setup, Extension


def main():
    files = [
        'src/point.c',
        'src/curve.c',
        'src/public.c',
        'src/private.c',
        'src/serialization.c',
        'src/sign.c',
        'src/libnotary.c',
    ]

    flags = [
        '-lgmp',
        '-Wall',
        '-fvisibility=hidden',
        '-O0',
        '-s',
    ]

    libnotary = Extension(
        name='libnotary',
        sources=files,
        language='C',
        extra_link_args=flags,
        extra_compile_args=flags,
    )

    modules = [
        libnotary,
    ]

    setup(
        name='libnotary', 
        ext_modules=modules,
    )


if __name__ == '__main__':
    main()
