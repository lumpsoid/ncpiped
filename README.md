# ncpiped

ncpiped was developed to provide easy access to Piped from the terminal. ncpiped is implemented as an interactive terminal application. 

It is intended to implement three modes: feed, search, and channels, presented as tabs for seamless navigation.

Currently, a minimal working build has been implemented with the ability to scroll through the feed and play the selected video in mpv (by default).

## Dependencies
- mpv
- prompt_toolkit

### PIP
`pip install prompt_toolkit`

### Conda
`conda install -c https://conda.anaconda.org/conda-forge prompt_toolkit`

### Arch linux
`sudo pacman -S mpv`

### Ubuntu
`sudo apt install mpv`

### Gentoo
`emerge --ask media-video/mpv`


## Installation
```
git clone https://github.com/lumpsoid/ncpiped.git
cd ncpiped
chmod +x ncpiped.py
./ncpiped.py
```


## Use cases
```
./ncpiped.py --help
./ncpiped.py -d watchapi.whatever.social -m feed
./ncpiped.py -d watchapi.whatever.social -m feed -v 'mpv --pause'
``` 