bl_info = {
    "name": "SpriteSheetRenderer",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Panel",
    "description": "Allows rendering of individual actions with custom settings.And packing images for SpriteSheet",
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

import sys
import importlib.util

# モジュールのインストールを確認する関数
def is_module_installed(module_name):
    return importlib.util.find_spec(module_name) is not None

# モジュールをインストールする関数
def install_module(module_name):
    if is_module_installed("PIL") :
        print("Pillow is alady installed")
    else :
        print("Pillow is not alady installed")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
        return f"Successfully installed {module_name}"
    except Exception as e:
        return f"Failed to install {module_name}: {e}"

def get_combine_script_path():
    # アドオンのファイルパスを取得し、結合スクリプトのパスを生成
    addon_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(addon_dir, "", COMBINE_SCRIPT_NAME)

# レンダリングされた画像のファイルパスを保存するリスト
rendered_images = []

output_path = ''  # 出力先のディレクトリを設定

# オペレーター
class PIP_OT_InstallPillow(bpy.types.Operator):
    bl_idname = "pip.install_pillow"
    bl_label = "Install Pillow"
    bl_description = "Install the Pillow Python module using pip"
    
    def execute(self, context):
        module_name = "Pillow"  # 固定されたモジュール名
        result = install_module(module_name)
        self.report({'INFO'}, result)
        return {'FINISHED'}

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
    bl_label = "SpriteSheetRenderer"
    bl_idname = "RENDER_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Pillowがインストールされているか確認
        if is_module_installed("PIL"):
            layout.label(text="Pillow is already installed.")
        else:
            layout.label(text="Install Pillow Module")
            layout.operator("pip.install_pillow", text="Install Pillow")
        
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
                # アクションを適用してレンダリング
                print(f"Rendering: {action.name}")
                # 全てのアクションをループ処理
                # アクション名をファイル名として使用
                scene.render.filepath = f'{scene.render_output_path}/{action.name}/{action.name}'
                output_path = bpy.path.abspath(scene.render_output_path)
                # ここでアクションをオブジェクトに設定する処理を行う
                bpy.context.object.animation_data.action = action
                
                # アクションのキーフレーム範囲を取得
                frame_start, frame_end = action.frame_range
    
                # レンダリング範囲を設定
                scene.frame_start = int(frame_start)
                scene.frame_end = int(frame_end)

                # レンダリングを実行
                bpy.ops.render.render(animation=True, write_still=True)
                
                filepath = bpy.path.abspath(scene.render_output_path)
                rendered_images = []
                for num in range(scene.frame_start,scene.frame_end):
                    # ファイルが存在するなら(stepへの対応)
                    image = filepath + f'/{action.name}/{action.name}' + f'{num:04d}.png'
                    if os.path.isfile(image) :
                        # レンダリングされた画像のパスをリストに追加
                        rendered_images.append(image)
                    
                # レンダリング終了後、結合スクリプトを実行
                subprocess.run(['python', get_combine_script_path(), *rendered_images, os.path.join(output_path, f'{action.name}.png')])
                

        return {'FINISHED'}

# アドオンを有効化するための登録関数
def register():
    bpy.utils.register_class(ActionPropertyGroup)
    bpy.utils.register_class(RENDER_PT_CustomPanel)
    bpy.utils.register_class(RENDER_OT_CustomAction)
    bpy.utils.register_class(PIP_OT_InstallPillow)
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
    bpy.utils.unregister_class(PIP_OT_InstallPillow)
    bpy.utils.unregister_class(RENDER_OT_CustomAction)
    del bpy.types.Scene.custom_action_props
    del bpy.types.Scene.render_output_path
    bpy.app.handlers.depsgraph_update_post.remove(scene_update_post_handler)
    bpy.app.handlers.load_post.remove(load_handler)


if __name__ == "__main__":
    register()