#! /usr/bin/env bash

@default:
    just --list

test:
    .vscode/build.sh
    scp "out/Nested Desktop.zip" deck@192.168.0.6:~
    clear
    ssh deck@192.168.0.6 "journalctl --follow"

ssh:
    ssh deck@192.168.0.6