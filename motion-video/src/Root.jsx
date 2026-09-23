import { Composition } from 'remotion';
import { CuracoReel } from './CuracoReel';

export const RemotionRoot = () => {
    return (
        <>
            <Composition
                id="CuracoReel"
                component={CuracoReel}
                durationInFrames={300} // 10 segundos a 30 fps
                fps={30}
                width={1080}
                height={1920} // Formato Vertical Reel / TikTok / Shorts (9:16)
            />
            <Composition
                id="CuracoHorizontal"
                component={CuracoReel}
                durationInFrames={300}
                fps={30}
                width={1920}
                height={1080} // Formato Horizontal YouTube / X (16:9)
            />
        </>
    );
};
