import json
import os
import shutil
import subprocess
from glob import glob
from typing import List, Optional

import httpx
from httpx import Response

from hotbox._types import ContainerSpec, GetAppsResponse, Image, Routes
from hotbox.settings import env
from hotbox.templates import (
    BaseDockerfileTemplate,
    BaseEntrypointTemplate,
    BaseInitTabTemplate,
    BaseInterfacesTemplate,
    BaseResolvConfTemplate,
    BaseRunAppTemplate,
    BaseStartMicovmTemplate,
)


class AppService:
    def __init__(self) -> None:
        pass

    def create_app_bundle(
        self,
        app_name: str,
        app_code_path: str,
        container_spec: ContainerSpec,
        vcpu_count: int,
        mem_size_mib: int,
        tmpdir: str,
        fs_size_mib: int,
    ) -> str:
        _image_dir = f"{tmpdir}/{app_name}_image"
        _code_dir = f"{_image_dir}/code"
        os.makedirs(_image_dir, exist_ok=True)
        os.makedirs(_code_dir, exist_ok=True)
        self._create_image(
            image_dir=_image_dir,
            fs_size_mib=fs_size_mib,
            container_spec=container_spec,
        )
        self._create_run_app(
            app_name=app_name,
            vcpu_count=vcpu_count,
            mem_size_mib=mem_size_mib,
            tmpdir=tmpdir,
        )
        shutil.copytree(
            src=app_code_path,
            dst=_code_dir,
            dirs_exist_ok=True,
        )
        # tar up the bundle
        bundle_path = f"{tmpdir}/{app_name}"
        shutil.make_archive(
            base_name=bundle_path,
            format="gztar",
            root_dir=tmpdir,
        )
        return f"{bundle_path}.tar.gz"

    def _create_image(
        self,
        container_spec: ContainerSpec,
        image_dir: str,
        fs_size_mib: int,
    ) -> None:
        self._create_inittab(
            image_dir=image_dir,
        )
        self._create_interfaces(
            image_dir=image_dir,
        )
        self._create_resolvconf(
            image_dir=image_dir,
        )
        self._create_dockerfile(
            image_dir=image_dir,
            container_spec=container_spec,
        )
        self._create_entrypoint(
            image_dir=image_dir,
            fs_size_mib=fs_size_mib,
        )
        self._create_start_script(
            image_dir=image_dir,
            container_spec=container_spec,
        )

    def _create_inittab(self, image_dir: str) -> None:
        content = BaseInitTabTemplate()
        with open(f"{image_dir}/inittab", "w") as f:
            f.write(content.render())

    def _create_interfaces(self, image_dir: str) -> None:
        content = BaseInterfacesTemplate()
        with open(f"{image_dir}/interfaces", "w") as f:
            f.write(content.render())

    def _create_resolvconf(self, image_dir: str) -> None:
        content = BaseResolvConfTemplate()
        with open(f"{image_dir}/resolv.conf", "w") as f:
            f.write(content.render())

    def _create_dockerfile(
        self,
        image_dir: str,
        container_spec: ContainerSpec,
    ) -> None:
        if type(container_spec.image) == Image:
            image = container_spec.image.value
        else:
            image = container_spec.image
        content = BaseDockerfileTemplate(
            inputs={
                "image": image,
                "install": container_spec.install,
                "build": container_spec.build,
            }
        )
        with open(f"{image_dir}/Dockerfile", "w") as f:
            f.write(content.render())

    def _create_entrypoint(
        self,
        image_dir: str,
        fs_size_mib: int,
    ) -> None:
        content = BaseEntrypointTemplate(
            inputs={
                "fs_size_mib": str(fs_size_mib),
            }
        )
        with open(f"{image_dir}/entrypoint", "w") as f:
            f.write(content.render())

    def _create_start_script(
        self, image_dir: str, container_spec: ContainerSpec
    ) -> None:
        content = BaseStartMicovmTemplate(
            inputs={
                "entrypoint": container_spec.entrypoint,
            }
        )
        with open(f"{image_dir}/start.sh", "w") as f:
            f.write(content.render())

    def _create_run_app(
        self, app_name: str, vcpu_count: int, mem_size_mib: int, tmpdir: str
    ) -> None:
        content = BaseRunAppTemplate(
            inputs={
                "app_name": app_name,
                "vcpu_count": str(vcpu_count),
                "mem_size_mib": str(mem_size_mib),
            }
        )
        with open(f"{tmpdir}/{app_name}_run_app.sh", "w") as f:
            f.write(content.render())

    def upload_app_bundle(self, app_name: str, bundle_path: str) -> Response:
        response = httpx.post(
            url=env.HOTBOX_API_URL + Routes.apps,
            files={
                "upload_file": (
                    os.path.basename(bundle_path),
                    open(bundle_path, "rb"),
                    "application/gzip",
                ),
                "create_app_request": (
                    None,
                    json.dumps({"app_name": app_name}),
                    "application/json",
                ),
            },
        )
        return response

    def unzip_and_run(
        self, bundle_path: str, app_name: str
    ) -> None:  # pragma: no cover
        subprocess.run(
            f"tar -xzf {bundle_path}",
            shell=True,
        )
        subprocess.run(
            f"chmod +x {app_name}_run_app.sh",
            shell=True,
        )
        subprocess.run(
            f"./{app_name}_run_app.sh &",
            shell=True,
        )

    def get_apps(self, name: Optional[str] = None) -> GetAppsResponse:
        _glob = "fc-*-config.json"
        if name is not None:
            _glob = f"fc-{name}-config.json"
        _files = glob(_glob)
        _apps = {}
        for _file in _files:
            with open(_file) as f:
                _app_name = "-".join(_file.split("-")[1:-1])
                _apps[_app_name] = json.load(f)
        return GetAppsResponse(apps=_apps)

    def make_delete_request(self, app_names: List[str]) -> Response:
        response = httpx.delete(
            url=env.HOTBOX_API_URL + Routes.apps,
            params={"app_names": app_names},
        )
        return response

    def delete(self, app_names: List[str]) -> List[str]:
        get_apps_res = self.get_apps()
        apps = get_apps_res.apps
        for app_name in set(app_names) & set(apps.keys()):
            app_content = apps[app_name]
            _files = glob(f"{app_name}*") + glob(f"fc-{app_name}*")
            for _file in _files:
                if os.path.isdir(_file):
                    shutil.rmtree(_file)
                else:
                    os.remove(_file)
            network_interfaces = app_content["network-interfaces"]
            # get the network interface with eth0 iface_id
            for iface in network_interfaces:
                if iface["iface_id"] == "eth0":
                    eth0_iface = iface
                    break
            subprocess.run(
                f"pkill -f fc-{app_name}",
                shell=True,
            )
            subprocess.run(
                f"ip link del {eth0_iface['host_dev_name']}",
                shell=True,
            )

        return app_names


app_svc = AppService()
