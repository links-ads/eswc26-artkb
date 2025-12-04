#!/bin/bash

ProgName=$(basename $0)

execute(){
    Action=$1
    Target=$2
    export BUILD_TARGET=$Target
    set -a
    source ./envs/$Target.env
    set +a
    shift 2
    echo "Executing action: $Action - Build target: $BUILD_TARGET"
    docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.$Target.yml $Action $@
}

cmd_init(){
    echo "Initialise main repository..."
    git checkout main
    git pull origin main
    echo "Done"
}

cmd_help(){
    echo "Usage: $ProgName <subcommand> [options]\n"
    echo "Subcommands:"
    echo "    build [dev/prod] [compose args]"
    echo "    run [dev/prod] [compose args]"
    echo "    stop [dev/prod]"
    echo "    boot [dev/prod]"
    echo "    config [dev/prod]"
    echo "    clean [dev/prod]"
    echo ""
    echo "For help with each subcommand run:"
    echo "$ProgName <subcommand> -h|--help"
    echo ""
}

cmd_boot(){
    echo "Building images..."
    Target=$1
    export BUILD_TARGET=$Target
    set -a
    source ./envs/$Target.env
    set +a
    docker compose --profile boot -f docker/docker-compose.base.yml -f docker/docker-compose.$Target.yml up --build boot
}

cmd_config(){
    echo "Printing config..."
    Target=$1
    export BUILD_TARGET=$Target
    set -a
    source ./envs/$Target.env
    set +a
    docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.$Target.yml config
}

cmd_clean(){
    echo "Building images..."
    Target=$1
    echo $Target
    export BUILD_TARGET=$Target
    set -a
    source ./envs/$Target.env
    set +a
    docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.$Target.yml down -v --rmi all
}

cmd_build(){
    echo "Building images..."
    Target=$1
    shift
    execute build $Target $@
}

cmd_run(){
    echo "Running project..."
    Target=$1
    shift
    execute up $Target $@
}

cmd_stop(){
    echo "Testing deployment configuration..."
    Target=$1
    shift
    execute stop $Target $@
}

subcommand=$1
case $subcommand in
    "" | "-h" | "--help")
        cmd_help
        ;;
    *)
        shift
        cmd_${subcommand} $@
        echo "Done!"
        if [ $? = 127 ]; then
            echo "Error: '$subcommand' is not a known subcommand." >&2
            echo "       Run '$ProgName --help' for a list of known subcommands." >&2
            exit 1
        fi
        ;;
esac