import json
import uuid
import socket
import os
from datetime import datetime
import time
import platform

system = dict(
    hostname=platform.node(),
    os=platform.system(),
    os_version=platform.version(),
    architecture=platform.machine(),
    machine_id=str(uuid.getnode())
)
environment = dict(
    python_version=platform.python_version(),
    system_language=os.environ.get('LANG', 'Unknown'),
    timezone=time.tzname
)
cpu = dict(
    core_count=os.cpu_count()
)
memory = dict(
    total_memory=None
)
network = dict(
    local_ip=None,
    public_ip=None,
    mac_address=':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)][::-1])
)
timestamp = dict(
    current_time=datetime.now().isoformat(),
    unix_timestamp=time.time()
)


def system_details():
    metrics = dict(
        system=system,
        environment=environment,
        cpu=cpu,
        memory=memory,
        network=network,
        timestamp=timestamp
    )

    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.readlines()
            for line in meminfo:
                if line.startswith('MemTotal:'):
                    metrics['memory']['total_memory'] = str(round(int(line.split()[1]) / 1024 / 1024, 2)) # type: ignore
    except Exception:
        pass

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        metrics['network']['local_ip'] = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    try:
        with os.popen('curl -s https://api.ipify.org') as stream:
            public_ip = stream.read().strip()
            if public_ip:
                metrics['network']['public_ip'] = public_ip # type: ignore
    except Exception:
        pass

    return metrics
