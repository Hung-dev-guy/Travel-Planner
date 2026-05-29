Run graph database
```bash
docker run \      
    -d \
    --name neo4j \
    --restart always \
    --publish=7474:7474 --publish=7687:7687 \
    --env NEO4J_AUTH=neo4j/12345678 \
    --volume=/home/hungdvlper/Documents/TTCS/Traplanner/SourceCode/neo4j-data:/data \
    neo4j:latest
```