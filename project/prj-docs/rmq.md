```
docker exec -it some-rabbit rabbitmqadmin -f tsv -q list queues name | tr -d '\r' | xargs -I {} rabbitmqadmin delete queue name={}
```