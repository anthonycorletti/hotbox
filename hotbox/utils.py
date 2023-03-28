import json
import os
import sys
from datetime import date, datetime
from typing import Any, Dict

import paramiko
from typer import FileText


def handle_filetext(filetext: FileText) -> Dict:
    if hasattr(filetext, "read"):
        content = filetext.read().encode("utf-8")
    if filetext == "-":
        content = sys.stdin.buffer.read()
    if isinstance(filetext, str):
        content = filetext.encode("utf-8")
    else:
        raise TypeError(f"Unsupported filetext type: {type(filetext)}")
    return json.loads(content)


def json_serializer(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class SCPClient:
    def __init__(self, host: str, private_key_path: str, username: str) -> None:
        self.host = host
        self.username = username
        self.private_key_path = private_key_path
        self.ssh: paramiko.SSHClient = None
        self.scp: paramiko.SFTPClient = None

    def __enter__(self) -> "SCPClient":
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()
        private_key = paramiko.RSAKey.from_private_key_file(self.private_key_path)
        self.ssh.connect(self.host, username=self.username, pkey=private_key)
        self.scp = self.ssh.open_sftp()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.scp is not None:
            self.scp.close()
        if self.ssh is not None:
            self.ssh.close()

    def put_dir(self, local_dir_path: str, remote_dir_path: str) -> None:
        # TODO parallelize this
        for item in os.listdir(local_dir_path):
            _src_path = os.path.join(local_dir_path, item)
            _dst_path = os.path.join(remote_dir_path, item)
            if os.path.isfile(_src_path):
                self.scp.put(_src_path, _dst_path)
            else:
                self.mkdir(_dst_path, ignore_existing=True)
                self.put_dir(_src_path, _dst_path)

    def mkdir(self, path: str, mode: int = 511, ignore_existing: bool = False) -> None:
        try:
            self.scp.mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise IOError(
                    f"Directory {path} already exists. Pass `ignore_existing=True` to "
                    "ignore this error or use another name."
                )


def scp_dir(
    app_id: str,
    local_dir: str,
    private_key_path: str,
    remote_hostname: str,
    remote_dir: str = "/home/ubuntu",
    username: str = "ubuntu",
) -> None:
    with SCPClient(
        host=remote_hostname, private_key_path=private_key_path, username=username
    ) as scp:
        scp.mkdir(f"{remote_dir}/{app_id}", ignore_existing=True)
        scp.put_dir(local_dir_path=local_dir, remote_dir_path=f"{remote_dir}/{app_id}")
