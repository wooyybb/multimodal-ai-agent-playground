def default_conditioning_package(notes=None):
    return {
        "enabled": False,
        "reference_image_path": "",
        "conditioned_reference_path": "",
        "conditioned_reference": "",
        "conditioning_info": {},
        "conditioning_type": "none",
        "identity_strength": 0.0,
        "style_strength": 0.0,
        "structure_strength": 0.0,
        "preserve": {
            "hair": True,
            "eye_color": True,
            "outfit": True,
            "accessories": True,
            "silhouette": True,
        },
        "notes": list(notes or []),
    }
