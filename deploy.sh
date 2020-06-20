#!/usr/bin/env bash
set -e

function abort_deployment() {
    echo "\033[1;31mAborting Deployment...\033[0m"
    exit 1
}

function confirm_question() {
    if [[ $# != 1 ]]; then
        abort_deployment
    else
        question=$1
        while true; do
            printf "${question}(yes/no) "
            read answer

            if [[ ${answer} = "yes" || ${answer} = "y" ]]; then
                return 0
            elif [[ ${answer} = "no" || ${answer} = "n" ]]; then
                return 1
            fi
        done
    fi
}

chown_and_log() {
    [[ $# != 3 ]] && echo "${FUNCNAME[0]}: Does not have correct arguments" && abort_deployment

    local new_uid=$1
    local new_gid=$2
    local directory=$3

    local directory_info=$(ls -ld ${directory})

    local user=$(echo ${directory_info} | awk '{print $3}')
    local uid=$(id ${user} | awk '{print $1}' | sed 's/uid=\(.*\)(.*/\1/')

    local group=$(echo ${directory_info} | awk '{print $4}')
    local gid=$(id ${group} | awk '{print $2}' | sed 's/gid=\(.*\)(.*/\1/')

    if [[ ${uid} != ${new_uid} || ${gid} != ${new_gid} ]]; then
        echo "Directory ${directory} is owned by ${uid}:${gid}"
        chown ${new_uid}:${new_gid} ${directory}
        echo "Directory ${directory} changed successfully to ${new_uid}:${new_gid}"
    else
        echo "Directory ${directory} is already owned by ${new_uid}:${new_gid}"
    fi
}

create_directory_and_log() {
    [[ $# != 1 ]] && echo "${FUNCNAME[0]}: Does not have correct arguments" && abort_deployment

    local directory=$1
    if [[ -d ${directory} ]]; then
        echo "Directory already exists: ${directory}"
    else
        mkdir ${directory}
        echo "Directory successfully created: ${directory}"
    fi
}

format_emscripten_fs() {
    echo -e "Checking ${EMSCRIPTEN}"
    [[ $# != 1 ]] && echo "${FUNCNAME[0]}: Does not have correct arguments" && abort_deployment

    local parent_directory=$1

    local compiler_directory=${parent_directory}/${EMSCRIPTEN}
    create_directory_and_log ${compiler_directory}
    echo ""
}

adjust_emscripten_ownership() {
    echo "Checking ${EMSCRIPTEN} ownership"
    [[ $# != 1 ]] && echo "${FUNCNAME[0]}: Does not have correct arguments" && abort_deployment

    local parent_directory=$1

    local compiler_directory=${parent_directory}/${EMSCRIPTEN}
    chown_and_log 1000 1000 ${compiler_directory}
    echo ""
}

format_golang_fs() {
    echo -e "Checking ${GOLANG}"
    [[ $# != 1 ]] && echo "${FUNCNAME[0]}: Does not have correct arguments" && abort_deployment

    local parent_directory=$1

    local compiler_directory=${parent_directory}/${GOLANG}
    create_directory_and_log ${compiler_directory}
    create_directory_and_log ${compiler_directory}/bin
    create_directory_and_log ${compiler_directory}/dev_tools
    create_directory_and_log ${compiler_directory}/src
    echo ""
}

adjust_golang_ownership() {
    echo -e "Checking ${GOLANG} ownership"
    [[ $# != 1 ]] && echo "${FUNCNAME[0]}: Does not have correct arguments" && abort_deployment

    local parent_directory=$1

    local compiler_directory=${parent_directory}/${GOLANG}
    chown_and_log 1000 1000 ${compiler_directory}
    chown_and_log 1000 1000 ${compiler_directory}/bin
    chown_and_log 1000 1000 ${compiler_directory}/dev_tools
    chown_and_log 1000 1000 ${compiler_directory}/src
    echo ""
}

function create_results_volume() {
    echo -e "\033[1;34mChecking for the Results volume...\033[0m\n"
    [[ $# != 1 ]] && echo "${FUNCNAME[0]}: Does not have correct arguments" && abort_deployment

    local configuration=$1

    local current_directory=${HOST_RESULTS_DIR_PREFIX}
    create_directory_and_log ${current_directory}
    echo ""

    current_directory=${current_directory}/wasmcc_results
    create_directory_and_log ${current_directory}
    echo ""

    if [[ ${configuration} = "production" ]]; then
        current_directory=${current_directory}${ROOT_RESULTS_DIR}
    elif [[ ${configuration} = "development" ]]; then
        current_directory=${current_directory}${ROOT_RESULTS_DIR_DEVEL}
    elif [[ ${configuration} = "testing" ]]; then
        current_directory=${current_directory}${ROOT_RESULTS_DIR_TEST}
    else
        abort_deployment
    fi

    create_directory_and_log ${current_directory}
    echo ""

    format_emscripten_fs ${current_directory}
    format_golang_fs ${current_directory}

    confirm_question "Change the owner to 1000:1000 for the aforementioned directories?"
    echo ""

    chown_and_log 1000 1000 ${current_directory}
    adjust_emscripten_ownership ${current_directory}
    adjust_golang_ownership ${current_directory}

    echo -e "\033[1;34mResults volume is ready\033[0m\n"
}

create_DB_volume() {
    echo -e "\033[1;34mChecking for the Database volume...\033[0m\n"
    [[ $# != 1 ]] && echo "${FUNCNAME[0]}: Does not have correct arguments" && abort_deployment

    local configuration=$1
    local current_directory=${HOST_RESULTS_DIR_PREFIX}/wasmcc_volumes
    create_directory_and_log ${current_directory}
    echo ""

    if [[ ${configuration} = "production" ]]; then
        current_directory=${current_directory}${ROOT_DB_DIR}
    elif [[ ${configuration} = "development" ]]; then
        current_directory=${current_directory}${ROOT_DB_DIR_DEVEL}
    elif [[ ${configuration} = "testing" ]]; then
        current_directory=${current_directory}${ROOT_DB_DIR_TEST}
    else
        abort_deployment
    fi

    create_directory_and_log ${current_directory}
    echo ""

    confirm_question "Change the owner to 999:0 for the aforementioned directories?"
    echo ""

    chown_and_log 999 0 ${current_directory}

    echo -e "\n\033[1;34mDatabase volume is ready\033[0m\n"
}

create_volumes() {
    [[ $# != 1 ]] && echo "${FUNCNAME[0]}: Does not have correct arguments" && abort_deployment

    local configuration=$1
    create_results_volume $1
    create_DB_volume $1
}

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
            source .env
            create_volumes testing
            docker-compose -f docker-compose.test.yaml up --abort-on-container-exit
            return_value=$?
            docker-compose -f docker-compose.test.yaml down
            exit ${return_value}
            ;;
        --deploy )
            source .env;
            create_volumes production
            docker-compose up -d
            exit $?
            ;;
        --deploy-devel )
            source .env;
            create_volumes development
            docker-compose -f docker-compose.devel.yaml up
            exit $?
            ;;
        --deploy-down )
            docker-compose down
            exit $?
            ;;
        --deploy-devel-down )
            docker-compose -f docker-compose.devel.yaml down
            exit $?
            ;;
        --stop-tests )
            docker-compose -f docker-compose.test.yaml down
            exit $?
            ;;
        --build )
            docker-compose build
            exit $?
            ;;
        --build-devel )
            docker-compose -f docker-compose.devel.yaml build
            exit $?
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
