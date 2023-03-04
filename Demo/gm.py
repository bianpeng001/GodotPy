from game.game_mgr import *

main_camera = game_mgr.camera_mgr.main_camera
#dust = main_camera.find_node('/root/MainScene/Dust01')
#print(dust)

ui_mgr = game_mgr.ui_mgr

print(ui_mgr.build_panel_controller.is_visible)

