import asyncio
from maim_message import Router, RouteConfig, TargetConfig

from .config import global_config
from .logger import logger, custom_logger
from .send_handler.main_send_handler import send_handler

route_config = RouteConfig(
    route_config={
        global_config.maibot_server.platform_name: TargetConfig(
            url=f"ws://{global_config.maibot_server.host}:{global_config.maibot_server.port}/ws",
            token=None,
        )
    }
)
router = Router(route_config, custom_logger)


async def mmc_start_com():
    logger.info("正在连接MaiBot")
    router.register_class_handler(send_handler.handle_message)
    await router.run()


async def mmc_stop_com():
    try:
        await router.stop()
    except asyncio.CancelledError:
        # 优雅关停时的取消信号，吞掉避免向上冒泡
        pass
    except Exception as e:
        logger.debug(f"router.stop 在关停过程中抛出异常: {e}")
