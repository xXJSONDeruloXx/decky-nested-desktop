#! /usr/bin/env bash

@default:
    just --list

test:
    .vscode/build.sh
    scp "out/Example Plugin.zip" deck@192.168.0.6:~/Downloads
    clear
    ssh deck@192.168.0.6 "journalctl --follow"

ssh:
    ssh deck@192.168.0.6