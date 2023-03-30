#!/usr/bin/env bash
#$ -wd /home/bodoom1/repos/csci-601-771-self-supervised-models/sp2023/hw6
#$ -V
#$ -N prompts
#$ -j y -o $JOB_NAME-$JOB_ID.out
#$ -M bodoom1@jhu.edu
#$ -m e
#$ -l ram_free=20G,mem_free=20G,gpu=1,hostname=octopod
#$ -q g.q
#$ -t 1
#$ -o /home/bodoom1/repos/csci-601-771-self-supervised-models/sp2023/hw6/logs/

source /home/gqin2/scripts/acquire-gpu;

conda activate speech

python bloom_1.py 