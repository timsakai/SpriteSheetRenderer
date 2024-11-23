bl_info = {
    "name": "Custom Action Renderer",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Panel",
    "description": "Allows rendering of individual actions with custom settings",
    "warning": "",
    "wiki_url": "",
    "category": "Rendering",
}

import bpy
import subprocess
import os
from pathlib import Path

# 結合スクリプトの名前
COMBINE_SCRIPT_NAME = "combine_images.py"

def get_combine_script_path():
    # アドオンのファイルパスを取得し、結合スクリプトのパスを生成
    addon_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(addon_dir, "SpriteSheetRenderer", COMBINE_SCRIPT_NAME)

# レンダリングされた画像のファイルパスを保存するリスト
rendered_images = []

output_path = ''  # 出力先のディレクトリを設定


# カスタムプロパティを持つクラス
class ActionPropertyGroup(bpy.types.PropertyGroup):
    # 各アクションの出力をトグルするためのブール値
    render_action: bpy.props.BoolProperty(name="Render", default=False)

def update_action_properties(scene):
    existing_actions = set(p.name for p in scene.custom_action_props)
    for action in bpy.data.actions:
        if action.name not in existing_actions:
            item = scene.custom_action_props.add()
            item.name = action.name

def load_handler(dummy):
    update_action_properties(bpy.context.scene)

# ハンドラ関数
def scene_update_post_handler(scene):
    update_action_properties(scene)

# パネルクラスの定義
class RENDER_PT_CustomPanel(bpy.types.Panel):
    bl_label = "Custom Action Renderer"
    bl_idname = "RENDER_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # ファイルパスの設定欄を追加
        layout.prop(scene, "render_output_path", text="Output Path")
        
        # アクションごとにチェックボックスを表示
        for action in bpy.data.actions:
            row = layout.row()
            prop = scene.custom_action_props[action.name]
            row.prop(prop, "render_action", text=action.name)

        # レンダリング実行のためのボタン
        layout.operator("render.custom_action")

# オペレータクラスの定義
class RENDER_OT_CustomAction(bpy.types.Operator):
    bl_idname = "render.custom_action"
    bl_label = "Render Actions"

    def execute(self, context):
        scene = context.scene
        for index,action in enumerate(bpy.data.actions):
            if scene.custom_action_props[action.name].render_action:
                # アクションを適用してレンダリング（サンプルコード）
                print(f"Rendering: {action.name}")
                # 全てのアクションをループ処理
                # アクション名をファイル名として使用
                scene.render.filepath = f'{scene.render_output_path}/{action.name}'
                output_path = bpy.path.abspath(scene.render_output_path)
                # ここでアクションをオブジェクトに設定する処理を行う
                # 例えば、特定のアーマチュアやオブジェクトに対してアクションを設定
                bpy.context.object.animation_data.action = action
                
                # アクションのキーフレーム範囲を取得
                frame_start, frame_end = action.frame_range
    
                # レンダリング範囲を設定
                scene.frame_start = int(frame_start)
                scene.frame_end = int(frame_end)

                # レンダリングを実行
                bpy.ops.render.render(animation=True, write_still=True)
                
                filepath = bpy.path.abspath(scene.render_output_path)
                filepath = os.path.join(filepath,action.name)
                rendered_images = []
                for num in range(scene.frame_start,scene.frame_end):
                    # レンダリングされた画像のパスをリストに追加
                    rendered_images.append(filepath + f'{num:04d}.png' )
                    
                # レンダリング終了後、結合スクリプトを実行
                subprocess.run(['python', get_combine_script_path(), *rendered_images, os.path.join(output_path, f'{action.name}.png')])
                

        return {'FINISHED'}

# アドオンを有効化するための登録関数
def register():
    bpy.utils.register_class(ActionPropertyGroup)
    bpy.utils.register_class(RENDER_PT_CustomPanel)
    bpy.utils.register_class(RENDER_OT_CustomAction)
    bpy.types.Scene.custom_action_props = bpy.props.CollectionProperty(type=ActionPropertyGroup)
    bpy.types.Scene.render_output_path = bpy.props.StringProperty(
        name="Render Output Path",
        default="",
        subtype='DIR_PATH'
    )
    bpy.app.handlers.depsgraph_update_post.append(scene_update_post_handler)
    bpy.app.handlers.load_post.append(load_handler)
    
def unregister():
    bpy.utils.unregister_class(ActionPropertyGroup)
    bpy.utils.unregister_class(RENDER_PT_CustomPanel)
    bpy.utils.unregister_class(RENDER_OT_CustomAction)
    del bpy.types.Scene.custom_action_props
    del bpy.types.Scene.render_output_path
    bpy.app.handlers.depsgraph_update_post.remove(scene_update_post_handler)
    bpy.app.handlers.load_post.remove(load_handler)


if __name__ == "__main__":
    register()