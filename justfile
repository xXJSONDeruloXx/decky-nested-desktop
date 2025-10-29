#! /usr/bin/env bash

test:
    .vscode/build.sh
    scp "out/Example Plugin.zip" deck@192.168.0.6:~/Downloads
    clear
    ssh deck@192.168.0.6 "journalctl --follow"