from hotbox.utils import _set_templates_home

NAME = "hotbox"
DESC = "🚀 Run your code 📦 on Firecracker MicroVMs 🔥 in the cloud ☁️"
API_V0 = "/api/v0"
SERVER_MODULE_NAME = "hotbox.api:api"

TEMPLATES_HOME = _set_templates_home()
DEFAULT_IMAGE_TEMPLATE_DIR = f"{TEMPLATES_HOME}/image"
DEFAULT_LANG_TEMPLATE_DIR = f"{TEMPLATES_HOME}/lang"
DEFAULT_RUN_APP_TEMPLATE_FILEPATH = f"{TEMPLATES_HOME}/run_app.sh.j2"
DEFAULT_USERDATA_TEMPLATE_FILEPATH = f"{TEMPLATES_HOME}/ec2_userdata.sh.j2"
