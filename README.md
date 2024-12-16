# Install

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Run

```bash
python3 src/main.py
```

# For testing start flask server and adjust config.yaml

```bash
python3 testing_endpoint.py
```

# TODO

- [ ] Observer for logs ?
- [x] Handle new file and reset index
- [ ] Data retention (delete old data after x days)
- [ ] Auto delete after sending to server
- [ ] Message broker ?
- [x] option to send entire log file from start
- [ ] better file handling ( file rotation, file deletion, etc )
