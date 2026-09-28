def build_comic_layout(story, image_paths):
    if len(story) != len(image_paths):
        raise ValueError("Every story panel must have a matching image.")
    return [
        {
            "panel_number": panel.get("panel_number", i),
            "title": panel.get("title", f"Panel {i}"),
            "image_path": image_path,
            "scene_description": panel.get("scene_description", ""),
            "caption": panel.get("caption", ""),
            "narration": panel.get("narration", ""),
            "dialogue": panel.get("dialogue", ""),
            "image_prompt": panel.get("image_prompt", ""),
        }
        for i, (panel, image_path) in enumerate(zip(story, image_paths), 1)
    ]
