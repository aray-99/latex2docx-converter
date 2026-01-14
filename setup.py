"""
Setup configuration for latex2docx package.
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='latex2docx',
    version='0.2.0',
    description='Convert LaTeX to DOCX with integrated TikZ support',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ryota',
    license='MIT',
    
    package_dir={'': 'src'},
    packages=find_packages('src'),
    
    python_requires='>=3.10',
    
    entry_points={
        'console_scripts': [
            'latex2docx=latex2docx.cli:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Natural Language :: Japanese',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing :: Markup :: LaTeX',
    ],
    
    keywords='LaTeX DOCX TikZ conversion',
)
