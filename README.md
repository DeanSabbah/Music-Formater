Simple program that formats a flat music library. It will sort your music with the following structure:
``` txt
.
├── Artist 1/
│   ├── Album 1/
│   │   ├── track 1
│   │   ├── track 2
│   │   ├── track 3
│   │   └── ...
│   ├── Album 2/
│   │   ├── track 1
│   │   ├── track 2
│   │   ├── track 3
│   │   └── ...
│   └── ...
├── Artist 2/
│   ├── Album 1/
│   │   ├── track 1
│   │   ├── track 2
│   │   ├── track 3
│   │   └── ...
│   ├── Album 2/
│   │   ├── track 1
│   │   ├── track 2
│   │   ├── track 3
│   │   └── ...
│   └── ...
└── ...
```
###### Generated using [tree.nathanfriend.com](tree.nathanfriend.com)

If a track has multiple artists, the first artist will be considered the main artist, and the track will be placed in that artist's directory.
