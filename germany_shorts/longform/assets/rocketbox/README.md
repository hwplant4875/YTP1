# Rocketbox avatars (MIT)

These come from the Microsoft Rocketbox Avatar Library, https://github.com/microsoft/Microsoft-Rocketbox. It has been
under the MIT licence since Nov 2020 (see `LICENSE_Rocketbox_MIT.md`), which allows commercial use, modification and
redistribution, YouTube included. Credit is optional, but if you give it: "Characters: Microsoft Rocketbox Avatar Library (MIT)".

`Male_Adult_03/`
* `Male_Adult_03_facial.fbx`: the original "_facial" export (hipoly, 81 bones, 175 blendshapes: 52 ARKit, FACS AUs, 15 visemes).
* Textures were converted from the 2048 px TGAs in `Assets/Avatars/Adults/Male_Adult_03/Textures/`:
  colour maps to 2048 JPG; normal maps to 1024 JPG; specular maps inverted to `*_rough.jpg` (1024); opacity (hair, lashes) to 1024 RGBA PNG.

To add another avatar, fetch `Assets/Avatars/<Group>/<Name>/Export/<Name>_facial.fbx` and its `Textures/<mNNN>_*.tga`
from raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/master/ (the texture prefix is named inside the FBX), then convert the same way.
Also included: Male_Adult_05 (m009), Male_Adult_08 (m014), Female_Adult_01 (f001), fetched with `tools/fetch_rocketbox.sh`.
Other avatars checked: Adults/Male_Adult_01..14, Professions/Business_Male_01..03 and Police_Male_01 all have `_facial` exports.
