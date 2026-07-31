import { Config } from "@remotion/cli/config";

// overlay de título com fundo transparente:
// imagem PNG (carrega alpha) + ProRes 4444 preserva alpha no render de vídeo.
Config.setVideoImageFormat("png");
Config.setPixelFormat("yuva444p10le");
Config.setCodec("prores");
Config.setProResProfile("4444");
Config.setOverwriteOutput(true);
