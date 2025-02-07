#!/bin/bash

# submit pre-meshing job
PREPJOB=$(subbin -n |-N_CORES_PREMESHING-| -N |-N_CORESPERNODE_PREMESHING-| -r |-RUNTIME_PREMESHING-| -m "|-MEMORY_PREMESHING-|G" --printjobid -I $(dirname $0)/preMeshing)

# submit main meshing job
MESHJOB=$(subopenfoam -n |-N_CORES_SHM-| -N |-N_CORESPERNODE_SHM-| -r |-RUNTIME_SHM-| -m "|-MEMORY_SHM-|G" -w ${PREPJOB} --printjobid -V v2212 snappyHexMesh --app_options="-case $(dirname $0)")

# submit post meshing and computation job
subbin -n |-N_CORES_OF-| -N |-N_CORESPERNODE_OF-| -r |-RUNTIME_OF-| -m "|-MEMORY_OF-|G" --write-end-file --end-file-name=|-OFDIRNAME-|_OF_finished -w ${MESHJOB} -I $(dirname $0)/Allrun
