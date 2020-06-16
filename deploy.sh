#!/usr/bin/env bash

function usage() {
    echo "deploy.sh [--delete-images branch] [--run-tests] [--help|-h]"
}

while [[ "$1" != "" ]]; do
    case "$1" in
        --delete-images )
            shift
            if [[ -n $1 ]] && [[ $1 != -* ]]; then
                echo "Images:"
                docker images --filter=reference="*:$1"

                answer=""
                while [[ ${answer} != "yes" && ${answer} != "y" && ${answer} != "no" && ${answer} != "n" ]]; do
                    printf "Are you sure you want to delete these images?(yes/no) "
                    read answer
                done

                if [[ ${answer} = "yes" || ${answer} = "y" ]]; then
                    echo "Deleting images..."
                    docker rmi $(docker images --filter=reference="*:$1" --format="{{.Repository}}:{{.Tag}}")
                    echo "Images Deleted"
                fi

                shift
            else
                usage
                exit 1
            fi
            ;;
        --run-tests )
            docker-compose -f docker-compose.test.yaml up --abort-on-container-exit
            return_value=$?
            docker-compose -f docker-compose.test.yaml down
            exit ${return_value}
            ;;
        --help | -h )
            usage
            exit 0
            ;;
        * )
            usage
            exit 1
            ;;
    esac
done
# if [[ -d /results ]]
# then
#     echo "/results exists on your filesystem."
#     echo "Please move its contents to another directory and remove the directory, so that the deployment can continue."
#     echo "Exiting..."
#     exit 1
# fi
#
# docker-compose up
#
# exit 0
