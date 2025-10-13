(base) avannala@Q2HWTCX6H4 spf-converter % sudo lsof -i :8000
Password:
COMMAND     PID     USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
Python    40354 avannala    3u  IPv4 0x47b72b2b4e9e7469      0t0  TCP localhost:irdmi (LISTEN)
Python    40446 avannala   23u  IPv4 0x87e31f6e75f96fee      0t0  TCP localhost:64941->localhost:irdmi (ESTABLISHED)
Python    40446 avannala   25u  IPv4  0x7ec810bb471151b      0t0  TCP localhost:64905->localhost:irdmi (ESTABLISHED)
Python    40446 avannala   26u  IPv4 0xebbde60b0e460070      0t0  TCP localhost:65235->localhost:irdmi (ESTABLISHED)
Python    58396 avannala    3u  IPv4 0x47b72b2b4e9e7469      0t0  TCP localhost:irdmi (LISTEN)
Python    58396 avannala   15u  IPv4 0x1e112db2b43afcaa      0t0  TCP localhost:64382->localhost:irdmi (ESTABLISHED)
Python    67551 avannala    7u  IPv4 0xe6285aa91a0e5b71      0t0  TCP localhost:49692->localhost:irdmi (ESTABLISHED)
Python    69339 avannala    9u  IPv4 0xdefa33553669107c      0t0  TCP localhost:49907->localhost:irdmi (ESTABLISHED)
Python    71886 avannala    8u  IPv4 0xee61fb0e07804111      0t0  TCP localhost:50148->localhost:irdmi (ESTABLISHED)
Python    75741 avannala    8u  IPv4 0x68c2483266c082f2      0t0  TCP localhost:50445->localhost:irdmi (ESTABLISHED)
Python    77522 avannala    8u  IPv4 0xb40df4b481af4190      0t0  TCP localhost:50578->localhost:irdmi (ESTABLISHED)
python3.1 78494 avannala    9u  IPv4 0xc49d6d0a6b9c477d      0t0  TCP localhost:50728->localhost:irdmi (ESTABLISHED)
python3.1 81058 avannala    8u  IPv4 0xf91e89985a93a001      0t0  TCP localhost:50967->localhost:irdmi (ESTABLISHED)
python3.1 82525 avannala    8u  IPv4 0x587339cecf894bda      0t0  TCP localhost:51150->localhost:irdmi (ESTABLISHED)
(base) avannala@Q2HWTCX6H4 spf-converter % kill -9 $(sudo lsof -t -i:8000)
(base) avannala@Q2HWTCX6H4 spf-converter %
(base) avannala@Q2HWTCX6H4 spf-converter % sudo lsof -i :8000