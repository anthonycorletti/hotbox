import json
import os
import shutil
import subprocess
from glob import glob
from typing import List, Optional

import httpx
from httpx import Response
from jinja2 import Template

from hotbox.const import (
    DEFAULT_IMAGE_TEMPLATE_DIR,
    DEFAULT_LANG_TEMPLATE_DIR,
    DEFAULT_RUN_APP_TEMPLATE_FILEPATH,
)
from hotbox.settings import env
from hotbox.types import GetAppsResponse, Image, Routes


class AppService:
    def __init__(self) -> None:
        pass

    def create_app_bundle(
        self,
        app_name: str,
        app_code_path: str,
        build_image: Image,
        vcpu_count: int,
        mem_size_mib: int,
        fs_size_mib: int,
        tmpdir: str,
    ) -> str:
        _image_dir = f"{tmpdir}/{app_name}_image"
        _code_dir = f"{tmpdir}/{app_name}_code"
        os.makedirs(_image_dir, exist_ok=True)
        os.makedirs(_code_dir, exist_ok=True)
        shutil.copytree(
            src=f"{DEFAULT_IMAGE_TEMPLATE_DIR}",
            dst=_image_dir,
            dirs_exist_ok=True,
        )
        shutil.copytree(
            src=app_code_path,
            dst=_code_dir,
            dirs_exist_ok=True,
        )
        self._create_image(
            image=build_image,
            image_dir=_image_dir,
            fs_size_mib=fs_size_mib,
        )
        self._create_run_app(
            app_name=app_name,
            vcpu_count=vcpu_count,
            mem_size_mib=mem_size_mib,
            tmpdir=tmpdir,
        )
        # tar up the bundle
        bundle_path = f"{tmpdir}/{app_name}"
        shutil.make_archive(
            base_name=bundle_path,
            format="gztar",
            root_dir=tmpdir,
        )
        return f"{bundle_path}.tar.gz"

    def _create_image(self, image: Image, image_dir: str, fs_size_mib: int) -> None:
        self._create_dockerfile(
            image_dir=image_dir,
            image=image,
        )
        self._create_entrypoint(
            image_dir=image_dir,
            image=image,
            fs_size_mib=fs_size_mib,
        )
        self._create_start_script(
            image_dir=image_dir,
            image=image,
        )

    def _create_dockerfile(
        self,
        image_dir: str,
        image: Image,
    ) -> None:
        with open(f"{image_dir}/Dockerfile.j2") as f:
            template = Template(f.read()).render(
                image=image.value,
            )
        with open(f"{image_dir}/Dockerfile", "w") as f:
            f.write(template)
        os.remove(f"{image_dir}/Dockerfile.j2")

    def _create_entrypoint(
        self, image_dir: str, fs_size_mib: int, image: Image
    ) -> None:
        _install = self._get_install_steps(image=image)
        _build = self._get_build_steps(image=image)
        with open(f"{image_dir}/entrypoint.j2") as f:
            template = Template(f.read()).render(
                install=_install,
                build=_build,
                fs_size_mib=fs_size_mib,
            )
        with open(f"{image_dir}/entrypoint", "w") as f:
            f.write(template)
        os.remove(f"{image_dir}/entrypoint.j2")

    def _get_install_steps(self, image: Image) -> str:
        with open(f"{DEFAULT_LANG_TEMPLATE_DIR}/{image.name}/install") as f:
            return f.read().strip()

    def _get_build_steps(self, image: Image) -> str:
        with open(f"{DEFAULT_LANG_TEMPLATE_DIR}/{image.name}/build") as f:
            return f.read().strip()

    def _create_start_script(self, image_dir: str, image: Image) -> None:
        _entrypoint = self._get_entrypoint(image=image)
        with open(f"{image_dir}/start.sh.j2") as f:
            template = Template(f.read()).render(
                image=image,
                entrypoint=_entrypoint,
            )
        with open(f"{image_dir}/start.sh", "w") as f:
            f.write(template)
        os.remove(f"{image_dir}/start.sh.j2")

    def _get_entrypoint(self, image: Image) -> str:
        with open(f"{DEFAULT_LANG_TEMPLATE_DIR}/{image.name}/entrypoint") as f:
            return f.read().strip()

    def _create_run_app(
        self, app_name: str, vcpu_count: int, mem_size_mib: int, tmpdir: str
    ) -> None:
        with open(DEFAULT_RUN_APP_TEMPLATE_FILEPATH) as f:
            template = Template(f.read()).render(
                app_name=app_name,
                vcpu_count=vcpu_count,
                mem_size_mib=mem_size_mib,
            )
        with open(f"{tmpdir}/{app_name}_run_app.sh", "w") as f:
            f.write(template)

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
