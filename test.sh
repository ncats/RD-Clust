#!/bin/bash
#
#
#SBATCH --job-name testjob
#SBATCH --mail-type BEGIN,END
#

#woo hoo from local
#hello from remote
python -c "import mygene"

