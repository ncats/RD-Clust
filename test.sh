#!/bin/bash
#
#
#SBATCH --job-name testjob
#SBATCH --mail-type BEGIN,END
#

which python
python -c "import mygene"

