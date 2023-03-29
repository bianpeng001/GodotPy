from game.game_mgr import *

main_camera = game_mgr.camera_mgr.main_camera
#dust = main_camera.find_node('/root/MainScene/Dust01')
#print(dust)

#game_mgr.enable_city_ai = True
ui_mgr = game_mgr.ui_mgr
#print(ui_mgr.build_panel_controller.is_visible)

#game_mgr.ui_mgr.story_panel_controller.play_story(['请主公指示'])
# game_mgr.ui_mgr.story_panel_controller.play_story([
#     '滚滚长江东逝水，浪花淘尽英雄。',
#     '是非成败转头空。',
#     '青山依旧在，几度夕阳红。',
#     '白发渔樵江渚上，惯看秋月春风。',
#     '一壶浊酒喜相逢。',
#     '古今多少事，都付笑谈中。',
# ])

# game_mgr.ui_mgr.story_panel_controller.play_story(
#     game_mgr.config_mgr.story.start_game_story)


import imp

#import game.game_data
#imp.reload(game.game_data)


