import { loadFont } from "@remotion/fonts";
import { Composition, staticFile } from "remotion";
import { Giant } from "./Giant";
import { DURATION, FPS, H, W } from "./timeline";

loadFont({ family: "Pretendard", url: staticFile("Pretendard-ExtraBold.otf"), weight: "800" });

export const MyComposition = () => {
  return (
    <Composition id="Giant" component={Giant} durationInFrames={DURATION} fps={FPS} width={W} height={H} />
  );
};
