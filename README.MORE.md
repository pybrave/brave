进程间通讯的格式
```
echo '{"workflow_id": "wf-001", "workflow_event":"flow_begin", "ingress_event": "workflow_log"}' | socat - UNIX-CONNECT:/tmp/brave.sock
```