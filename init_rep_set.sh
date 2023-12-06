#!/bin/bash

# Check if the replica set is already initiated
isInitialized1=$(docker exec -it docker_project-mongo1-1 mongo --quiet --eval "rs.isMaster().ismaster" | tr -d '[:space:]')
isInitialized2=$(docker exec -it docker_project-mongo2-1 mongo --quiet --eval "rs.isMaster().ismaster" | tr -d '[:space:]')
isInitialized3=$(docker exec -it docker_project-mongo3-1 mongo --quiet --eval "rs.isMaster().ismaster" | tr -d '[:space:]')
#This script uses tr -d '[:space:]' to remove any leading or trailing whitespace from the isInitialized
echo "isInitialized1: $isInitialized1"
echo "isInitialized2: $isInitialized2"
echo "isInitialized3: $isInitialized3"

# Check if any of the servers is already initialized
if [ "$isInitialized1" = "true" ]; then
  echo "Replica set is already initialized on docker_project-mongo1-1."
  exit 0
fi

if [ "$isInitialized2" = "true" ]; then
  echo "Replica set is already initialized on docker_project-mongo2-1."
  exit 0
fi

if [ "$isInitialized3" = "true" ]; then
  echo "Replica set is already initialized on docker_project-mongo3-1."
  exit 0
fi

# At this point, none of the servers are initialized, so we proceed to initiate the replica set
echo "Initializing replica set..."
# Initiate the replica set
docker exec -it docker_project-mongo1-1 mongosh --eval "rs.initiate({
  _id: 'myReplicaSet',
  members: [
    { _id: 0, host: 'mongo1' },
    { _id: 1, host: 'mongo2' },
    { _id: 2, host: 'mongo3' }
  ]
})"
