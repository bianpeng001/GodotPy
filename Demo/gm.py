from game.game_mgr import game_mgr

main_camera = game_mgr.camera_mgr.main_camera
dust = main_camera.find_node('/root/MainScene/Dust01')
print(dust)


